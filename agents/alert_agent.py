"""Alert agent for change grading and deduplication."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from tools.knowledge_base import find_similar_alert, record_alert
from tools.report_builder import utc_now_iso


def _build_dedup_key(change: Dict[str, Any]) -> str:
    summary = change.get("description", "").strip().lower()
    return "{company}|{dimension}|{change_type}|{summary}".format(
        company=change.get("company", "").strip().lower(),
        dimension=change.get("dimension", "").strip().lower(),
        change_type=change.get("change_type", "").strip().lower(),
        summary=summary,
    )


def _grade_severity(change: Dict[str, Any]) -> str:
    credibility = float(change.get("credibility", 0.0))
    if change.get("severity_candidate") == "high" or credibility >= 0.85:
        return "high"
    if credibility >= 0.65:
        return "medium"
    return "low"


def generate_alerts(
    target: str,
    analysis_results: List[Dict[str, Any]],
    baseline: Optional[Dict[str, Any]] = None,
    change_events: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Generate graded alerts while suppressing recent duplicates."""
    del analysis_results
    del baseline
    alerts: List[Dict[str, Any]] = []
    for change in change_events or []:
        dedup_key = _build_dedup_key(change)
        duplicate = find_similar_alert(
            company=target,
            change_type=change.get("change_type", ""),
            dimension=change.get("dimension", ""),
            dedup_key=dedup_key,
        )
        if duplicate:
            continue

        severity = _grade_severity(change)
        alert = {
            "alert_id": "ALT-{company}-{index}".format(
                company=target,
                index=len(alerts) + 1,
            ),
            "company": target,
            "change_type": change.get("change_type", ""),
            "dimension": change.get("dimension", ""),
            "severity": severity,
            "title": "{company} {dimension} 变化预警".format(
                company=target,
                dimension=change.get("dimension", "signal"),
            ),
            "description": change.get("description", ""),
            "recommended_actions": [
                {
                    "department": "product" if change.get("dimension") == "product" else "strategy",
                    "action": "复核该变化并确认是否需要追加监测或人工研判。",
                }
            ],
            "push_timing": "immediate" if severity == "high" else "daily_digest",
            "detected_at": utc_now_iso(),
            "dedup_key": dedup_key,
            "source_url": change.get("source_url", ""),
        }
        record_alert(alert)
        alerts.append(alert)
    return alerts
