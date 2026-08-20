from typing import Optional

from schemas import CandidateResume


def candidate_resume_text(candidate: CandidateResume) -> str:
    parts = [
        f"Name: {candidate.name}",
        f"Title: {candidate.title}",
        f"Location: {candidate.location}",
        f"Experience: {candidate.experience} years",
        f"Skills: {candidate.skills}",
        f"Summary: {candidate.summary}",
        f"Education: {candidate.education}",
        f"Email: {candidate.email}",
        f"Status: {candidate.status}",
    ]
    return "\n".join(part for part in parts if part and ": " in part)


def row_to_candidate_resume(row: dict) -> CandidateResume:
    candidate = CandidateResume(
        id=int(row.get("id") or 0),
        sync_key=row.get("sync_key"),
        name=row.get("name") or "",
        title=row.get("title") or "",
        location=row.get("location") or "",
        experience=int(row.get("experience") or 0),
        skills=row.get("skills") or "",
        summary=row.get("summary") or "",
        education=row.get("education") or "",
        email=row.get("email") or "",
        status=row.get("status") or "available",
        full_text="",
    )
    candidate.full_text = candidate_resume_text(candidate)
    return candidate


def build_requirement_text(query: str, skills: Optional[str], min_experience: int, max_experience: int) -> str:
    pieces = [query.strip()] if query else []
    if skills:
        pieces.append(f"Required skills: {skills}")
    pieces.append(f"Desired experience range: {min_experience} to {max_experience} years")
    return "\n".join(part for part in pieces if part)


def build_job_requirement(
    *,
    job_title: str = "",
    job_skills: str = "",
    job_description: str = "",
    job_experience: str = "",
) -> str:
    pieces = []
    if job_title:
        pieces.append(f"Role: {job_title}")
    if job_skills:
        pieces.append(f"Required skills: {job_skills}")
    if job_experience:
        pieces.append(f"Experience: {job_experience}")
    if job_description:
        pieces.append(f"Description: {job_description}")
    if not pieces:
        return (
            "General professional role. Assess overall candidate quality, relevant skills, "
            "experience depth, and communication based on the resume."
        )
    return "\n".join(pieces)


def resume_text_to_candidate(
    resume_text: str,
    *,
    candidate_name: str = "",
    location: str = "",
    skills: str = "",
) -> CandidateResume:
    candidate = CandidateResume(
        id=0,
        name=candidate_name or "Candidate",
        title="Applicant",
        location=location,
        experience=0,
        skills=skills,
        summary=resume_text[:400],
        education="",
        email="",
        status="available",
        full_text=resume_text,
    )
    return candidate
