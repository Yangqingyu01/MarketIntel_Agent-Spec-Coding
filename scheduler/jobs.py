"""Scheduler jobs for recurring market intelligence summaries."""

from __future__ import annotations

from typing import Any, Dict, List

from agents.orchestrator import run_analysis
from agents.report_agent import build_digest_summary
from feishu.cards import build_digest_card
from feishu.sender import send_card
from tools.knowledge_base import load_competitors


def _targets_for_frequency(frequency: str) -> List[str]:
    payload = load_competitors()
    competitors = payload.get("competitors", [])
    return [
        competitor.get("name", "")
        for competitor in competitors
        if competitor.get("name") and competitor.get("monitoring_frequency", "manual") == frequency
    ]


def run_scheduled_scan(frequency: str = "daily") -> Dict[str, Any]:
    targets = _targets_for_frequency(frequency)
    reports: List[Dict[str, Any]] = []
    alerts: List[Dict[str, Any]] = []
    for target in targets:
        result = run_analysis([target], output_format="summary")
        reports.append(result.get("report", {}))
        alerts.extend(result.get("alerts", []))

    summary = build_digest_summary(reports, alerts, frequency)
    summary["card"] = build_digest_card(summary)
    return summary


def run_and_dispatch_summary(frequency: str = "daily") -> Dict[str, Any]:
    summary = run_scheduled_scan(frequency)
    delivery = send_card(summary["card"])
    return {"summary": summary, "delivery": delivery}
