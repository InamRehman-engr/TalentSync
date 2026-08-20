import os
import secrets
import re
import logging
from datetime import datetime
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import text
from database import (
    engine, users, candidates, jobs, applications, sessions, resume_uploads,
    init_schema,
)
from db_sync import run_sync
from github_search import search_github_users, GitHubSearchError
from resume_parser import parse_resume_upload
from resume_dedup import run_resume_dedup_pipeline, embedding_to_json, format_bulk_item_error, dedup_user_message
from ats_scoring import compute_ats_score
from resume_evaluator import evaluate_resume_with_ai

INTELLIGENCE_URL = os.getenv("INTELLIGENCE_URL", "http://localhost:5010")
GITHUB_PAT = os.getenv("GITHUB_PAT", "")

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024


# ─── DATABASE HELPERS ────────────────────────────────────────────────────────────

def get_db():
    """Return a SQLAlchemy transactional connection context manager.
    Usage: with get_db() as conn: ...
    Auto-commits on success, rolls back on exception.
    """
    return engine.begin()


def init_db():
    init_schema()
    run_sync()


def get_session(req):
    token = req.headers.get("Authorization", "").replace("Bearer ", "").strip()
    if not token:
        return None
    with get_db() as conn:
        row = conn.execute(
            text("SELECT * FROM sessions WHERE token=:token"), {"token": token}
        ).fetchone()
        return dict(row._mapping) if row else None


def _tenant_key_from_company(company: str, fallback: str = "") -> str:
    base = (company or "").strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    if slug:
        return slug[:80]
    if fallback and "@" in fallback:
        return re.sub(r"[^a-z0-9]+", "-", fallback.split("@", 1)[0].lower()).strip("-")[:80]
    return "default-tenant"


def _breakdown_from_ats(ats_score: int) -> dict:
    ats = max(0, min(int(ats_score or 0), 100))
    skill_part = round(ats * 0.5)
    title_part = round(ats * 0.2)
    resume_part = round(ats * 0.15)
    keyword_part = ats - skill_part - title_part - resume_part
    return {
        "skill_match": skill_part,
        "title_relevance": title_part,
        "resume_quality": resume_part,
        "keyword_strength": keyword_part,
    }


# ─── AUTH ────────────────────────────────────────────────────────────────────────

@app.route("/api/auth/login", methods=["POST"])
def login():
    body = request.get_json(silent=True) or {}
    email = (body.get("email") or "").strip().lower()
    password = body.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    with get_db() as conn:
        row = conn.execute(
            text("SELECT * FROM users WHERE LOWER(email)=:email"), {"email": email}
        ).fetchone()
        user = dict(row._mapping) if row else None

        if not user or user["password"] != password:
            return jsonify({"error": "Invalid email or password"}), 401

        token = secrets.token_hex(32)
        conn.execute(
            sessions.insert().values(
                token=token, email=user["email"], role=user["role"],
                name=user["name"], company=user["company"] or "",
                title=user["title"] or "",
            )
        )

    return jsonify({
        "token": token,
        "user": {
            "email": user["email"],
            "role": user["role"],
            "name": user["name"],
            "company": user["company"] or "",
            "title": user["title"] or "",
        },
    })


@app.route("/api/auth/register", methods=["POST"])
def register():
    body = request.get_json(silent=True) or {}
    email = (body.get("email") or "").strip().lower()
    password = body.get("password") or ""
    role = body.get("role") or ""
    name = body.get("name") or ""
    company = body.get("company") or ""
    title = body.get("title") or ""

    if not email or not password or role not in ("employer", "employee") or not name:
        return jsonify({"error": "name, email, password, and role (employer/employee) are required"}), 400

    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return jsonify({"error": "Invalid email format"}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    with get_db() as conn:
        existing = conn.execute(
            text("SELECT email FROM users WHERE LOWER(email)=:email"), {"email": email}
        ).fetchone()
        if existing:
            return jsonify({
                "error": "An account with this email already exists. Sign in or reset your password.",
                "code": "email_exists",
            }), 409

        conn.execute(
            users.insert().values(
                email=email, password=password, role=role,
                name=name, company=company, title=title,
            )
        )

        token = secrets.token_hex(32)
        conn.execute(
            sessions.insert().values(
                token=token, email=email, role=role,
                name=name, company=company, title=title,
            )
        )

    return jsonify({
        "token": token,
        "user": {"email": email, "role": role, "name": name, "company": company, "title": title},
    }), 201


@app.route("/api/auth/reset-password", methods=["POST"])
def reset_password():
    """Set a new password when the email is registered. Does not reveal whether email exists."""
    body = request.get_json(silent=True) or {}
    email = (body.get("email") or "").strip().lower()
    new_password = body.get("new_password") or body.get("password") or ""

    if not email or not new_password:
        return jsonify({"error": "email and new_password are required"}), 400

    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return jsonify({"error": "Invalid email format"}), 400

    if len(new_password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    with get_db() as conn:
        row = conn.execute(
            text("SELECT email FROM users WHERE LOWER(email)=:email"), {"email": email}
        ).fetchone()
        if not row:
            return jsonify({"error": "No account found with this email"}), 404

        stored_email = row[0]
        conn.execute(
            text("UPDATE users SET password=:password WHERE LOWER(email)=:email"),
            {"password": new_password, "email": email},
        )
        conn.execute(
            text("DELETE FROM sessions WHERE LOWER(email)=:email"),
            {"email": email},
        )

    return jsonify({
        "success": True,
        "message": "Password updated. Sign in with your new password.",
        "email": stored_email,
    })


@app.route("/api/auth/me", methods=["GET"])
def me():
    session = get_session(request)
    if not session:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"user": session})


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    token = request.headers.get("Authorization", "").replace("Bearer ", "").strip()
    with get_db() as conn:
        conn.execute(
            text("DELETE FROM sessions WHERE token=:token"), {"token": token}
        )
    return jsonify({"success": True})


# ─── CANDIDATES (Employer search) ────────────────────────────────────────────────

def _matches_skill_filter(all_text: str, skill_filter: str) -> bool:
    if not skill_filter:
        return True
    text = all_text.lower()
    parts = [s.strip().lower() for s in skill_filter.split(",") if s.strip()]
    if not parts:
        return skill_filter.lower() in text
    return any(p in text for p in parts)


def _score_text_match(all_text: str, query: str, skill_filter: str, base_score: int = 70) -> int | None:
    """Return match score or None if row should be filtered out."""
    if not _matches_skill_filter(all_text, skill_filter):
        return None
    combined = " ".join(t for t in [query, skill_filter] if t.strip()).strip()
    if not combined:
        return base_score
    terms = combined.lower().split()
    term_hits = sum(1 for t in terms if len(t) > 1 and t in all_text)
    if term_hits == 0:
        return None
    bonus = term_hits * 5
    if term_hits == len(terms):
        bonus += 10
    return min(99, base_score + bonus)


def _search_talent_pool(
    query: str,
    skill_filter: str,
    status_filter: str,
    sort_by: str,
    min_exp: int,
    max_exp: int,
    location_filter: str,
) -> list[dict]:
    search_text = query or skill_filter
    location_lower = location_filter.lower()

    if search_text or status_filter or min_exp != 0 or max_exp != 99 or location_filter:
        try:
            payload = {
                "query": search_text or "developer",
                "skills": skill_filter or None,
                "min_experience": min_exp,
                "max_experience": max_exp,
                "top_k": 15,
            }
            response = requests.post(
                f"{INTELLIGENCE_URL}/intelligence/search", json=payload, timeout=30
            )
            response.raise_for_status()
            data = response.json()
            results = []
            for c in data.get("results", []):
                if status_filter and c.get("status", "").lower() != status_filter:
                    continue
                if location_lower and location_lower not in (c.get("location") or "").lower():
                    continue
                results.append({
                    "id": c.get("id", 0),
                    "source": "pool",
                    "name": c.get("name", ""),
                    "email": c.get("email", ""),
                    "title": c.get("title", ""),
                    "location": c.get("location", ""),
                    "experience": c.get("experience", 0),
                    "skills": c.get("skills", ""),
                    "match_score": c.get("fit_score") or c.get("vector_score") or 0,
                    "status": c.get("status", "available"),
                    "summary": c.get("summary", ""),
                    "education": c.get("education", ""),
                    "evaluation": c.get("evaluation", ""),
                })
            if results:
                if sort_by == "experience":
                    results.sort(key=lambda x: x["experience"], reverse=True)
                else:
                    results.sort(key=lambda x: x["match_score"], reverse=True)
                return results
            logging.info("Intelligence search returned no results, falling back to SQL")
        except Exception:
            logging.exception("Intelligence search proxy failed, falling back to local SQL search")

    return _search_talent_pool_sql(
        query, skill_filter, status_filter, sort_by, min_exp, max_exp, location_filter,
    )


