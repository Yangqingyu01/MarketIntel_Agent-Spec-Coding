"""FastAPI routes for the MarketIntel MVP."""

from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from agents.orchestrator import run_analysis
from auth.service import AuthenticatedUser, require_authenticated_user
from config import config
from feishu.cards import build_digest_card
from feishu.sender import send_card
from scheduler.jobs import run_scheduled_scan
from scheduler.runner import describe_scheduler
from tools.knowledge_base import (
    list_recent_alerts,
    list_snapshots,
    load_competitors_for_organization,
    save_competitor,
)


router = APIRouter(prefix="/api")


def _dimension_items(snapshot: Dict, dimension: str) -> List[Dict]:
    return [
        item
        for item in snapshot.get("items", [])
        if item.get("dimension") == dimension
    ]


def _history_payload(company: str, organization_id: str) -> Dict:
    snapshots = list_snapshots(company=company, limit=8, organization_id=organization_id)
    snapshots_chronological = list(reversed(snapshots))
    timeline = []
    comparisons = []

    previous_snapshot = None
    for snapshot in snapshots_chronological:
        product_items = _dimension_items(snapshot, "product")
        pricing_items = _dimension_items(snapshot, "pricing")
        timeline.append(
            {
                "snapshot_id": snapshot.get("snapshot_id", ""),
                "snapshot_date": snapshot.get("snapshot_date", ""),
                "source_count": snapshot.get("source_count", 0),
                "product_count": len(product_items),
                "pricing_count": len(pricing_items),
            }
        )

        current_summary = {}
        for dimension in ("product", "pricing"):
            current_items = _dimension_items(snapshot, dimension)
            previous_items = (
                _dimension_items(previous_snapshot, dimension)
                if previous_snapshot
                else []
            )
            current_signals = {
                item.get("extracted_data", "") for item in current_items if item.get("extracted_data")
            }
            previous_signals = {
                item.get("extracted_data", "") for item in previous_items if item.get("extracted_data")
            }
            new_signals = sorted(current_signals - previous_signals)[:3]
            removed_signals = sorted(previous_signals - current_signals)[:3]
            current_summary[dimension] = {
                "count": len(current_items),
                "delta": len(current_items) - len(previous_items),
                "highlights": new_signals,
                "removed": removed_signals,
            }

        comparisons.append(
            {
                "snapshot_id": snapshot.get("snapshot_id", ""),
                "snapshot_date": snapshot.get("snapshot_date", ""),
                "product": current_summary["product"],
                "pricing": current_summary["pricing"],
            }
        )
        previous_snapshot = snapshot

    snapshot_list = []
    for snapshot in snapshots:
        items = snapshot.get("items", [])
        snapshot_list.append(
            {
                "snapshot_id": snapshot.get("snapshot_id", ""),
                "snapshot_date": snapshot.get("snapshot_date", ""),
                "source_count": snapshot.get("source_count", 0),
                "overall_confidence": snapshot.get("overall_confidence", 0.0),
                "dimensions": snapshot.get("dimensions", []),
                "items": [
                    {
                        "dimension": item.get("dimension", ""),
                        "extracted_data": item.get("extracted_data", ""),
                        "evidence_quote": item.get("evidence_quote", ""),
                        "source_url": item.get("source_url", ""),
                        "source_name": item.get("source_name", ""),
                        "publish_date": item.get("publish_date", ""),
                        "crawl_date": item.get("crawl_date", ""),
                        "credibility": item.get("credibility", 0.0),
                    }
                    for item in items
                ],
            }
        )

    return {
        "company": company,
        "snapshots": snapshot_list,
        "timeline": timeline,
        "comparisons": list(reversed(comparisons)),
        "alerts": list_recent_alerts(limit=20, company=company, organization_id=organization_id),
    }


def _history_overview_payload(companies: List[str], organization_id: str) -> Dict:
    rows = []
    normalized_companies = []
    for company in companies:
        company_name = company.strip()
        if not company_name:
            continue
        normalized_companies.append(company_name)
        history = _history_payload(company_name, organization_id=organization_id)
        for point in history.get("timeline", []):
            rows.append(
                {
                    "company": company_name,
                    "snapshot_id": point.get("snapshot_id", ""),
                    "snapshot_date": point.get("snapshot_date", ""),
                    "product_count": point.get("product_count", 0),
                    "pricing_count": point.get("pricing_count", 0),
                    "source_count": point.get("source_count", 0),
                }
            )
    rows.sort(key=lambda item: (item.get("snapshot_date", ""), item.get("company", "")), reverse=True)
    return {"companies": normalized_companies, "rows": rows[:24]}


