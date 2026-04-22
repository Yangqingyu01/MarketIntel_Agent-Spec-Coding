"""Alert agent for future change detection integration."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def generate_alerts(
    target: str,
    analysis_results: List[Dict[str, Any]],
    baseline: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """MVP keeps alerts empty until change detection is implemented."""
    return []