def _search_talent_pool_sql(
    query: str,
    skill_filter: str,
    status_filter: str,
    sort_by: str,
    min_exp: int,
    max_exp: int,
    location_filter: str,
) -> list[dict]:
    location_lower = location_filter.lower()
    with get_db() as conn:
        raw = conn.execute(
            text("SELECT * FROM candidates WHERE experience >= :min_exp AND experience <= :max_exp"),
            {"min_exp": min_exp, "max_exp": max_exp},
        ).fetchall()
    rows = [dict(r._mapping) for r in raw]

    results = []
    for c in rows:
        skills = [s.strip().lower() for s in (c["skills"] or "").split(",")]
        skills_joined = " ".join(skills)
        title_lower = (c["title"] or "").lower()
        name_lower = (c["name"] or "").lower()
        summary_lower = (c["summary"] or "").lower()
        loc_lower = (c["location"] or "").lower()
        education_lower = (c["education"] or "").lower()
        email_lower = (c["email"] or "").lower()

        if location_lower and location_lower not in loc_lower:
            continue

        all_text = (
            f"{name_lower} {title_lower} {skills_joined} {summary_lower} "
            f"{loc_lower} {education_lower} {email_lower}"
        )

        if skill_filter and not _matches_skill_filter(all_text, skill_filter):
            continue

        if query or skill_filter:
            combined = " ".join(t for t in [query, skill_filter] if t.strip()).lower()
            terms = [t for t in combined.split() if len(t) > 1]
            if terms and not any(t in all_text for t in terms):
                continue

        score = c["match_score"] or 70
        if query or skill_filter:
            combined = " ".join(t for t in [query, skill_filter] if t.strip()).lower()
            terms = [t for t in combined.split() if len(t) > 1]
            title_lower = (c["title"] or "").lower()
            name_lower = (c["name"] or "").lower()
            loc_lower = (c["location"] or "").lower()
            title_matches = sum(1 for t in terms if t in title_lower)
            skill_matches = sum(1 for t in terms if any(t in s for s in skills))
            name_matches = sum(1 for t in terms if t in name_lower)
            location_matches = sum(1 for t in terms if t in loc_lower)
            bonus = (title_matches * 6) + (skill_matches * 4) + (name_matches * 3) + (location_matches * 2)
            term_hits = sum(1 for t in terms if t in all_text)
            if term_hits == len(terms):
                bonus += 10
            score = min(99, score + bonus)

        if status_filter and (c["status"] or "available").lower() != status_filter:
            continue

        results.append({
            "id": c["id"],
            "source": "pool",
            "name": c["name"],
            "email": c["email"] or "",
            "title": c["title"],
            "location": c["location"] or "",
            "experience": c["experience"],
            "skills": c["skills"] or "",
            "match_score": score,
            "status": c["status"] or "available",
            "summary": c["summary"] or "",
            "education": c["education"] or "",
        })

    if sort_by == "experience":
        results.sort(key=lambda x: x["experience"], reverse=True)
    else:
        results.sort(key=lambda x: x["match_score"], reverse=True)
    return results


def _search_application_resumes(
    employer_email: str,
    query: str,
    skill_filter: str,
    location_filter: str,
    project_filter: str,
) -> list[dict]:
    with get_db() as conn:
        raw = conn.execute(
            text("""
                SELECT a.id, a.candidate_email, a.resume_text, a.ats_score, a.applied_date,
                       j.title AS job_title, j.company
                FROM applications a
                JOIN jobs j ON j.id = a.job_id
                WHERE j.posted_by = :employer_email
            """),
            {"employer_email": employer_email},
        ).fetchall()
    rows = [dict(r._mapping) for r in raw]
    results = []
    effective_query = " ".join(t for t in [query, project_filter] if t.strip())
    for row in rows:
        resume_text = row["resume_text"] or ""
        name = row["candidate_email"].split("@")[0].replace(".", " ").title()
        all_text = f"{name} {resume_text} {row.get('job_title', '')} {row.get('company', '')}".lower()
        score = _score_text_match(all_text, effective_query, skill_filter, base_score=row["ats_score"] or 60)
        if score is None:
            continue
        if location_filter and location_filter.lower() not in all_text:
            continue
        if project_filter and project_filter.lower() not in all_text:
            continue
        excerpt = resume_text[:200] + ("…" if len(resume_text) > 200 else "")
        results.append({
            "id": f"application:{row['id']}",
            "source": "application",
            "name": name,
            "email": row["candidate_email"],
            "title": f"Applicant — {row.get('job_title', 'Unknown role')}",
            "location": "",
            "experience": 0,
            "skills": "",
            "match_score": score,
            "status": "submitted",
            "summary": excerpt,
            "education": "",
            "job_title": row.get("job_title", ""),
            "company": row.get("company", ""),
            "ats_score": row["ats_score"] or 0,
            "applied_date": row.get("applied_date", ""),
        })
    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results


def _search_uploaded_resumes(
    employer_email: str,
    query: str,
    skill_filter: str,
    location_filter: str,
    project_filter: str,
) -> list[dict]:
    with get_db() as conn:
        raw = conn.execute(
            text("SELECT * FROM resume_uploads WHERE employer_email = :email"),
            {"email": employer_email},
        ).fetchall()
    rows = [dict(r._mapping) for r in raw]
    results = []
    effective_query = " ".join(t for t in [query, project_filter] if t.strip())
    for row in rows:
        resume_text = row["resume_text"] or ""
        name = row["candidate_name"] or "Unknown Candidate"
        loc = row["location"] or ""
        skills = row["skills"] or ""
        all_text = f"{name} {resume_text} {loc} {skills}".lower()
        score = _score_text_match(
            all_text, effective_query, skill_filter,
            base_score=row.get("ai_score") or row.get("ats_score") or 65,
        )
        if score is None:
            continue
        if location_filter and location_filter.lower() not in all_text:
            continue
        if project_filter and project_filter.lower() not in all_text:
            continue
        excerpt = resume_text[:200] + ("…" if len(resume_text) > 200 else "")
        display_score = row.get("ai_score") or score
        results.append({
            "id": f"upload:{row['id']}",
            "source": "upload",
            "name": name,
            "email": "",
            "title": "Uploaded Resume",
            "location": loc,
            "experience": 0,
            "skills": skills,
            "match_score": display_score,
            "status": "available",
            "summary": excerpt,
            "education": "",
            "uploaded_date": row.get("uploaded_date", ""),
            "ats_score": row.get("ats_score") or 0,
            "ai_score": row.get("ai_score") or 0,
            "ai_evaluation": row.get("ai_evaluation") or "",
            "source_filename": row.get("source_filename") or "",
        })
    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results


def _merge_results(results: list[dict], sort_by: str) -> list[dict]:
    seen: set[str] = set()
    merged: list[dict] = []
    for r in results:
        key = r.get("email", "").lower() if r.get("email") else str(r.get("id", ""))
        if key and key in seen:
            continue
        if key:
            seen.add(key)
        merged.append(r)
    if sort_by == "experience":
        merged.sort(key=lambda x: x.get("experience", 0), reverse=True)
    else:
        merged.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    return merged


