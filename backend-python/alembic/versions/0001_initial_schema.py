"""Initial schema baseline.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-07-04

Creates core tables when missing and adds legacy columns on databases that
predate Alembic. Safe to run on existing production databases.
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(name: str) -> bool:
    return inspect(op.get_bind()).has_table(name)


def _has_column(table: str, column: str) -> bool:
    if not _has_table(table):
        return False
    return column in {col["name"] for col in inspect(op.get_bind()).get_columns(table)}


def _add_column_if_missing(table: str, column: sa.Column) -> None:
    if _has_column(table, column.name):
        return
    op.add_column(table, column)


def upgrade() -> None:
    from database import metadata

    bind = op.get_bind()

    if not _has_table("users"):
        metadata.tables["users"].create(bind)

    if not _has_table("candidates"):
        metadata.tables["candidates"].create(bind)

    if not _has_table("jobs"):
        metadata.tables["jobs"].create(bind)

    if not _has_table("sessions"):
        metadata.tables["sessions"].create(bind)

    if not _has_table("applications"):
        metadata.tables["applications"].create(bind)

    if not _has_table("resume_uploads"):
        op.create_table(
            "resume_uploads",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("employer_email", sa.String(), nullable=False),
            sa.Column("candidate_name", sa.String(), server_default=""),
            sa.Column("location", sa.String(), server_default=""),
            sa.Column("skills", sa.Text(), server_default=""),
            sa.Column("resume_text", sa.Text(), nullable=False),
            sa.Column("uploaded_date", sa.String(), nullable=False),
            sa.Column("source_filename", sa.String(), server_default=""),
            sa.Column("ats_score", sa.Integer(), server_default="0"),
            sa.Column("evaluated_job_id", sa.Integer(), nullable=True),
            sa.Column("evaluated_role_title", sa.String(), server_default=""),
            sa.Column("ai_score", sa.Integer(), server_default="0"),
            sa.Column("ai_evaluation", sa.Text(), server_default=""),
            sa.Column("tenant_key", sa.String(), server_default=""),
            sa.PrimaryKeyConstraint("id"),
        )

    # Legacy column patches for DBs created before incremental schema updates.
    _add_column_if_missing("candidates", sa.Column("sync_key", sa.String(), nullable=True))
    _add_column_if_missing("jobs", sa.Column("sync_key", sa.String(), nullable=True))
    _add_column_if_missing("jobs", sa.Column("tenant_key", sa.String(), server_default=""))
    _add_column_if_missing("applications", sa.Column("tenant_key", sa.String(), server_default=""))
    _add_column_if_missing("resume_uploads", sa.Column("source_filename", sa.String(), server_default=""))
    _add_column_if_missing("resume_uploads", sa.Column("ats_score", sa.Integer(), server_default="0"))
    _add_column_if_missing("resume_uploads", sa.Column("evaluated_job_id", sa.Integer(), nullable=True))
    _add_column_if_missing("resume_uploads", sa.Column("evaluated_role_title", sa.String(), server_default=""))
    _add_column_if_missing("resume_uploads", sa.Column("ai_score", sa.Integer(), server_default="0"))
    _add_column_if_missing("resume_uploads", sa.Column("ai_evaluation", sa.Text(), server_default=""))
    _add_column_if_missing("resume_uploads", sa.Column("tenant_key", sa.String(), server_default=""))

    if _has_column("jobs", "tenant_key"):
        op.execute(
            "CREATE INDEX IF NOT EXISTS idx_jobs_status_tenant ON jobs(status, tenant_key)"
        )
    if _has_column("applications", "tenant_key"):
        op.execute(
            "CREATE INDEX IF NOT EXISTS idx_applications_tenant_key ON applications(tenant_key)"
        )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_applications_job_candidate "
        "ON applications(job_id, candidate_email)"
    )


def downgrade() -> None:
    bind = op.get_bind()
    for name in reversed(["resume_uploads", "applications", "sessions", "jobs", "candidates", "users"]):
        if inspect(bind).has_table(name):
            op.drop_table(name)
