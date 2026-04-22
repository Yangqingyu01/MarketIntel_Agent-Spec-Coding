"""Shared helper utilities for building reports and runtime messages."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any


LOGGER_NAME = "marketintel"


def get_logger(name: str = LOGGER_NAME) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("[%(levelname)s] %(name)s - %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def current_date() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def safe_json_dumps(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)


def truncate_text(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    return value[: max(limit - 3, 0)] + "..."


def degradation_note(reason: str, reliability: str) -> str:
    return "{reason}。结果可靠性：{reliability}".format(
        reason=reason,
        reliability=reliability,
    )