@app.route("/api/candidates/search", methods=["GET"])
def search_candidates():
    session = get_session(request)
    if not session:
        return jsonify({"error": "Unauthorized"}), 401

    query = (request.args.get("q") or "").strip()
    skill_filter = (request.args.get("skill") or "").strip()
    status_filter = (request.args.get("status") or "").strip().lower()
    sort_by = (request.args.get("sortBy") or "matchScore").strip()
    min_exp = request.args.get("min_exp", type=int, default=0)
    max_exp = request.args.get("max_exp", type=int, default=99)
    location_filter = (request.args.get("location") or "").strip()
    project_filter = (request.args.get("project") or "").strip()
    language_filter = (request.args.get("language") or "").strip()

    sources_raw = (request.args.get("sources") or "").strip()
    sources = {s.strip().lower() for s in sources_raw.split(",") if s.strip()}

    include_github = (request.args.get("include_github") or "").lower() in ("true", "1", "yes")

    # Default to talent pool only when no sources specified and GitHub is off
    if not sources and not include_github:
        sources = {"pool"}

    all_results: list[dict] = []
    github_error: str | None = None
    sources_used: list[str] = []

    if "pool" in sources:
        pool_results = _search_talent_pool(
            query, skill_filter, status_filter, sort_by,
            min_exp, max_exp, location_filter,
        )
        all_results.extend(pool_results)
        sources_used.append("pool")

    if "applications" in sources:
        app_results = _search_application_resumes(
            session["email"], query, skill_filter, location_filter, project_filter,
        )
        all_results.extend(app_results)
        sources_used.append("applications")

    if "uploads" in sources:
        upload_results = _search_uploaded_resumes(
            session["email"], query, skill_filter, location_filter, project_filter,
        )
        all_results.extend(upload_results)
        sources_used.append("uploads")

    if include_github:
        if not GITHUB_PAT:
            github_error = "GitHub search is not configured. Set GITHUB_PAT in your environment."
        elif GITHUB_PAT.startswith("glpat-"):
            github_error = (
                "GITHUB_PAT is a GitLab token, not a GitHub token. "
                "Create a GitHub PAT at github.com/settings/tokens (starts with ghp_)."
            )
        else:
            try:
                gh_query = query or skill_filter or project_filter or "developer"
                gh_results, gh_warning = search_github_users(
                    query=gh_query,
                    skill=skill_filter,
                    location=location_filter,
                    language=language_filter,
                    project=project_filter,
                    top_k=10,
                )
                all_results.extend(gh_results)
                if gh_results:
                    sources_used.append("github")
                    if gh_warning:
                        github_error = gh_warning
                else:
                    github_error = gh_warning or "No GitHub users matched your filters. Try broader keywords."
            except GitHubSearchError as exc:
                github_error = str(exc)
                logging.warning("GitHub search failed: %s", exc)
            except Exception as exc:
                github_error = f"GitHub search failed: {exc}"
                logging.exception("Unexpected GitHub search error")

    merged = _merge_results(all_results, sort_by)

    source_counts = {
        "pool": sum(1 for r in merged if r.get("source") == "pool"),
        "application": sum(1 for r in merged if r.get("source") == "application"),
        "upload": sum(1 for r in merged if r.get("source") == "upload"),
        "github": sum(1 for r in merged if r.get("source") == "github"),
    }

    response_data = {
        "candidates": merged,
        "total": len(merged),
        "sources_used": sources_used,
        "source_counts": source_counts,
        "github_enabled": include_github,
    }
    if github_error:
        response_data["github_error"] = github_error

    return jsonify(response_data)


# ─── RESUME UPLOADS (Employer library) ───────────────────────────────────────────

def _resolve_evaluation_job(session: dict, data: dict) -> tuple[dict | None, int | None, str]:
    """Build job context from a posted job id or employer-provided role fields."""
    job_id = data.get("job_id")
    if job_id:
        with get_db() as conn:
            row = conn.execute(
                text("SELECT * FROM jobs WHERE id=:id AND posted_by=:email"),
                {"id": job_id, "email": session["email"]},
            ).fetchone()
            if row:
                job = dict(row._mapping)
                exp_range = job.get("experience") or f"{job.get('experience_min')}-{job.get('experience_max')}"
                return {
                    "title": job.get("title") or "",
                    "skills": job.get("skills") or "",
                    "description": job.get("description") or "",
                    "experience": exp_range,
                }, int(job_id), job.get("title") or ""

    role_title = (data.get("role_title") or "").strip()
    role_skills = (data.get("role_skills") or "").strip()
    role_description = (data.get("role_description") or "").strip()
    role_experience = (data.get("role_experience") or "").strip()
    if role_title or role_skills or role_description or role_experience:
        if not role_title:
            return None, None, ""
        return {
            "title": role_title,
            "skills": role_skills,
            "description": role_description,
            "experience": role_experience,
        }, None, role_title or "Custom role"

    return None, None, ""


def _score_uploaded_resume(
    resume_text: str,
    *,
    candidate_name: str = "",
    location: str = "",
    skills: str = "",
    job: dict | None = None,
) -> tuple[int, int, str]:
    """Return (ats_score, ai_score, ai_evaluation) for an uploaded resume."""
    ats_score = 0
    if job:
        ats_score, _ = compute_ats_score(resume_text, job)

    ai_result = evaluate_resume_with_ai(
        resume_text,
        candidate_name=candidate_name,
        location=location,
        skills=skills,
        job=job,
    )
    return ats_score, ai_result["fit_score"], ai_result["evaluation"]


def _resume_row_to_dict(row: dict) -> dict:
    return {
        "id": row["id"],
        "candidate_name": row.get("candidate_name") or "",
        "location": row.get("location") or "",
        "skills": row.get("skills") or "",
        "uploaded_date": row.get("uploaded_date") or "",
        "source_filename": row.get("source_filename") or "",
        "ats_score": row.get("ats_score") or 0,
        "ai_score": row.get("ai_score") or 0,
        "ai_evaluation": row.get("ai_evaluation") or "",
        "evaluated_job_id": row.get("evaluated_job_id"),
        "evaluated_role_title": row.get("evaluated_role_title") or "",
    }


def _insert_resume_upload(
    conn,
    *,
    employer_email: str,
    candidate_name: str,
    location: str,
    skills: str,
    resume_text: str,
    uploaded_date: str,
    source_filename: str = "",
    ats_score: int = 0,
    ai_score: int = 0,
    ai_evaluation: str = "",
    evaluated_job_id: int | None = None,
    evaluated_role_title: str = "",
    tenant_key: str = "",
    dedup_hash: str = "",
    embedding: str = "",
) -> int:
    result = conn.execute(
        resume_uploads.insert().values(
            employer_email=employer_email,
            candidate_name=candidate_name,
            location=location,
            skills=skills,
            resume_text=resume_text[:15000],
            uploaded_date=uploaded_date,
            source_filename=source_filename,
            dedup_hash=dedup_hash,
            embedding=embedding,
            ats_score=ats_score,
            ai_score=ai_score,
            ai_evaluation=ai_evaluation[:2000],
            evaluated_job_id=evaluated_job_id,
            evaluated_role_title=evaluated_role_title[:200],
            tenant_key=tenant_key,
        )
    )
    return result.inserted_primary_key[0]


def _update_resume_upload(
    conn,
    resume_id: int,
    *,
    employer_email: str,
    candidate_name: str,
    location: str,
    skills: str,
    resume_text: str,
    uploaded_date: str,
    source_filename: str = "",
    ats_score: int = 0,
    ai_score: int = 0,
    ai_evaluation: str = "",
    evaluated_job_id: int | None = None,
    evaluated_role_title: str = "",
    tenant_key: str = "",
    dedup_hash: str = "",
    embedding: str = "",
) -> None:
    conn.execute(
        text(
            """
            UPDATE resume_uploads
            SET candidate_name=:candidate_name,
                location=:location,
                skills=:skills,
                resume_text=:resume_text,
                uploaded_date=:uploaded_date,
                source_filename=:source_filename,
                dedup_hash=:dedup_hash,
                embedding=:embedding,
                ats_score=:ats_score,
                ai_score=:ai_score,
                ai_evaluation=:ai_evaluation,
                evaluated_job_id=:evaluated_job_id,
                evaluated_role_title=:evaluated_role_title,
                tenant_key=:tenant_key
            WHERE id=:id AND employer_email=:employer_email
            """
        ),
        {
            "id": resume_id,
            "employer_email": employer_email,
            "candidate_name": candidate_name,
            "location": location,
            "skills": skills,
            "resume_text": resume_text[:15000],
            "uploaded_date": uploaded_date,
            "source_filename": source_filename,
            "dedup_hash": dedup_hash,
            "embedding": embedding,
            "ats_score": ats_score,
            "ai_score": ai_score,
            "ai_evaluation": ai_evaluation[:2000],
            "evaluated_job_id": evaluated_job_id,
            "evaluated_role_title": evaluated_role_title[:200],
            "tenant_key": tenant_key,
        },
    )


