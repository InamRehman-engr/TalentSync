"""ATS-style resume scoring against a job posting."""


def compute_ats_score(resume_text: str, job: dict) -> tuple[int, dict]:
    job_skills = [s.strip().lower() for s in (job.get("skills") or "").split(",") if s.strip()]
    resume_lower = (resume_text or "").lower()
    job_title_words = [w for w in (job.get("title") or "").lower().split() if len(w) > 2]

    skill_matches = sum(1 for s in job_skills if s in resume_lower)
    title_matches = sum(1 for w in job_title_words if w in resume_lower)

    skill_score = (skill_matches / max(len(job_skills), 1)) * 50
    title_score = (title_matches / max(len(job_title_words), 1)) * 20
    length_score = min(len(resume_text) / 500, 1) * 15
    keyword_bonus = (
        15
        if any(w in resume_lower for w in ["experience", "project", "developed", "built", "managed", "led"])
        else 5
    )
    ats_score = min(round(skill_score + title_score + length_score + keyword_bonus), 100)

    breakdown = {
        "skill_match": round(skill_score),
        "title_relevance": round(title_score),
        "resume_quality": round(length_score),
        "keyword_strength": round(keyword_bonus),
        "matched_skills": [s for s in job_skills if s in resume_lower],
        "missing_skills": [s for s in job_skills if s not in resume_lower],
    }
    return ats_score, breakdown
