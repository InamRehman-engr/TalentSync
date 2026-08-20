"""Add resume dedup_hash column and unique index.

Revision ID: 0002_add_resume_dedup_hash
Revises: 0001_initial_schema
Create Date: 2026-07-04

One-time data migration: backfills dedup_hash for legacy resume_uploads rows.
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect, text

revision: str = "0002_add_resume_dedup_hash"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _backfill_dedup_hashes(connection) -> None:
    from database import resume_dedup_hash

    rows = connection.execute(
        text(
            """
            SELECT id, employer_email, resume_text, source_filename
            FROM resume_uploads
            WHERE dedup_hash IS NULL OR dedup_hash = ''
            ORDER BY id ASC
            """
        )
    ).fetchall()
    if not rows:
        return

    seen: set[tuple[str, str]] = set()
    for row in rows:
        data = dict(row._mapping)
        dedup_hash = resume_dedup_hash(
            data["employer_email"],
            data.get("resume_text") or "",
            data.get("source_filename") or "",
        )
        key = (data["employer_email"].strip().lower(), dedup_hash)
        if key in seen:
            continue
        seen.add(key)
        connection.execute(
            text("UPDATE resume_uploads SET dedup_hash=:hash WHERE id=:id"),
            {"hash": dedup_hash, "id": data["id"]},
        )


def upgrade() -> None:
    bind = op.get_bind()
    columns = {col["name"] for col in inspect(bind).get_columns("resume_uploads")}

    if "dedup_hash" not in columns:
        op.add_column("resume_uploads", sa.Column("dedup_hash", sa.String(), nullable=True))

    _backfill_dedup_hashes(bind)

    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_resume_uploads_employer_dedup "
        "ON resume_uploads(employer_email, dedup_hash) "
        "WHERE dedup_hash IS NOT NULL AND dedup_hash != ''"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_resume_uploads_employer_dedup")
    columns = {col["name"] for col in inspect(op.get_bind()).get_columns("resume_uploads")}
    if "dedup_hash" in columns:
        op.drop_column("resume_uploads", "dedup_hash")