def _save_resume_upload(
    conn,
    *,
    employer_email: str,
    candidate_name: str,
    location: str,
    skills: str,
    resume_text: str,
    uploaded_date: str,
    source_filename: str = "",
    ats_score: int = 0,
    ai_score: int = 0,
    ai_evaluation: str = "",
    evaluated_job_id: int | None = None,
    evaluated_role_title: str = "",
    tenant_key: str = "",
    dedup_result=None,
    pending_embeddings: list | None = None,
) -> tuple[int, bool, str | None]:
    """
    Insert a resume after dedup pipeline passes.
    Returns (resume_id, created, error_message).
    """
    dedup = dedup_result or run_resume_dedup_pipeline(
        conn,
        employer_email,
        resume_text,
        pending_embeddings=pending_embeddings,
    )
    if not dedup.ok:
        return 0, False, dedup.reason

    fields = {
        "employer_email": employer_email,
        "candidate_name": candidate_name,
        "location": location,
        "skills": skills,
        "resume_text": resume_text,
        "uploaded_date": uploaded_date,
        "source_filename": source_filename,
        "ats_score": ats_score,
        "ai_score": ai_score,
        "ai_evaluation": ai_evaluation,
        "evaluated_job_id": evaluated_job_id,
        "evaluated_role_title": evaluated_role_title,
        "tenant_key": tenant_key,
        "dedup_hash": dedup.dedup_hash,
        "embedding": embedding_to_json(dedup.embedding),
    }
    new_id = _insert_resume_upload(conn, **fields)
    return new_id, True, None


@app.route("/api/resumes/upload", methods=["POST"])
def upload_resume():
    session = get_session(request)
    if not session or session["role"] != "employer":
        return jsonify({"error": "Unauthorized"}), 401

    body = request.get_json(silent=True) or {}
    resume_text = (body.get("resume_text") or "").strip()
    if not resume_text:
        return jsonify({"error": "resume_text is required"}), 400

    tenant_key = _tenant_key_from_company(session.get("company") or "", session.get("email") or "")
    source_filename = (body.get("source_filename") or "").strip()

    uploaded_date = datetime.now().strftime("%Y-%m-%d")
    job, job_id, role_title = _resolve_evaluation_job(session, body)
    if not job:
        return jsonify({
            "error": "Enter a role title to evaluate against (skills and description are optional).",
        }), 400

    with get_db() as conn:
        dedup = run_resume_dedup_pipeline(conn, session["email"], resume_text)
        if not dedup.ok:
            return jsonify(dedup.to_error_payload()), 409

        ats_score, ai_score, ai_evaluation = _score_uploaded_resume(
            resume_text,
            candidate_name=body.get("candidate_name", ""),
            location=body.get("location", ""),
            skills=body.get("skills", ""),
            job=job,
        )
        new_id = _insert_resume_upload(
            conn,
            employer_email=session["email"],
            candidate_name=body.get("candidate_name", ""),
            location=body.get("location", ""),
            skills=body.get("skills", ""),
            resume_text=resume_text,
            uploaded_date=uploaded_date,
            source_filename=source_filename,
            ats_score=ats_score,
            ai_score=ai_score,
            ai_evaluation=ai_evaluation,
            evaluated_job_id=job_id,
            evaluated_role_title=role_title,
            tenant_key=tenant_key,
            dedup_hash=dedup.dedup_hash,
            embedding=embedding_to_json(dedup.embedding),
        )

    return jsonify({
        "resume": {
            "id": new_id,
            "candidate_name": body.get("candidate_name", ""),
            "location": body.get("location", ""),
            "skills": body.get("skills", ""),
            "uploaded_date": uploaded_date,
            "ats_score": ats_score,
            "ai_score": ai_score,
            "ai_evaluation": ai_evaluation,
            "evaluated_role_title": role_title,
        },
        "created": True,
    }), 201


@app.route("/api/resumes/<int:resume_id>", methods=["PUT"])
def replace_resume(resume_id: int):
    """Idempotent full replacement of an existing resume upload."""
    session = get_session(request)
    if not session or session["role"] != "employer":
        return jsonify({"error": "Unauthorized"}), 401

    body = request.get_json(silent=True) or {}
    resume_text = (body.get("resume_text") or "").strip()
    if not resume_text:
        return jsonify({"error": "resume_text is required"}), 400

    tenant_key = _tenant_key_from_company(session.get("company") or "", session.get("email") or "")
    source_filename = (body.get("source_filename") or "").strip()
    uploaded_date = datetime.now().strftime("%Y-%m-%d")
    job, job_id, role_title = _resolve_evaluation_job(session, body)
    if not job:
        return jsonify({
            "error": "Enter a role title to evaluate against (skills and description are optional).",
        }), 400

    ats_score, ai_score, ai_evaluation = _score_uploaded_resume(
        resume_text,
        candidate_name=body.get("candidate_name", ""),
        location=body.get("location", ""),
        skills=body.get("skills", ""),
        job=job,
    )

    with get_db() as conn:
        row = conn.execute(
            text("SELECT id FROM resume_uploads WHERE id=:id AND employer_email=:email"),
            {"id": resume_id, "email": session["email"]},
        ).fetchone()
        if not row:
            return jsonify({"error": "Resume not found"}), 404

        dedup = run_resume_dedup_pipeline(
            conn,
            session["email"],
            resume_text,
            exclude_resume_id=resume_id,
        )
        if not dedup.ok:
            return jsonify(dedup.to_error_payload()), 409

        _update_resume_upload(
            conn,
            resume_id,
            employer_email=session["email"],
            candidate_name=body.get("candidate_name", ""),
            location=body.get("location", ""),
            skills=body.get("skills", ""),
            resume_text=resume_text,
            uploaded_date=uploaded_date,
            source_filename=source_filename,
            ats_score=ats_score,
            ai_score=ai_score,
            ai_evaluation=ai_evaluation,
            evaluated_job_id=job_id,
            evaluated_role_title=role_title,
            tenant_key=tenant_key,
            dedup_hash=dedup.dedup_hash,
            embedding=embedding_to_json(dedup.embedding),
        )

    return jsonify({
        "resume": {
            "id": resume_id,
            "candidate_name": body.get("candidate_name", ""),
            "location": body.get("location", ""),
            "skills": body.get("skills", ""),
            "uploaded_date": uploaded_date,
            "ats_score": ats_score,
            "ai_score": ai_score,
            "ai_evaluation": ai_evaluation,
            "evaluated_role_title": role_title,
        },
        "updated": True,
    })


