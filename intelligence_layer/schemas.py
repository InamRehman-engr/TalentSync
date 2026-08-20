from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class CandidateResume(BaseModel):
    id: int
    sync_key: Optional[str] = None
    name: str
    title: str
    location: str = ""
    experience: int = 0
    skills: str = ""
    summary: str = ""
    education: str = ""
    email: str = ""
    status: str = "available"
    full_text: str
    vector_score: Optional[float] = None
    fit_score: Optional[float] = None
    evaluation: Optional[str] = None


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    skills: Optional[str] = None
    min_experience: int = 0
    max_experience: int = 99
    top_k: int = 10


class SearchResponse(BaseModel):
    query: str
    results: List[CandidateResume]


class RebuildResponse(BaseModel):
    imported: int
    collection_name: str


class EvaluateResumeRequest(BaseModel):
    resume_text: str = Field(..., min_length=30)
    candidate_name: str = ""
    location: str = ""
    skills: str = ""
    job_title: str = ""
    job_skills: str = ""
    job_description: str = ""
    job_experience: str = ""


class EvaluateResumeResponse(BaseModel):
    fit_score: float
    evaluation: str
    model: str = "ollama"
