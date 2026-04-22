"""Scheduler jobs for recurring market intelligence summaries."""

from __future__ import annotations

from typing import Any, Dict, List

from agents.orchestrator import run_analysis
from agents.report_agent import build_digest_summary
from feishu.cards import build_digest_card
from feishu.sender import send_card
from tools.knowledge_base import (
    list_competitor_organization_ids,
    load_competitors_for_organization,
)


def _targets_for_frequency(frequency: str, organization_id: str = "") -> List[str]:
    payload = load_competitors_for_organization(organization_id=organization_id or None)
    competitors = payload.get("competitors", [])
    return [
        competitor.get("name", "")
        for competitor in competitors
        if competitor.get("name") and competitor.get("monitoring_frequency", "manual") == frequency
    ]


def run_scheduled_scan(frequency: str = "daily", organization_id: str = "") -> Dict[str, Any]:
    reports: List[Dict[str, Any]] = []
    alerts: List[Dict[str, Any]] = []
    organization_ids = [organization_id] if organization_id else list_competitor_organization_ids()

    for scoped_organization_id in organization_ids:
        targets = _targets_for_frequency(frequency, organization_id=scoped_organization_id)
        for target in targets:
            result = run_analysis(
                [target],
                output_format="summary",
                organization_id=scoped_organization_id or None,
            )
            reports.append(result.get("report", {}))
            alerts.extend(result.get("alerts", []))

    summary = build_digest_summary(reports, alerts, frequency)
    summary["card"] = build_digest_card(summary)
    return summary


def run_and_dispatch_summary(
    frequency: str = "daily",
    organization_id: str = "",
) -> Dict[str, Any]:
    summary = run_scheduled_scan(frequency, organization_id=organization_id)
    delivery = send_card(summary["card"])
    return {"summary": summary, "delivery": delivery}