@app.route("/api/resumes/<int:resume_id>", methods=["PATCH"])
def patch_resume(resume_id: int):
    """Partial, idempotent update of resume metadata or text."""
    session = get_session(request)
    if not session or session["role"] != "employer":
        return jsonify({"error": "Unauthorized"}), 401

    body = request.get_json(silent=True) or {}
    with get_db() as conn:
        row = conn.execute(
            text("SELECT * FROM resume_uploads WHERE id=:id AND employer_email=:email"),
            {"id": resume_id, "email": session["email"]},
        ).fetchone()
        if not row:
            return jsonify({"error": "Resume not found"}), 404
        existing = dict(row._mapping)

        resume_text = (body.get("resume_text") if "resume_text" in body else existing.get("resume_text") or "").strip()
        if not resume_text:
            return jsonify({"error": "resume_text cannot be empty"}), 400

        candidate_name = body.get("candidate_name") if "candidate_name" in body else existing.get("candidate_name") or ""
        location = body.get("location") if "location" in body else existing.get("location") or ""
        skills = body.get("skills") if "skills" in body else existing.get("skills") or ""
        source_filename = body.get("source_filename") if "source_filename" in body else existing.get("source_filename") or ""

        eval_data = {
            "job_id": body.get("job_id", existing.get("evaluated_job_id")),
            "role_title": body.get("role_title", existing.get("evaluated_role_title") or ""),
            "role_skills": body.get("role_skills", ""),
            "role_description": body.get("role_description", ""),
            "role_experience": body.get("role_experience", ""),
        }
        job, job_id, role_title = _resolve_evaluation_job(session, eval_data)
        if not job:
            return jsonify({
                "error": "A role title is required to evaluate this resume.",
            }), 400

        ats_score, ai_score, ai_evaluation = _score_uploaded_resume(
            resume_text,
            candidate_name=candidate_name,
            location=location,
            skills=skills,
            job=job,
        )
        uploaded_date = datetime.now().strftime("%Y-%m-%d")
        tenant_key = existing.get("tenant_key") or _tenant_key_from_company(
            session.get("company") or "", session.get("email") or ""
        )
        dedup = run_resume_dedup_pipeline(
            conn,
            session["email"],
            resume_text,
            exclude_resume_id=resume_id,
        )
        if not dedup.ok:
            return jsonify(dedup.to_error_payload()), 409

        _update_resume_upload(
            conn,
            resume_id,
            employer_email=session["email"],
            candidate_name=candidate_name,
            location=location,
            skills=skills,
            resume_text=resume_text,
            uploaded_date=uploaded_date,
            source_filename=source_filename,
            ats_score=ats_score,
            ai_score=ai_score,
            ai_evaluation=ai_evaluation,
            evaluated_job_id=job_id,
            evaluated_role_title=role_title,
            tenant_key=tenant_key,
            dedup_hash=dedup.dedup_hash,
            embedding=embedding_to_json(dedup.embedding),
        )

    return jsonify({
        "resume": {
            "id": resume_id,
            "candidate_name": candidate_name,
            "location": location,
            "skills": skills,
            "uploaded_date": uploaded_date,
            "ats_score": ats_score,
            "ai_score": ai_score,
            "ai_evaluation": ai_evaluation,
            "evaluated_role_title": role_title,
        },
        "updated": True,
    })


@app.route("/api/resumes/upload/bulk", methods=["POST"])
def upload_resumes_bulk():
    session = get_session(request)
    if not session or session["role"] != "employer":
        return jsonify({"error": "Unauthorized"}), 401

    files = request.files.getlist("files")
    if not files:
        single = request.files.get("file")
        if single:
            files = [single]
    if not files:
        return jsonify({"error": "No files uploaded. Send PDF, TXT, DOCX, or ZIP files."}), 400

    eval_data = {
        "job_id": request.form.get("job_id", type=int),
        "role_title": request.form.get("role_title", ""),
        "role_skills": request.form.get("role_skills", ""),
        "role_description": request.form.get("role_description", ""),
        "role_experience": request.form.get("role_experience", ""),
    }
    job, job_id, role_title = _resolve_evaluation_job(session, eval_data)
    if not job:
        return jsonify({
            "error": "Enter a role title to evaluate against (skills and description are optional).",
        }), 400

    uploaded_date = datetime.now().strftime("%Y-%m-%d")
    tenant_key = _tenant_key_from_company(session.get("company") or "", session.get("email") or "")
    saved: list[dict] = []
    errors: list[str] = []
    batch_embeddings: list[list[float]] = []
    batch_hashes: set[str] = set()

    for upload in files:
        if not upload.filename:
            continue
        file_data = upload.read()
        if not file_data:
            errors.append(f"{upload.filename}: empty file")
            continue
        try:
            parsed_list, parse_errors = parse_resume_upload(upload.filename, file_data)
            errors.extend(parse_errors)
        except ValueError as exc:
            errors.append(f"{upload.filename}: {exc}")
            continue

        with get_db() as conn:
            for item in parsed_list:
                dedup = run_resume_dedup_pipeline(
                    conn,
                    session["email"],
                    item["resume_text"],
                    pending_embeddings=batch_embeddings,
                    pending_hashes=batch_hashes,
                )
                if not dedup.ok:
                    label = item.get("source_filename") or item.get("candidate_name") or "Resume"
                    errors.append(format_bulk_item_error(label, dedup.reason))
                    continue

                ats_score, ai_score, ai_evaluation = _score_uploaded_resume(
                    item["resume_text"],
                    candidate_name=item["candidate_name"],
                    location=request.form.get("location", ""),
                    skills=request.form.get("skills", ""),
                    job=job,
                )
                resume_id, created, save_error = _save_resume_upload(
                    conn,
                    employer_email=session["email"],
                    candidate_name=item["candidate_name"],
                    location=request.form.get("location", ""),
                    skills=request.form.get("skills", ""),
                    resume_text=item["resume_text"],
                    uploaded_date=uploaded_date,
                    source_filename=item.get("source_filename", ""),
                    ats_score=ats_score,
                    ai_score=ai_score,
                    ai_evaluation=ai_evaluation,
                    evaluated_job_id=job_id,
                    evaluated_role_title=role_title,
                    tenant_key=tenant_key,
                    dedup_result=dedup,
                )
                if save_error:
                    label = item.get("source_filename") or item.get("candidate_name") or "Resume"
                    errors.append(format_bulk_item_error(label, save_error))
                    continue
                batch_hashes.add(dedup.dedup_hash)
                if dedup.embedding:
                    batch_embeddings.append(dedup.embedding)
                saved.append({
                    "id": resume_id,
                    "candidate_name": item["candidate_name"],
                    "source_filename": item.get("source_filename", ""),
                    "ats_score": ats_score,
                    "ai_score": ai_score,
                    "ai_evaluation": ai_evaluation,
                    "uploaded_date": uploaded_date,
                    "evaluated_role_title": role_title,
                    "created": created,
                })

    if not saved:
        if errors:
            if all("duplicate" in e.lower() or "already exists" in e.lower() for e in errors):
                summary = (
                    dedup_user_message(errors[0].split(": ", 1)[1])
                    if len(errors) == 1 and ": " in errors[0]
                    else f"All {len(errors)} file(s) are duplicates — nothing new was added to your library."
                )
            else:
                summary = "No resumes could be processed."
        else:
            summary = "No resumes could be processed."
        return jsonify({"error": summary, "errors": errors}), 400

    created_count = sum(1 for item in saved if item.get("created"))
    status_code = 201 if created_count == len(saved) and saved else 200
    return jsonify({
        "resumes": saved,
        "total": len(saved),
        "created": created_count,
        "errors": errors,
        "evaluated_job_id": job_id,
        "evaluated_role_title": role_title,
    }), status_code


@app.route("/api/resumes/mine", methods=["GET"])
def list_my_resumes():
    session = get_session(request)
    if not session or session["role"] != "employer":
        return jsonify({"error": "Unauthorized"}), 401

    with get_db() as conn:
        raw = conn.execute(
            text("""
                SELECT r.id, r.candidate_name, r.location, r.skills, r.uploaded_date,
                       r.source_filename, r.ats_score, r.ai_score, r.ai_evaluation,
                       r.evaluated_job_id, r.evaluated_role_title,
                       LENGTH(r.resume_text) AS text_length,
                       COALESCE(j.title, r.evaluated_role_title) AS evaluated_job_title
                FROM resume_uploads r
                LEFT JOIN jobs j ON j.id = r.evaluated_job_id
                WHERE r.employer_email = :email
                ORDER BY r.id DESC
            """),
            {"email": session["email"]},
        ).fetchall()
    rows = [dict(r._mapping) for r in raw]
    return jsonify({"resumes": rows, "total": len(rows)})


@app.route("/api/resumes/<int:resume_id>", methods=["DELETE"])
def delete_resume(resume_id: int):
    session = get_session(request)
    if not session or session["role"] != "employer":
        return jsonify({"error": "Unauthorized"}), 401

    with get_db() as conn:
        row = conn.execute(
            text("SELECT id FROM resume_uploads WHERE id=:id AND employer_email=:email"),
            {"id": resume_id, "email": session["email"]},
        ).fetchone()
        if not row:
            return jsonify({"error": "Resume not found"}), 404
        conn.execute(
            text("DELETE FROM resume_uploads WHERE id=:id"),
            {"id": resume_id},
        )
    return jsonify({"success": True})


@app.route("/api/resumes/mine", methods=["DELETE"])
def clear_my_resumes():
    session = get_session(request)
    if not session or session["role"] != "employer":
        return jsonify({"error": "Unauthorized"}), 401

    with get_db() as conn:
        result = conn.execute(
            text("DELETE FROM resume_uploads WHERE employer_email=:email"),
            {"email": session["email"]},
        )
        deleted = result.rowcount or 0
    return jsonify({"success": True, "deleted": deleted})


