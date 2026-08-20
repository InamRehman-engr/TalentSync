"""Proxy resume evaluation to the intelligence layer (Ollama)."""

from __future__ import annotations

import logging
import os

import requests

log = logging.getLogger(__name__)

INTELLIGENCE_URL = os.getenv("INTELLIGENCE_URL", "http://localhost:5010")


def evaluate_resume_with_ai(
    resume_text: str,
    *,
    candidate_name: str = "",
    location: str = "",
    skills: str = "",
    job: dict | None = None,
) -> dict:
    """
    Call intelligence layer for AI fit scoring.
    Returns {fit_score, evaluation, ai_available}.
    """
    payload = {
        "resume_text": resume_text,
        "candidate_name": candidate_name,
        "location": location,
        "skills": skills,
        "job_title": (job or {}).get("title", ""),
        "job_skills": (job or {}).get("skills", ""),
        "job_description": (job or {}).get("description", ""),
        "job_experience": (job or {}).get("experience", ""),
    }

    try:
        response = requests.post(
            f"{INTELLIGENCE_URL}/intelligence/evaluate-resume",
            json=payload,
            timeout=180,
        )
        response.raise_for_status()
        data = response.json()
        return {
            "fit_score": int(round(float(data.get("fit_score", 0)))),
            "evaluation": data.get("evaluation", ""),
            "ai_available": True,
        }
    except Exception as exc:
        log.warning("AI resume evaluation failed: %s", exc)
        return {
            "fit_score": 0,
            "evaluation": "AI evaluation unavailable. Check that the intelligence service and Ollama are running.",
            "ai_available": False,
        }
