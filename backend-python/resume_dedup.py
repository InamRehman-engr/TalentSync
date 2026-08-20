"""Resume deduplication: normalize text, exact hash match, embedding similarity."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
from dataclasses import dataclass
from typing import Any

import numpy as np
import requests
from sqlalchemy import text

log = logging.getLogger(__name__)

INTELLIGENCE_URL = os.getenv("INTELLIGENCE_URL", "http://localhost:5010")
SIMILARITY_THRESHOLD = float(os.getenv("RESUME_SIMILARITY_THRESHOLD", "0.95"))


def normalize_resume_text(raw: str) -> str:
    """Canonical form for hashing and embedding comparison."""
    text_value = (raw or "").replace("\r\n", "\n").replace("\r", "\n")
    text_value = text_value.lower()
    text_value = re.sub(r"[^\w\s]", " ", text_value)
    text_value = re.sub(r"\s+", " ", text_value).strip()
    return text_value


def resume_content_hash(employer_email: str, resume_text: str) -> str:
    """SHA-256 of normalized resume content, scoped per employer."""
    email = employer_email.strip().lower()
    normalized = normalize_resume_text(resume_text)
    payload = f"{email}\0{normalized}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def embed_resume_text(resume_text: str) -> list[float] | None:
    """Generate an embedding vector via the intelligence layer."""
    normalized = normalize_resume_text(resume_text)
    if not normalized:
        return None
    try:
        response = requests.post(
            f"{INTELLIGENCE_URL}/intelligence/embed",
            json={"text": normalized},
            timeout=120,
        )
        response.raise_for_status()
        vector = response.json().get("embedding")
        if not vector:
            return None
        return [float(v) for v in vector]
    except Exception as exc:
        log.warning("Resume embedding failed: %s", exc)
        return None


def cosine_similarity(a: list[float], b: list[float]) -> float:
    va = np.asarray(a, dtype=float)
    vb = np.asarray(b, dtype=float)
    denom = float(np.linalg.norm(va) * np.linalg.norm(vb))
    if denom == 0.0:
        return 0.0
    return float(np.dot(va, vb) / denom)


def embedding_to_json(vector: list[float] | None) -> str:
    return json.dumps(vector) if vector else ""


def embedding_from_json(raw: str | None) -> list[float] | None:
    if not raw:
        return None
    try:
        data = json.loads(raw)
        if isinstance(data, list) and data:
            return [float(v) for v in data]
    except (TypeError, ValueError, json.JSONDecodeError):
        return None
    return None


@dataclass
class ResumeDedupResult:
    ok: bool
    reason: str = ""
    dedup_hash: str = ""
    normalized_text: str = ""
    embedding: list[float] | None = None
    existing_resume: dict[str, Any] | None = None
    similarity: float | None = None

    def to_error_payload(self) -> dict[str, Any]:
        message = self.reason
        if ": " in message:
            message = message.split(": ", 1)[1]
        payload: dict[str, Any] = {
            "error": message,
            "dedup_stage": "exact" if self.reason.startswith("exact") else "similarity",
        }
        if self.existing_resume:
            payload["resume"] = {
                "id": self.existing_resume.get("id"),
                "candidate_name": self.existing_resume.get("candidate_name") or "",
                "source_filename": self.existing_resume.get("source_filename") or "",
                "uploaded_date": self.existing_resume.get("uploaded_date") or "",
            }
        if self.similarity is not None:
            payload["similarity"] = round(self.similarity, 4)
            payload["threshold"] = SIMILARITY_THRESHOLD
        return payload


def dedup_user_message(reason: str) -> str:
    if ": " in reason:
        return reason.split(": ", 1)[1]
    return reason


def format_bulk_item_error(label: str, reason: str) -> str:
    return f"{label}: {dedup_user_message(reason)}"


def _row_to_dict(row) -> dict[str, Any]:
    return dict(row._mapping)


def _find_resume_by_hash(conn, employer_email: str, dedup_hash: str) -> dict[str, Any] | None:
    row = conn.execute(
        text(
            """
            SELECT * FROM resume_uploads
            WHERE employer_email = :email AND dedup_hash = :dedup_hash
            LIMIT 1
            """
        ),
        {"email": employer_email, "dedup_hash": dedup_hash},
    ).fetchone()
    return _row_to_dict(row) if row else None


def _list_employer_resumes(
    conn,
    employer_email: str,
    *,
    exclude_resume_id: int | None = None,
) -> list[dict[str, Any]]:
    rows = conn.execute(
        text(
            """
            SELECT id, candidate_name, source_filename, uploaded_date,
                   resume_text, dedup_hash, embedding
            FROM resume_uploads
            WHERE employer_email = :email
            ORDER BY id ASC
            """
        ),
        {"email": employer_email},
    ).fetchall()
    resumes = [_row_to_dict(row) for row in rows]
    if exclude_resume_id is not None:
        resumes = [row for row in resumes if int(row["id"]) != int(exclude_resume_id)]
    return resumes


def find_similar_resume(
    conn,
    employer_email: str,
    resume_text: str,
    query_embedding: list[float],
    *,
    exclude_resume_id: int | None = None,
) -> tuple[dict[str, Any] | None, float]:
    """Return (matching_row, similarity) when similarity exceeds threshold."""
    best_row: dict[str, Any] | None = None
    best_score = 0.0

    for row in _list_employer_resumes(conn, employer_email, exclude_resume_id=exclude_resume_id):
        stored = embedding_from_json(row.get("embedding"))
        if stored is None:
            stored = embed_resume_text(row.get("resume_text") or "")
        if not stored:
            continue
        score = cosine_similarity(query_embedding, stored)
        if score > best_score:
            best_score = score
            best_row = row

    if best_row and best_score >= SIMILARITY_THRESHOLD:
        return best_row, best_score
    return None, best_score


def run_resume_dedup_pipeline(
    conn,
    employer_email: str,
    resume_text: str,
    *,
    exclude_resume_id: int | None = None,
    pending_embeddings: list[list[float]] | None = None,
    pending_hashes: set[str] | None = None,
) -> ResumeDedupResult:
    """
    Upload pipeline:
      extract (caller) -> normalize -> SHA-256 -> duplicate reject
      -> embed -> similarity (>threshold) reject -> ok to save
    """
    normalized = normalize_resume_text(resume_text)
    if len(normalized) < 30:
        return ResumeDedupResult(
            ok=False,
            reason="Resume text is too short after normalization",
            normalized_text=normalized,
        )

    dedup_hash = resume_content_hash(employer_email, resume_text)
    if pending_hashes and dedup_hash in pending_hashes:
        return ResumeDedupResult(
            ok=False,
            reason="exact_duplicate: This resume is a duplicate of another file in this upload batch",
            dedup_hash=dedup_hash,
            normalized_text=normalized,
        )

    exact = _find_resume_by_hash(conn, employer_email, dedup_hash)
    if exact and (exclude_resume_id is None or int(exact["id"]) != int(exclude_resume_id)):
        return ResumeDedupResult(
            ok=False,
            reason="exact_duplicate: This resume already exists in your library",
            dedup_hash=dedup_hash,
            normalized_text=normalized,
            existing_resume=exact,
        )

    embedding = embed_resume_text(resume_text)
    if embedding:
        if pending_embeddings:
            for pending in pending_embeddings:
                score = cosine_similarity(embedding, pending)
                if score >= SIMILARITY_THRESHOLD:
                    return ResumeDedupResult(
                        ok=False,
                        reason="similar_duplicate: This resume is nearly identical to another upload in this batch",
                        dedup_hash=dedup_hash,
                        normalized_text=normalized,
                        embedding=embedding,
                        similarity=score,
                    )

        similar, score = find_similar_resume(
            conn,
            employer_email,
            resume_text,
            embedding,
            exclude_resume_id=exclude_resume_id,
        )
        if similar:
            return ResumeDedupResult(
                ok=False,
                reason="similar_duplicate: This resume closely matches one already in your library",
                dedup_hash=dedup_hash,
                normalized_text=normalized,
                embedding=embedding,
                existing_resume=similar,
                similarity=score,
            )

    return ResumeDedupResult(
        ok=True,
        dedup_hash=dedup_hash,
        normalized_text=normalized,
        embedding=embedding,
    )