# ─── JOBS (Employee browsing) ────────────────────────────────────────────────────

@app.route("/api/jobs", methods=["GET"])
def list_jobs():
    query = (request.args.get("q") or "").lower().strip()

    with get_db() as conn:
        raw = conn.execute(text("SELECT * FROM jobs WHERE status='active'")).fetchall()
    rows = [dict(r._mapping) for r in raw]

    results = []
    for j in rows:
        relevance = 0
        if query:
            searchable = f"{j['title']} {j['company']} {j['skills'] or ''} {j['description'] or ''} {j['location'] or ''} {j['type'] or ''} {j['salary'] or ''}".lower()
            terms = query.split()
            term_hits = sum(1 for t in terms if t in searchable)
            if term_hits == 0:
                continue
            title_lower = j["title"].lower()
            skills_lower = (j["skills"] or "").lower()
            relevance = sum(3 for t in terms if t in title_lower) + sum(2 for t in terms if t in skills_lower) + term_hits

        exp_range = j["experience"] or f"{j['experience_min']}-{j['experience_max']}"
        tenant_key = j.get("tenant_key") or _tenant_key_from_company(j.get("company", ""), j.get("posted_by", ""))
        results.append({
            "id": j["id"],
            "title": j["title"],
            "company": j["company"],
            "tenant_key": tenant_key,
            "location": j["location"] or "",
            "type": j["type"] or "Full-time",
            "experience": exp_range,
            "skills": j["skills"] or "",
            "description": j["description"] or "",
            "salary": j["salary"] or "",
            "posted_date": j["posted_date"] or "",
            "_relevance": relevance,
        })

    if query:
        results.sort(key=lambda x: x["_relevance"], reverse=True)
    for r in results:
        r.pop("_relevance", None)

    return jsonify({"jobs": results, "total": len(results)})


@app.route("/api/tenants/jobs", methods=["GET"])
def list_tenant_jobs():
    session = get_session(request)
    if not session or session["role"] != "employee":
        return jsonify({"error": "Unauthorized"}), 401

    query = (request.args.get("q") or "").lower().strip()

    with get_db() as conn:
        raw = conn.execute(text("SELECT * FROM jobs WHERE status='active' ORDER BY posted_date DESC, id DESC")).fetchall()
    rows = [dict(r._mapping) for r in raw]

    tenant_map: dict[str, dict] = {}
    for job in rows:
        searchable = (
            f"{job.get('title', '')} {job.get('company', '')} {job.get('skills', '')} "
            f"{job.get('description', '')} {job.get('location', '')} {job.get('type', '')} {job.get('salary', '')}"
        ).lower()
        if query and query not in searchable:
            continue

        tenant_key = job.get("tenant_key") or _tenant_key_from_company(job.get("company", ""), job.get("posted_by", ""))
        tenant_name = job.get("company") or "Unknown Company"
        if tenant_key not in tenant_map:
            tenant_map[tenant_key] = {
                "tenant_key": tenant_key,
                "company": tenant_name,
                "jobs": [],
            }

        exp_range = job["experience"] or f"{job['experience_min']}-{job['experience_max']}"
        tenant_map[tenant_key]["jobs"].append({
            "id": job["id"],
            "tenant_key": tenant_key,
            "title": job["title"],
            "company": tenant_name,
            "location": job.get("location") or "",
            "type": job.get("type") or "Full-time",
            "experience": exp_range,
            "skills": job.get("skills") or "",
            "description": job.get("description") or "",
            "salary": job.get("salary") or "",
            "posted_date": job.get("posted_date") or "",
        })

    tenants = list(tenant_map.values())
    tenants.sort(key=lambda t: (-len(t["jobs"]), t["company"].lower()))

    for tenant in tenants:
        tenant["total_jobs"] = len(tenant["jobs"])

    return jsonify({
        "tenants": tenants,
        "total_tenants": len(tenants),
        "total_jobs": sum(t["total_jobs"] for t in tenants),
    })


@app.route("/api/jobs/mine", methods=["GET"])
def my_jobs():
    session = get_session(request)
    if not session or session["role"] != "employer":
        return jsonify({"error": "Unauthorized"}), 401

    with get_db() as conn:
        raw = conn.execute(
            text("SELECT * FROM jobs WHERE posted_by=:email ORDER BY id DESC"),
            {"email": session["email"]},
        ).fetchall()
    rows = [dict(r._mapping) for r in raw]
    results = []
    for j in rows:
        exp_range = j["experience"] or f"{j['experience_min']}-{j['experience_max']}"
        tenant_key = j.get("tenant_key") or _tenant_key_from_company(j.get("company", ""), j.get("posted_by", ""))
        results.append({
            "id": j["id"],
            "title": j["title"],
            "company": j["company"],
            "tenant_key": tenant_key,
            "location": j["location"] or "",
            "type": j["type"] or "Full-time",
            "experience": exp_range,
            "skills": j["skills"] or "",
            "description": j["description"] or "",
            "status": j["status"] or "active",
            "posted_date": j["posted_date"] or "",
        })
    return jsonify({"jobs": results, "total": len(results)})


@app.route("/api/jobs", methods=["POST"])
def create_job():
    session = get_session(request)
    if not session or session["role"] != "employer":
        return jsonify({"error": "Unauthorized"}), 401

    body = request.get_json(silent=True) or {}
    posted_date = datetime.now().strftime("%Y-%m-%d")
    company = session.get("company") or body.get("company", "")
    tenant_key = _tenant_key_from_company(company, session.get("email", ""))

    with get_db() as conn:
        result = conn.execute(
            jobs.insert().values(
                title=body.get("title", ""),
                company=company,
                location=body.get("location", ""),
                type=body.get("type", "Full-time"),
                experience_min=body.get("experience_min", 0),
                experience_max=body.get("experience_max", 5),
                experience=body.get("experience", ""),
                skills=body.get("skills", ""),
                description=body.get("description", ""),
                salary=body.get("salary", ""),
                posted_by=session["email"],
                posted_date=posted_date,
                status="active",
                tenant_key=tenant_key,
            )
        )
        new_id = result.inserted_primary_key[0]

    new_job = {
        "id": new_id,
        "title": body.get("title", ""),
        "company": company,
        "tenant_key": tenant_key,
        "location": body.get("location", ""),
        "type": body.get("type", "Full-time"),
        "experience_min": body.get("experience_min", 0),
        "experience_max": body.get("experience_max", 5),
        "experience": body.get("experience", ""),
        "skills": body.get("skills", ""),
        "description": body.get("description", ""),
        "salary": body.get("salary", ""),
        "posted_by": session["email"],
        "posted_date": posted_date,
        "status": "active",
    }
    return jsonify({"job": new_job}), 201


@app.route("/api/jobs/<int:job_id>", methods=["PUT"])
def replace_job(job_id: int):
    """Idempotent full replacement of a job posting."""
    session = get_session(request)
    if not session or session["role"] != "employer":
        return jsonify({"error": "Unauthorized"}), 401

    body = request.get_json(silent=True) or {}
    required = ("title", "description")
    missing = [field for field in required if not str(body.get(field) or "").strip()]
    if missing:
        return jsonify({"error": f"{', '.join(missing)} are required for PUT"}), 400

    with get_db() as conn:
        existing_row = conn.execute(
            text("SELECT * FROM jobs WHERE id=:id AND posted_by=:email"),
            {"id": job_id, "email": session["email"]},
        ).fetchone()
        if not existing_row:
            return jsonify({"error": "Job not found"}), 404

        existing = dict(existing_row._mapping)
        updated = {
            "title": str(body.get("title", "")).strip(),
            "location": str(body.get("location", "")).strip(),
            "type": str(body.get("type", "Full-time")).strip() or "Full-time",
            "experience": str(body.get("experience", "")).strip(),
            "skills": str(body.get("skills", "")).strip(),
            "description": str(body.get("description", "")).strip(),
            "salary": str(body.get("salary", "")).strip(),
            "status": str(body.get("status", "active")).strip() or "active",
        }

        conn.execute(
            text(
                """
                UPDATE jobs
                SET title=:title, location=:location, type=:type, experience=:experience,
                    skills=:skills, description=:description, salary=:salary, status=:status
                WHERE id=:id AND posted_by=:email
                """
            ),
            {
                **updated,
                "id": job_id,
                "email": session["email"],
            },
        )

    return jsonify({
        "job": {
            "id": job_id,
            "title": updated["title"],
            "company": existing.get("company") or "",
            "tenant_key": existing.get("tenant_key") or _tenant_key_from_company(existing.get("company", ""), session.get("email", "")),
            "location": updated["location"],
            "type": updated["type"] or "Full-time",
            "experience": updated["experience"],
            "skills": updated["skills"],
            "description": updated["description"],
            "salary": updated["salary"],
            "status": updated["status"],
            "posted_date": existing.get("posted_date") or "",
        },
        "updated": True,
    })


