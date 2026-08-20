import logging
import os
import re
from typing import List

from schemas import CandidateResume

logging.basicConfig(level=logging.INFO)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")


def _call_ollama(prompt: str) -> str | None:
    try:
        import requests

        chat_payload = {
            "model": OLLAMA_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"temperature": 0.2, "num_predict": 256},
        }
        response = requests.post(f"{OLLAMA_URL}/api/chat", json=chat_payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        message = data.get("message") or {}
        content = message.get("content")
        if content:
            return content

        # Fallback for older Ollama installs
        gen_payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2, "num_predict": 256},
        }
        gen_resp = requests.post(f"{OLLAMA_URL}/api/generate", json=gen_payload, timeout=120)
        gen_resp.raise_for_status()
        return gen_resp.json().get("response")
    except Exception as exc:
        logging.warning("Ollama request failed: %s", exc)
        return None


def _prompt_for_candidate(requirement: str, candidate: CandidateResume) -> str:
    return (
        "You are a hiring assistant. Evaluate the following candidate resume for the job requirement. "
        "Score the candidate from 0 to 100, where 100 means an excellent fit. "
        "Prefer candidates who match the required skills, experience, and positive emotional fit. "
        "Reply with a short score and one sentence of reasoning.\n\n"
        f"Job requirement:\n{requirement}\n\n"
        f"Candidate resume:\n{candidate.full_text}\n\n"
        "Answer format:\nScore: <number>\nReason: <short explanation>\n"
    )


def _parse_evaluation(text: str) -> tuple[float, str]:
    score = 0.0
    reason = text.strip().replace("\n", " ")
    match = re.search(r"score\s*[:=]\s*(\d{1,3})", text, re.IGNORECASE)
    if match:
        score = min(100.0, max(0.0, float(match.group(1))))
    elif "excellent" in text.lower():
        score = 90.0
    elif "good" in text.lower():
        score = 75.0
    elif "weak" in text.lower() or "poor" in text.lower():
        score = 35.0
    else:
        score = 60.0
    return score, reason


def _simple_heuristic(requirement: str, candidate: CandidateResume) -> tuple[float, str]:
    requirement_text = requirement.lower()
    candidate_text = candidate.full_text.lower()
    score = 50.0

    skills = [skill.strip() for skill in candidate.skills.split(",") if skill.strip()]
    skills_hit = sum(1 for skill in skills if skill.lower() in requirement_text)
    score += min(25.0, skills_hit * 8.0)

    experience_bonus = min(20.0, max(0.0, candidate.experience * 2.0))
    score += experience_bonus

    emotional_terms = ["leadership", "communication", "collaboration", "passionate", "motivated", "enthusiastic"]
    emotion_hits = sum(1 for term in emotional_terms if term in candidate_text)
    score += min(15.0, emotion_hits * 3.0)

    reason_parts = []
    if skills_hit:
        reason_parts.append(f"matched {skills_hit} requested skill(s)")
    reason_parts.append(f"{candidate.experience} years of experience")
    if emotion_hits:
        reason_parts.append("positive communication/emotion signals")

    reason = ", ".join(reason_parts) or "candidate text was scored by default heuristics"
    return min(100.0, score), reason


def evaluate_candidates(requirement: str, candidates: List[CandidateResume]) -> List[CandidateResume]:
    evaluated: List[CandidateResume] = []

    for candidate in candidates:
        score = 0.0
        reason = ""
        prompt = _prompt_for_candidate(requirement, candidate)

        if OLLAMA_URL:
            output = _call_ollama(prompt)
            if output:
                score, reason = _parse_evaluation(output)

        if score == 0.0 and reason == "":
            score, reason = _simple_heuristic(requirement, candidate)

        candidate.fit_score = score
        candidate.evaluation = reason
        evaluated.append(candidate)

    evaluated.sort(key=lambda c: (c.fit_score or 0.0), reverse=True)
    return evaluated


def evaluate_single_resume(requirement: str, candidate: CandidateResume) -> CandidateResume:
    """Evaluate one resume text against a job requirement using Ollama."""
    score = 0.0
    reason = ""
    prompt = _prompt_for_candidate(requirement, candidate)

    if OLLAMA_URL:
        output = _call_ollama(prompt)
        if output:
            score, reason = _parse_evaluation(output)

    if score == 0.0 and reason == "":
        score, reason = _simple_heuristic(requirement, candidate)

    candidate.fit_score = score
    candidate.evaluation = reason
    return candidate
