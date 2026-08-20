"""
db_sync.py — Declarative database sync using Pydantic models.

How it works
------------
* Define seed/reference data as typed Pydantic models below.
* On every app startup, `run_sync(db_path)` is called.
* It performs an UPSERT for every record defined here:
    - Users  → keyed by `email` (PRIMARY KEY).
    - Candidates → keyed by `sync_key` (a stable slug you assign).
    - Jobs       → keyed by `sync_key` (a stable slug you assign).
* Records that are NOT in this file (i.e. created by users at runtime)
  are NEVER modified or deleted.
* If you change a field value here and restart, the DB row is updated.
* If you remove a record from this file, the DB row is left as-is
  (soft-delete — you can delete it manually via Adminer if needed).
"""

from __future__ import annotations

import logging
from typing import Literal
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy import select, update, func
from database import engine, users, candidates, jobs

log = logging.getLogger(__name__)


# ─── PYDANTIC MODELS ──────────────────────────────────────────────────────────

class UserRecord(BaseModel):
    email: EmailStr
    password: str
    role: Literal["employer", "employee"]
    name: str
    company: str = ""
    title: str = ""

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("password must be at least 6 characters")
        return v


class CandidateRecord(BaseModel):
    sync_key: str          # stable slug, e.g. "candidate-ali-hassan"
    name: str
    title: str
    location: str = ""
    experience: int = 0
    skills: str = ""
    match_score: int = 70
    status: Literal["available", "hired", "interviewing"] = "available"
    email: str = ""
    summary: str = ""
    education: str = ""


class JobRecord(BaseModel):
    sync_key: str          # stable slug, e.g. "job-senior-embedded-techventures"
    title: str
    company: str
    location: str = ""
    type: str = "Full-time"
    experience_min: int = 0
    experience_max: int = 5
    experience: str = ""
    skills: str = ""
    description: str = ""
    salary: str = ""
    posted_by: EmailStr
    posted_date: str       # YYYY-MM-DD
    status: Literal["active", "closed"] = "active"


# ─── SEED / REFERENCE DATA ────────────────────────────────────────────────────
# Edit these lists to change what gets synced on every restart.

USERS: list[UserRecord] = [
    UserRecord(
        email="employer1@talentsync.com",
        password="Employer@123",
        role="employer",
        name="Ahmed Raza",
        company="TechVentures",
        title="HR Director",
    ),
    UserRecord(
        email="employer2@talentsync.com",
        password="Employer@123",
        role="employer",
        name="Sarah Khan",
        company="NexGen Solutions",
        title="Talent Lead",
    ),
    UserRecord(
        email="employee1@talentsync.com",
        password="Employee@123",
        role="employee",
        name="Ali Khan",
        title="Embedded Systems Engineer",
    ),
    UserRecord(
        email="employee2@talentsync.com",
        password="Employee@123",
        role="employee",
        name="Fatima Noor",
        title="Full Stack Developer",
    ),
]

CANDIDATES: list[CandidateRecord] = [
    CandidateRecord(
        sync_key="candidate-ali-hassan",
        name="Ali Hassan",
        title="Embedded Systems Engineer",
        location="Lahore, PK",
        experience=3,
        skills="C,C++,ARM Cortex,FreeRTOS,PCB Design,UART,SPI,I2C",
        match_score=92,
        status="available",
        email="employee1@talentsync.com",
        summary="Experienced embedded engineer with expertise in ARM-based microcontrollers and real-time systems.",
        education="BS Electrical Engineering - LUMS",
    ),
    CandidateRecord(
        sync_key="candidate-fatima-noor",
        name="Fatima Noor",
        title="Full Stack Developer",
        location="Islamabad, PK",
        experience=4,
        skills="Vue.js,React,Node.js,Python,PostgreSQL,Docker",
        match_score=88,
        status="available",
        email="employee2@talentsync.com",
        summary="Versatile full-stack developer with production experience in Vue and React ecosystems.",
        education="BS Computer Science - NUST",
    ),
    CandidateRecord(
        sync_key="candidate-usman-tariq",
        name="Usman Tariq",
        title="Data Scientist",
        location="Karachi, PK",
        experience=2,
        skills="Python,TensorFlow,PyTorch,SQL,Pandas,Scikit-learn",
        match_score=85,
        status="available",
        email="employee3@talentsync.com",
        summary="Data scientist specializing in NLP and predictive modeling with published research.",
        education="MS Data Science - IBA Karachi",
    ),
    CandidateRecord(
        sync_key="candidate-zara-malik",
        name="Zara Malik",
        title="Frontend Engineer",
        location="Lahore, PK",
        experience=3,
        skills="React,Vue.js,TypeScript,Tailwind CSS,Next.js,Figma",
        match_score=90,
        status="available",
        email="employee4@talentsync.com",
        summary="Frontend specialist passionate about performance and accessible design systems.",
        education="BS Software Engineering - UET Lahore",
    ),
]