@app.route("/api/jobs/<int:job_id>", methods=["PATCH"])
def patch_job(job_id: int):
    """Partial, idempotent update of a job posting."""
    session = get_session(request)
    if not session or session["role"] != "employer":
        return jsonify({"error": "Unauthorized"}), 401

    body = request.get_json(silent=True) or {}
    if not body:
        return jsonify({"error": "No fields to update"}), 400

    with get_db() as conn:
        existing_row = conn.execute(
            text("SELECT * FROM jobs WHERE id=:id AND posted_by=:email"),
            {"id": job_id, "email": session["email"]},
        ).fetchone()
        if not existing_row:
            return jsonify({"error": "Job not found"}), 404

        existing = dict(existing_row._mapping)
        updated = {
            "title": str(body.get("title") if body.get("title") is not None else (existing.get("title") or "")).strip(),
            "location": str(body.get("location") if body.get("location") is not None else (existing.get("location") or "")).strip(),
            "type": str(body.get("type") if body.get("type") is not None else (existing.get("type") or "Full-time")).strip(),
            "experience": str(body.get("experience") if body.get("experience") is not None else (existing.get("experience") or "")).strip(),
            "skills": str(body.get("skills") if body.get("skills") is not None else (existing.get("skills") or "")).strip(),
            "description": str(body.get("description") if body.get("description") is not None else (existing.get("description") or "")).strip(),
            "salary": str(body.get("salary") if body.get("salary") is not None else (existing.get("salary") or "")).strip(),
            "status": str(body.get("status") if body.get("status") is not None else (existing.get("status") or "active")).strip() or "active",
        }

        if not updated["title"] or not updated["description"]:
            return jsonify({"error": "title and description are required"}), 400

        conn.execute(
            text(
                """
                UPDATE jobs
                SET title=:title, location=:location, type=:type, experience=:experience,
                    skills=:skills, description=:description, salary=:salary, status=:status
                WHERE id=:id AND posted_by=:email
                """
            ),
            {
                **updated,
                "id": job_id,
                "email": session["email"],
            },
        )

    return jsonify({
        "job": {
            "id": job_id,
            "title": updated["title"],
            "company": existing.get("company") or "",
            "tenant_key": existing.get("tenant_key") or _tenant_key_from_company(existing.get("company", ""), session.get("email", "")),
            "location": updated["location"],
            "type": updated["type"] or "Full-time",
            "experience": updated["experience"],
            "skills": updated["skills"],
            "description": updated["description"],
            "salary": updated["salary"],
            "status": updated["status"],
            "posted_date": existing.get("posted_date") or "",
        },
        "updated": True,
    })


@app.route("/api/jobs/<int:job_id>/applications", methods=["GET"])
def list_job_applications(job_id: int):
    session = get_session(request)
    if not session or session["role"] != "employer":
        return jsonify({"error": "Unauthorized"}), 401

    with get_db() as conn:
        job_row = conn.execute(
            text("SELECT id, title, company, tenant_key FROM jobs WHERE id=:id AND posted_by=:email"),
            {"id": job_id, "email": session["email"]},
        ).fetchone()
        if not job_row:
            return jsonify({"error": "Job not found"}), 404

        raw = conn.execute(
            text(
                """
                SELECT id, candidate_email, ats_score, status, applied_date, resume_text
                FROM applications
                WHERE job_id=:job_id
                ORDER BY ats_score DESC, id DESC
                """
            ),
            {"job_id": job_id},
        ).fetchall()

    job = dict(job_row._mapping)
    rows = [dict(r._mapping) for r in raw]
    results = []
    for a in rows:
        ats = int(a.get("ats_score") or 0)
        breakdown = _breakdown_from_ats(ats)
        results.append({
            "id": a["id"],
            "candidate_email": a.get("candidate_email") or "",
            "candidate_name": (a.get("candidate_email") or "").split("@")[0].replace(".", " ").title(),
            "ats_score": ats,
            "fit_for_job": ats >= 70,
            "status": a.get("status") or "submitted",
            "applied_date": a.get("applied_date") or "",
            "resume_excerpt": (a.get("resume_text") or "")[:240],
            "breakdown": breakdown,
        })

    return jsonify({
        "job": {
            "id": job["id"],
            "title": job.get("title") or "",
            "company": job.get("company") or "",
            "tenant_key": job.get("tenant_key") or _tenant_key_from_company(job.get("company", ""), session.get("email", "")),
        },
        "applications": results,
        "total": len(results),
    })


# ─── APPLICATIONS (Employee apply) ──────────────────────────────────────────────

def _parse_application_payload():
    body = request.get_json(silent=True) if request.is_json else {}
    job_id = body.get("job_id") if body else request.form.get("job_id", type=int)
    resume_text = (body.get("resume_text", "") if body else request.form.get("resume_text", "")).strip()

    uploaded = request.files.get("resume_file")
    if uploaded and uploaded.filename:
        file_data = uploaded.read()
        if not file_data:
            return None, None, ({"error": "Uploaded file is empty"}, 400)
        try:
            parsed_list, _ = parse_resume_upload(uploaded.filename, file_data)
        except ValueError as exc:
            return None, None, ({"error": str(exc)}, 400)
        if len(parsed_list) > 1:
            return None, None, ({"error": "Please upload a single resume file when applying."}, 400)
        parsed_resume = parsed_list[0]
        if not resume_text:
            resume_text = parsed_resume.get("resume_text", "").strip()

    if not job_id or not resume_text:
        return None, None, ({"error": "job_id and either resume_text or resume_file are required"}, 400)
    return int(job_id), resume_text, None


def _application_response(conn, *, job_id: int, candidate_email: str, created: bool):
    row = conn.execute(
        text("SELECT * FROM jobs WHERE id=:id"), {"id": job_id}
    ).fetchone()
    job = dict(row._mapping) if row else None
    if not job:
        return {"error": "Job not found"}, 404

    app_row = conn.execute(
        text(
            """
            SELECT id, applied_date, ats_score, status, tenant_key
            FROM applications
            WHERE job_id=:job_id AND candidate_email=:email
            LIMIT 1
            """
        ),
        {"job_id": job_id, "email": candidate_email},
    ).fetchone()
    if not app_row:
        return {"error": "Application not found"}, 404

    app_data = dict(app_row._mapping)
    resume_row = conn.execute(
        text("SELECT resume_text FROM applications WHERE id=:id"),
        {"id": app_data["id"]},
    ).fetchone()
    resume_text = (dict(resume_row._mapping).get("resume_text") or "") if resume_row else ""
    ats_score, breakdown = compute_ats_score(resume_text, job)

    payload = {
        "application": {
            "id": app_data["id"],
            "job_id": job_id,
            "candidate_email": candidate_email,
            "applied_date": app_data.get("applied_date") or "",
            "ats_score": app_data.get("ats_score") or ats_score,
            "status": app_data.get("status") or "submitted",
            "tenant_key": app_data.get("tenant_key") or "",
        },
        "ats_score": app_data.get("ats_score") or ats_score,
        "breakdown": breakdown,
        "created": created,
        "updated": not created,
    }
    return payload, 201 if created else 200


