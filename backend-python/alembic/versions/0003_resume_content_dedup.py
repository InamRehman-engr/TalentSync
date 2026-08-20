"""Recompute dedup_hash from normalized content; add embedding column.

Revision ID: 0003_resume_content_dedup
Revises: 0002_add_resume_dedup_hash
Create Date: 2026-07-06
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect, text

revision: str = "0003_resume_content_dedup"
down_revision: Union[str, None] = "0002_add_resume_dedup_hash"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _recompute_dedup_hashes(connection) -> None:
    from resume_dedup import resume_content_hash

    rows = connection.execute(
        text(
            """
            SELECT id, employer_email, resume_text
            FROM resume_uploads
            ORDER BY id ASC
            """
        )
    ).fetchall()
    if not rows:
        return

    seen: set[tuple[str, str]] = set()
    for row in rows:
        data = dict(row._mapping)
        dedup_hash = resume_content_hash(
            data["employer_email"],
            data.get("resume_text") or "",
        )
        key = (data["employer_email"].strip().lower(), dedup_hash)
        if key in seen:
            connection.execute(
                text("DELETE FROM resume_uploads WHERE id = :id"),
                {"id": data["id"]},
            )
            continue
        seen.add(key)
        connection.execute(
            text("UPDATE resume_uploads SET dedup_hash = :hash WHERE id = :id"),
            {"hash": dedup_hash, "id": data["id"]},
        )


def upgrade() -> None:
    bind = op.get_bind()
    columns = {col["name"] for col in inspect(bind).get_columns("resume_uploads")}

    if "embedding" not in columns:
        op.add_column("resume_uploads", sa.Column("embedding", sa.Text(), nullable=True))

    _recompute_dedup_hashes(bind)


def downgrade() -> None:
    columns = {col["name"] for col in inspect(op.get_bind()).get_columns("resume_uploads")}
    if "embedding" in columns:
        op.drop_column("resume_uploads", "embedding")
