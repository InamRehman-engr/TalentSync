"""
database.py — SQLAlchemy engine, connection pool, and table definitions.

To switch from SQLite to PostgreSQL, set the DATABASE_URL environment variable:

    DATABASE_URL=postgresql://user:password@host:5432/dbname

No other code changes are required — all SQL in app.py and db_sync.py uses
dialect-neutral SQLAlchemy constructs. Schema changes are managed with Alembic
(see backend-python/alembic/versions/).
"""

from __future__ import annotations

import os
import logging
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, event, MetaData, Table, Column,
    String, Integer, Text, CheckConstraint, ForeignKey, UniqueConstraint,
)
from sqlalchemy.pool import NullPool

log = logging.getLogger(__name__)

# ─── ENGINE ───────────────────────────────────────────────────────────────────

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
_DEFAULT_URL = f"sqlite:///{os.path.join(DATA_DIR, 'nhr.db')}"
DATABASE_URL: str = os.getenv("DATABASE_URL", _DEFAULT_URL)

_is_sqlite = DATABASE_URL.startswith("sqlite")

if _is_sqlite:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=NullPool,
    )

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragmas(dbapi_conn, _record) -> None:
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL")
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()
else:
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
    )

# ─── SCHEMA ───────────────────────────────────────────────────────────────────

metadata = MetaData()

users = Table(
    "users", metadata,
    Column("email", String, primary_key=True),
    Column("password", String, nullable=False),
    Column("role", String, nullable=False),
    Column("name", String, nullable=False),
    Column("company", String, server_default=""),
    Column("title", String, server_default=""),
    CheckConstraint("role IN ('employer','employee')", name="ck_users_role"),
)

candidates = Table(
    "candidates", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String, nullable=False),
    Column("title", String, nullable=False),
    Column("location", String, server_default=""),
    Column("experience", Integer, server_default="0"),
    Column("skills", Text, server_default=""),
    Column("match_score", Integer, server_default="70"),
    Column("status", String, server_default="available"),
    Column("email", String, server_default=""),
    Column("summary", Text, server_default=""),
    Column("education", String, server_default=""),
    Column("sync_key", String),
    UniqueConstraint("sync_key", name="uq_candidates_sync_key"),
)

jobs = Table(
    "jobs", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("title", String, nullable=False),
    Column("company", String, nullable=False),
    Column("location", String, server_default=""),
    Column("type", String, server_default="Full-time"),
    Column("experience_min", Integer, server_default="0"),
    Column("experience_max", Integer, server_default="5"),
    Column("experience", String, server_default=""),
    Column("skills", Text, server_default=""),
    Column("description", Text, server_default=""),
    Column("salary", String, server_default=""),
    Column("posted_by", String, nullable=False),
    Column("posted_date", String, nullable=False),
    Column("status", String, server_default="active"),
    Column("tenant_key", String, server_default=""),
    Column("sync_key", String),
    UniqueConstraint("sync_key", name="uq_jobs_sync_key"),
)

applications = Table(
    "applications", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("job_id", Integer, ForeignKey("jobs.id"), nullable=False),
    Column("candidate_email", String, nullable=False),
    Column("resume_text", Text, server_default=""),
    Column("applied_date", String, nullable=False),
    Column("ats_score", Integer, server_default="0"),
    Column("status", String, server_default="submitted"),
    Column("tenant_key", String, server_default=""),
    UniqueConstraint("job_id", "candidate_email", name="uq_applications_job_candidate"),
)

sessions = Table(
    "sessions", metadata,
    Column("token", String, primary_key=True),
    Column("email", String, nullable=False),
    Column("role", String, nullable=False),
    Column("name", String, nullable=False),
    Column("company", String, server_default=""),
    Column("title", String, server_default=""),
)

resume_uploads = Table(
    "resume_uploads", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("employer_email", String, nullable=False),
    Column("candidate_name", String, server_default=""),
    Column("location", String, server_default=""),
    Column("skills", Text, server_default=""),
    Column("resume_text", Text, nullable=False),
    Column("uploaded_date", String, nullable=False),
    Column("source_filename", String, server_default=""),
    Column("dedup_hash", String),
    Column("embedding", Text),
    Column("ats_score", Integer, server_default="0"),
    Column("evaluated_job_id", Integer),
    Column("evaluated_role_title", String, server_default=""),
    Column("ai_score", Integer, server_default="0"),
    Column("ai_evaluation", Text, server_default=""),
    Column("tenant_key", String, server_default=""),
)

# ─── INIT ─────────────────────────────────────────────────────────────────────


def resume_dedup_hash(employer_email: str, resume_text: str, source_filename: str = "") -> str:
    """Stable key from normalized resume content (per employer)."""
    from resume_dedup import resume_content_hash

    return resume_content_hash(employer_email, resume_text)


def init_schema() -> None:
    """Apply pending Alembic migrations. Safe to call on every startup."""
    from migrate import run_migrations

    run_migrations()
    log.info("database: schema ready (%s)", DATABASE_URL.split("://")[0])