@app.route("/api/applications", methods=["POST"])
def create_application():
    """Create a new job application. Returns 409 if the candidate already applied."""
    session = get_session(request)
    if not session or session["role"] != "employee":
        return jsonify({"error": "Unauthorized"}), 401

    job_id, resume_text, error = _parse_application_payload()
    if error:
        return jsonify(error[0]), error[1]

    with get_db() as conn:
        job_row = conn.execute(
            text("SELECT * FROM jobs WHERE id=:id"), {"id": job_id}
        ).fetchone()
        if not job_row:
            return jsonify({"error": "Job not found"}), 404
        job = dict(job_row._mapping)

        existing = conn.execute(
            text(
                """
                SELECT id FROM applications
                WHERE job_id=:job_id AND candidate_email=:email
                LIMIT 1
                """
            ),
            {"job_id": job_id, "email": session["email"]},
        ).fetchone()
        if existing:
            return jsonify({
                "error": "You have already applied to this job",
                "application_id": int(existing[0]),
                "hint": f"Use PUT /api/applications/job/{job_id} to update your application.",
            }), 409

        ats_score, _ = compute_ats_score(resume_text, job)
        tenant_key = job.get("tenant_key") or _tenant_key_from_company(job.get("company", ""), job.get("posted_by", ""))
        applied_date = datetime.now().strftime("%Y-%m-%d")
        conn.execute(
            applications.insert().values(
                job_id=job_id,
                candidate_email=session["email"],
                resume_text=resume_text[:8000],
                applied_date=applied_date,
                ats_score=ats_score,
                status="submitted",
                tenant_key=tenant_key,
            )
        )

        payload, status_code = _application_response(
            conn, job_id=job_id, candidate_email=session["email"], created=True
        )
    return jsonify(payload), status_code


@app.route("/api/applications/job/<int:job_id>", methods=["PUT"])
def upsert_application(job_id: int):
    """Idempotent create-or-replace application for the current employee and job."""
    session = get_session(request)
    if not session or session["role"] != "employee":
        return jsonify({"error": "Unauthorized"}), 401

    body = request.get_json(silent=True) if request.is_json else {}
    resume_text = (body.get("resume_text", "") if body else request.form.get("resume_text", "")).strip()

    uploaded = request.files.get("resume_file")
    if uploaded and uploaded.filename:
        file_data = uploaded.read()
        if not file_data:
            return jsonify({"error": "Uploaded file is empty"}), 400
        try:
            parsed_list, _ = parse_resume_upload(uploaded.filename, file_data)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        if len(parsed_list) > 1:
            return jsonify({"error": "Please upload a single resume file when applying."}), 400
        parsed_resume = parsed_list[0]
        if not resume_text:
            resume_text = parsed_resume.get("resume_text", "").strip()

    if not resume_text:
        return jsonify({"error": "resume_text or resume_file is required"}), 400

    with get_db() as conn:
        job_row = conn.execute(
            text("SELECT * FROM jobs WHERE id=:id"), {"id": job_id}
        ).fetchone()
        if not job_row:
            return jsonify({"error": "Job not found"}), 404
        job = dict(job_row._mapping)

        ats_score, _ = compute_ats_score(resume_text, job)
        tenant_key = job.get("tenant_key") or _tenant_key_from_company(job.get("company", ""), job.get("posted_by", ""))
        applied_date = datetime.now().strftime("%Y-%m-%d")
        params = {
            "job_id": job_id,
            "email": session["email"],
            "resume_text": resume_text[:8000],
            "applied_date": applied_date,
            "ats_score": ats_score,
            "tenant_key": tenant_key,
        }

        insert_result = conn.execute(
            text(
                """
                INSERT INTO applications (job_id, candidate_email, resume_text, applied_date, ats_score, status, tenant_key)
                SELECT :job_id, :email, :resume_text, :applied_date, :ats_score, 'submitted', :tenant_key
                WHERE NOT EXISTS (
                    SELECT 1 FROM applications WHERE job_id=:job_id AND candidate_email=:email
                )
                """
            ),
            params,
        )
        created = bool(insert_result.rowcount)
        if not created:
            conn.execute(
                text(
                    """
                    UPDATE applications
                    SET resume_text=:resume_text,
                        applied_date=:applied_date,
                        ats_score=:ats_score,
                        tenant_key=:tenant_key,
                        status='submitted'
                    WHERE job_id=:job_id AND candidate_email=:email
                    """
                ),
                params,
            )

        payload, status_code = _application_response(
            conn, job_id=job_id, candidate_email=session["email"], created=created
        )
    return jsonify(payload), status_code


@app.route("/api/applications/<int:application_id>", methods=["PATCH"])
def patch_application(application_id: int):
    """Partial, idempotent update of an application (employee: own only)."""
    session = get_session(request)
    if not session or session["role"] != "employee":
        return jsonify({"error": "Unauthorized"}), 401

    body = request.get_json(silent=True) or {}
    if not body:
        return jsonify({"error": "No fields to update"}), 400

    with get_db() as conn:
        row = conn.execute(
            text(
                """
                SELECT a.*, j.title AS job_title
                FROM applications a
                JOIN jobs j ON j.id = a.job_id
                WHERE a.id=:id AND a.candidate_email=:email
                """
            ),
            {"id": application_id, "email": session["email"]},
        ).fetchone()
        if not row:
            return jsonify({"error": "Application not found"}), 404

        existing = dict(row._mapping)
        job_row = conn.execute(
            text("SELECT * FROM jobs WHERE id=:id"), {"id": existing["job_id"]}
        ).fetchone()
        job = dict(job_row._mapping) if job_row else {}

        resume_text = body.get("resume_text") if "resume_text" in body else existing.get("resume_text") or ""
        resume_text = str(resume_text).strip()
        if not resume_text:
            return jsonify({"error": "resume_text cannot be empty"}), 400

        status = body.get("status") if "status" in body else existing.get("status") or "submitted"
        ats_score, breakdown = compute_ats_score(resume_text, job)
        applied_date = datetime.now().strftime("%Y-%m-%d")

        conn.execute(
            text(
                """
                UPDATE applications
                SET resume_text=:resume_text,
                    applied_date=:applied_date,
                    ats_score=:ats_score,
                    status=:status
                WHERE id=:id AND candidate_email=:email
                """
            ),
            {
                "id": application_id,
                "email": session["email"],
                "resume_text": resume_text[:8000],
                "applied_date": applied_date,
                "ats_score": ats_score,
                "status": status,
            },
        )

    return jsonify({
        "application": {
            "id": application_id,
            "job_id": existing["job_id"],
            "candidate_email": session["email"],
            "applied_date": applied_date,
            "ats_score": ats_score,
            "status": status,
        },
        "ats_score": ats_score,
        "breakdown": breakdown,
        "updated": True,
    })


@app.route("/api/applications/my", methods=["GET"])
def my_applications():
    session = get_session(request)
    if not session:
        return jsonify({"error": "Unauthorized"}), 401

    with get_db() as conn:
        raw = conn.execute(
            text("""SELECT a.id, a.job_id, a.ats_score, a.applied_date, a.status,
                     a.tenant_key, j.title AS job_title, j.company
               FROM applications a
               LEFT JOIN jobs j ON j.id = a.job_id
               WHERE a.candidate_email=:email"""),
            {"email": session["email"]},
        ).fetchall()
    rows = [dict(r._mapping) for r in raw]

    results = []
    for a in rows:
        ats = a["ats_score"] or 0
        breakdown = _breakdown_from_ats(ats)
        results.append({
            "id": a["id"],
            "job_id": a["job_id"],
            "job_title": a["job_title"] or "Unknown",
            "company": a["company"] or "",
            "tenant_key": a.get("tenant_key") or _tenant_key_from_company(a.get("company", ""), session.get("email", "")),
            "ats_score": ats,
            "applied_at": a["applied_date"] or "",
            "status": a["status"] or "submitted",
            "breakdown": breakdown,
        })

    return jsonify({"applications": results})


# ─── HEALTH ──────────────────────────────────────────────────────────────────────

@app.route("/api/health")
def health():
    from database import DATABASE_URL
    dialect = DATABASE_URL.split("://")[0]
    return jsonify({"status": "ok", "engine": "python", "db": dialect})


# ─── INIT ────────────────────────────────────────────────────────────────────────

init_db()

if __name__ == "__main__":
    debug_enabled = os.getenv("FLASK_DEBUG", "").strip().lower() in ("1", "true", "yes")
    app.run(host="0.0.0.0", port=3001, debug=debug_enabled, use_reloader=False)
