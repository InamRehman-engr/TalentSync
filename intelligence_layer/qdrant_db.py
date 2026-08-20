import os
from typing import Iterable, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

from embeddings import embed_text, embed_texts
from schemas import CandidateResume

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "resumes")

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)


def check_qdrant() -> bool:
    try:
        client.get_collections()
        return True
    except Exception:
        return False


def _ensure_collection(vector_size: int) -> None:
    try:
        client.get_collection(collection_name=COLLECTION_NAME)
    except Exception:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors=VectorParams(size=vector_size, distance=Distance.COSINE),
        )


class ResumeVectorStore:
    def __init__(self, collection_name: str = COLLECTION_NAME):
        self.collection_name = collection_name

    def upsert_candidates(self, resumes: Iterable[CandidateResume]) -> int:
        vectors = embed_texts([candidate.full_text for candidate in resumes])
        if not vectors:
            return 0
        _ensure_collection(len(vectors[0]))

        points = []
        for candidate, vector in zip(resumes, vectors):
            points.append(
                PointStruct(
                    id=str(candidate.id),
                    vector=vector,
                    payload={
                        "id": candidate.id,
                        "sync_key": candidate.sync_key,
                        "name": candidate.name,
                        "title": candidate.title,
                        "location": candidate.location,
                        "experience": candidate.experience,
                        "skills": candidate.skills,
                        "summary": candidate.summary,
                        "education": candidate.education,
                        "email": candidate.email,
                        "status": candidate.status,
                        "full_text": candidate.full_text,
                    },
                )
            )

        client.upsert(collection_name=self.collection_name, points=points)
        return len(points)

    def search_resumes(
        self,
        query_text: str,
        top_k: int = 10,
        min_experience: int = 0,
        max_experience: int = 99,
    ) -> List[CandidateResume]:
        query_vector = embed_text(query_text)
        hits = client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k * 3,
            with_payload=True,
        )

        candidates: List[CandidateResume] = []
        for hit in hits:
            payload = hit.payload or {}
            experience = int(payload.get("experience") or 0)
            if experience < min_experience or experience > max_experience:
                continue

            candidate = CandidateResume(
                id=int(payload.get("id") or 0),
                sync_key=payload.get("sync_key"),
                name=payload.get("name") or "",
                title=payload.get("title") or "",
                location=payload.get("location") or "",
                experience=experience,
                skills=payload.get("skills") or "",
                summary=payload.get("summary") or "",
                education=payload.get("education") or "",
                email=payload.get("email") or "",
                status=payload.get("status") or "available",
                full_text=payload.get("full_text") or "",
                vector_score=float(hit.score) if getattr(hit, "score", None) is not None else None,
            )
            candidates.append(candidate)
            if len(candidates) >= top_k:
                break

        return candidates