JOBS: list[JobRecord] = [
    JobRecord(
        sync_key="job-senior-embedded-techventures",
        title="Senior Embedded Engineer",
        company="TechVentures",
        location="Lahore, PK",
        type="Full-time",
        experience_min=2,
        experience_max=5,
        skills="C,C++,ARM Cortex,RTOS,PCB Design",
        description=(
            "We are looking for an experienced embedded systems engineer to design firmware "
            "for our IoT product line. Must have hands-on experience with ARM Cortex-M "
            "microcontrollers and real-time operating systems."
        ),
        posted_by="employer1@talentsync.com",
        posted_date="2026-04-10",
        status="active",
    ),
    JobRecord(
        sync_key="job-fullstack-nexgen",
        title="Full Stack Developer",
        company="NexGen Solutions",
        location="Islamabad, PK",
        type="Full-time",
        experience_min=2,
        experience_max=4,
        skills="Vue.js,Node.js,PostgreSQL,Docker",
        description=(
            "Join our product team to build scalable web applications. Strong frontend "
            "skills with Vue.js and backend experience with Node.js required."
        ),
        posted_by="employer2@talentsync.com",
        posted_date="2026-04-09",
        status="active",
    ),
    JobRecord(
        sync_key="job-data-scientist-techventures",
        title="Data Scientist",
        company="TechVentures",
        location="Karachi, PK",
        type="Full-time",
        experience_min=1,
        experience_max=3,
        skills="Python,TensorFlow,SQL,Pandas",
        description=(
            "Looking for a data scientist to build predictive models for our HR analytics "
            "platform. Experience with NLP is a plus."
        ),
        posted_by="employer1@talentsync.com",
        posted_date="2026-04-08",
        status="active",
    ),
    JobRecord(
        sync_key="job-devops-nexgen",
        title="DevOps Engineer",
        company="NexGen Solutions",
        location="Remote",
        type="Full-time",
        experience_min=3,
        experience_max=6,
        skills="AWS,Kubernetes,Terraform,CI/CD,Docker",
        description=(
            "Seeking a DevOps engineer to manage our cloud infrastructure and deployment "
            "pipelines. Must be comfortable with AWS and container orchestration."
        ),
        posted_by="employer2@talentsync.com",
        posted_date="2026-04-07",
        status="active",
    ),
]


# ─── SYNC ENGINE ──────────────────────────────────────────────────────────────

def _sync_users(conn) -> None:
    for u in USERS:
        existing = conn.execute(
            select(users.c.email).where(func.lower(users.c.email) == u.email.lower())
        ).fetchone()

        if existing:
            conn.execute(
                update(users)
                .where(func.lower(users.c.email) == u.email.lower())
                .values(password=u.password, role=u.role, name=u.name,
                        company=u.company, title=u.title)
            )
            log.debug("db_sync: updated user %s", u.email)
        else:
            conn.execute(users.insert().values(**u.model_dump()))
            log.info("db_sync: inserted user %s", u.email)


def _sync_candidates(conn) -> None:
    for c in CANDIDATES:
        existing = conn.execute(
            select(candidates.c.id).where(candidates.c.sync_key == c.sync_key)
        ).fetchone()

        if existing:
            conn.execute(
                update(candidates)
                .where(candidates.c.sync_key == c.sync_key)
                .values(**c.model_dump(exclude={"sync_key"}))
            )
            log.debug("db_sync: updated candidate %s", c.sync_key)
        else:
            conn.execute(candidates.insert().values(**c.model_dump()))
            log.info("db_sync: inserted candidate %s", c.sync_key)


def _sync_jobs(conn) -> None:
    for j in JOBS:
        existing = conn.execute(
            select(jobs.c.id).where(jobs.c.sync_key == j.sync_key)
        ).fetchone()

        if existing:
            conn.execute(
                update(jobs)
                .where(jobs.c.sync_key == j.sync_key)
                .values(**j.model_dump(exclude={"sync_key"}))
            )
            log.debug("db_sync: updated job %s", j.sync_key)
        else:
            conn.execute(jobs.insert().values(**j.model_dump()))
            log.info("db_sync: inserted job %s", j.sync_key)


def run_sync() -> None:
    """
    Upsert all USERS, CANDIDATES, and JOBS defined in this file.
    Call once on startup after init_schema() has been called.
    engine.begin() provides an auto-commit/rollback transaction.
    """
    with engine.begin() as conn:
        _sync_users(conn)
        _sync_candidates(conn)
        _sync_jobs(conn)
    log.info("db_sync: sync complete")