class AnalyzeRequest(BaseModel):
    targets: List[str] = Field(..., min_length=1)
    dimensions: List[str] = Field(default_factory=lambda: list(config.default_dimensions))
    time_range: str = config.default_time_range


@router.post("/analyze")
async def analyze(
    req: AnalyzeRequest,
    user: AuthenticatedUser = Depends(require_authenticated_user),
) -> Dict:
    result = run_analysis(
        targets=req.targets,
        dimensions=req.dimensions,
        time_range=req.time_range,
        organization_id=user.organization_id,
    )
    return {
        "task_id": result["task_id"],
        "report": result["report"],
        "alerts": result["alerts"],
        "intel_count": len(result["analysis_results"]),
    }


@router.get("/alerts")
async def get_alerts(user: AuthenticatedUser = Depends(require_authenticated_user)) -> Dict:
    return {"alerts": list_recent_alerts(organization_id=user.organization_id)}


@router.get("/config/competitors")
async def list_competitors(
    user: AuthenticatedUser = Depends(require_authenticated_user),
) -> Dict:
    return load_competitors_for_organization(organization_id=user.organization_id)


@router.post("/config/competitors")
async def add_competitor(
    competitor: Dict,
    user: AuthenticatedUser = Depends(require_authenticated_user),
) -> Dict:
    save_competitor(competitor, organization_id=user.organization_id)
    return {"ok": True}


@router.get("/scheduler/status")
async def scheduler_status(
    user: AuthenticatedUser = Depends(require_authenticated_user),
) -> Dict:
    payload = load_competitors_for_organization(organization_id=user.organization_id)
    competitors = payload.get("competitors", [])
    frequency_counts = {"daily": 0, "weekly": 0, "manual": 0}
    for item in competitors:
        frequency = item.get("monitoring_frequency", "manual")
        if frequency not in frequency_counts:
            frequency_counts[frequency] = 0
        frequency_counts[frequency] += 1
    return {
        "scheduler": describe_scheduler(),
        "competitor_count": len(competitors),
        "frequency_counts": frequency_counts,
    }


@router.get("/scheduler/summary")
async def scheduler_summary(
    frequency: str = Query(default="daily", pattern="^(daily|weekly)$"),
    user: AuthenticatedUser = Depends(require_authenticated_user),
) -> Dict:
    summary = run_scheduled_scan(frequency, organization_id=user.organization_id)
    return {"summary": summary}


@router.get("/feishu/status")
async def feishu_status() -> Dict:
    sample_summary = {
        "summary_type": "daily",
        "headline": "Daily monitoring digest preview",
    }
    sample_card = build_digest_card(sample_summary)
    preview_delivery = send_card(sample_card)
    target_chat = config.feishu_target_chat_id
    masked_chat = (
        ""
        if not target_chat
        else "{head}***{tail}".format(
            head=target_chat[:3],
            tail=target_chat[-3:] if len(target_chat) > 3 else "",
        )
    )
    return {
        "configured": bool(config.feishu_app_id and config.feishu_app_secret),
        "delivery_mode": preview_delivery.get("delivery_mode", "mock"),
        "app_id_configured": bool(config.feishu_app_id),
        "app_secret_configured": bool(config.feishu_app_secret),
        "target_chat_configured": bool(target_chat),
        "target_chat_masked": masked_chat,
        "webhook_endpoint": "/api/feishu/webhook",
        "preview_delivery": {
            "ok": preview_delivery.get("ok", False),
            "delivery_mode": preview_delivery.get("delivery_mode", "mock"),
            "chat_id": preview_delivery.get("chat_id", ""),
        },
        "sample_card": sample_card,
    }


@router.get("/history")
async def company_history(
    company: str = Query(..., min_length=1),
    user: AuthenticatedUser = Depends(require_authenticated_user),
) -> Dict:
    return {"history": _history_payload(company, organization_id=user.organization_id)}


@router.get("/history/overview")
async def history_overview(
    companies: str = Query(default=""),
    user: AuthenticatedUser = Depends(require_authenticated_user),
) -> Dict:
    requested = [item.strip() for item in companies.split(",") if item.strip()]
    if not requested:
        payload = load_competitors_for_organization(organization_id=user.organization_id)
        requested = [
            str(item.get("name", "")).strip()
            for item in payload.get("competitors", [])
            if str(item.get("name", "")).strip()
        ]
    return {"overview": _history_overview_payload(requested[:6], organization_id=user.organization_id)}
