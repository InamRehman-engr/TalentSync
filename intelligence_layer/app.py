import logging
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

from embeddings import embed_text
from parser import build_requirement_text, row_to_candidate_resume, build_job_requirement, resume_text_to_candidate
from qdrant_db import ResumeVectorStore, check_qdrant
from schemas import CandidateResume, RebuildResponse, SearchRequest, EvaluateResumeRequest, EvaluateResumeResponse
from evaluator import evaluate_candidates, evaluate_single_resume

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nhr:nhr_secret@localhost:5432/nhr")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
vector_store = ResumeVectorStore()


@app.route("/health", methods=["GET"])
def health():
    qdrant_ok = check_qdrant()
    return jsonify({
        "status": "ok",
        "database_url": DATABASE_URL,
        "qdrant_ok": qdrant_ok,
    }), 200


@app.route("/intelligence/rebuild", methods=["POST"])
def rebuild_index():
    try:
        with engine.begin() as conn:
            rows = conn.execute(text("SELECT * FROM candidates")).fetchall()
            candidates = [row_to_candidate_resume(dict(row._mapping)) for row in rows]
            imported = vector_store.upsert_candidates(candidates)
        response = RebuildResponse(imported=imported, collection_name=vector_store.collection_name)
        return jsonify(response.model_dump()), 200
    except SQLAlchemyError as exc:
        logging.exception("Failed to load candidates from database")
        return jsonify({"error": "Database load failed", "detail": str(exc)}), 500
    except Exception as exc:
        logging.exception("Failed to rebuild vector index")
        return jsonify({"error": "Vector index rebuild failed", "detail": str(exc)}), 500


@app.route("/intelligence/search", methods=["POST"])
def search_candidates():
    body = request.get_json(silent=True) or {}
    try:
        request_model = SearchRequest(**body)
    except Exception as exc:
        return jsonify({"error": "Invalid request", "detail": str(exc)}), 400

    query_text = build_requirement_text(
        request_model.query,
        request_model.skills,
        request_model.min_experience,
        request_model.max_experience,
    )

    try:
        candidates = vector_store.search_resumes(
            query_text,
            top_k=request_model.top_k,
            min_experience=request_model.min_experience,
            max_experience=request_model.max_experience,
        )
    except Exception as exc:
        logging.exception("Vector search failed")
        return jsonify({"error": "Vector search failed", "detail": str(exc)}), 500

    evaluated = evaluate_candidates(request_model.query, candidates)
    return jsonify({"query": request_model.query, "results": [candidate.model_dump() for candidate in evaluated]}), 200


@app.route("/intelligence/embed", methods=["POST"])
def embed_resume():
    body = request.get_json(silent=True) or {}
    text_value = body.get("text") or ""
    try:
        vector = embed_text(text_value)
        return jsonify({"embedding": vector}), 200
    except Exception as exc:
        logging.exception("Embedding failed")
        return jsonify({"error": "Embedding failed", "detail": str(exc)}), 500


@app.route("/intelligence/evaluate-resume", methods=["POST"])
def evaluate_resume():
    body = request.get_json(silent=True) or {}
    try:
        request_model = EvaluateResumeRequest(**body)
    except Exception as exc:
        return jsonify({"error": "Invalid request", "detail": str(exc)}), 400

    requirement = build_job_requirement(
        job_title=request_model.job_title,
        job_skills=request_model.job_skills,
        job_description=request_model.job_description,
        job_experience=request_model.job_experience,
    )
    candidate = resume_text_to_candidate(
        request_model.resume_text,
        candidate_name=request_model.candidate_name,
        location=request_model.location,
        skills=request_model.skills,
    )

    try:
        result = evaluate_single_resume(requirement, candidate)
        response = EvaluateResumeResponse(
            fit_score=float(result.fit_score or 0),
            evaluation=result.evaluation or "",
        )
        return jsonify(response.model_dump()), 200
    except Exception as exc:
        logging.exception("Resume evaluation failed")
        return jsonify({"error": "Resume evaluation failed", "detail": str(exc)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5010"))
    app.run(host="0.0.0.0", port=port)
