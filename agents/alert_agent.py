"""Alert agent for future change detection integration."""

from __future__ import annotations

from typing import Any


def generate_alerts(
    target: str,
    analysis_results: list[dict[str, Any]],
    baseline: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """MVP keeps alerts empty until change detection is implemented."""
    return []
