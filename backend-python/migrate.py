"""Run Alembic migrations (alembic upgrade head)."""
from __future__ import annotations

import logging
from pathlib import Path

from alembic import command
from alembic.config import Config

log = logging.getLogger(__name__)


def run_migrations() -> None:
    ini_path = Path(__file__).resolve().parent / "alembic.ini"
    cfg = Config(str(ini_path))
    command.upgrade(cfg, "head")
    log.info("database: migrations applied (alembic head)")
