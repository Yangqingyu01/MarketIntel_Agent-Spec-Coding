"""Analysis agent for extraction, credibility scoring, baseline lookup, and change detection."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from tools.data_extractor import extract_intel
from tools.knowledge_base import get_latest_snapshot
from tools.report_builder import current_date


SOURCE_BASE_SCORE = {
    "official": 0.90,
    "authoritative_media": 0.75,
    "search_result": 0.60,
    "community": 0.30,
}


def score_item(item: Dict[str, Any], extracted: Dict[str, Any]) -> float:
    base = SOURCE_BASE_SCORE.get(item.get("source_type", "search_result"), 0.52)
    publish_date = item.get("publish_date", "")
    recency_penalty = 0.0 if publish_date else 0.05
    score = max(0.0, min(1.0, base - recency_penalty))
    return round(score, 2)


def analyze_results(
    target: str,
    search_results: List[Dict[str, Any]],
    organization_id: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
    analysis_results: List[Dict[str, Any]] = []
    seen_signatures = set()
    for item in search_results:
        extracted = extract_intel(item.get("content", ""), target)
        if not extracted:
            continue
        signature = (
            extracted.get("dimension", ""),
            extracted.get("extracted_data", ""),
            item.get("url", ""),
        )
        if signature in seen_signatures:
            continue
        seen_signatures.add(signature)
        extracted["credibility"] = score_item(item, extracted)
        extracted["source_url"] = item.get("url", "")
        extracted["source_name"] = item.get("source_name", "")
        extracted["source_type"] = item.get("source_type", "search_result")
        extracted["publish_date"] = item.get("publish_date", "")
        extracted["crawl_date"] = item.get("crawl_date", current_date())
        extracted["raw_title"] = item.get("title", "")
        extracted["fallback_used"] = bool(item.get("fallback_used", False))
        extracted["degradation_note"] = item.get("degradation_note", "")
        extracted["compliance_note"] = item.get("compliance_note", "")
        analysis_results.append(extracted)

    baseline = get_latest_snapshot(target, organization_id=organization_id)
    return analysis_results, baseline


def build_change_events(
    target: str,
    analysis_results: List[Dict[str, Any]],
    baseline: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Compare the current run with the latest baseline snapshot."""
    if not baseline:
        return []

    baseline_items = baseline.get("items", []) if isinstance(baseline, dict) else []
    baseline_signatures = {
        (
            item.get("dimension", "unknown"),
            item.get("extracted_data", ""),
        )
        for item in baseline_items
    }
    baseline_dimensions = {
        item.get("dimension", "unknown")
        for item in baseline_items
        if item.get("dimension")
    }

    change_events: List[Dict[str, Any]] = []
    seen_signatures = set()
    for item in analysis_results:
        if float(item.get("credibility", 0.0)) < 0.40:
            continue
        signature = (
            item.get("dimension", "unknown"),
            item.get("extracted_data", ""),
        )
        if signature in baseline_signatures or signature in seen_signatures:
            continue
        seen_signatures.add(signature)
        dimension = item.get("dimension", "unknown")
        change_type = "updated" if dimension in baseline_dimensions else "new_signal"
        change_events.append(
            {
                "change_id": "CHG-{company}-{dimension}-{index}".format(
                    company=target,
                    dimension=dimension,
                    index=len(change_events) + 1,
                ),
                "company": target,
                "dimension": dimension,
                "change_type": change_type,
                "description": "{company} 在 {dimension} 维度出现新的公开信号：{summary}".format(
                    company=target,
                    dimension=dimension,
                    summary=item.get("extracted_data", ""),
                ),
                "severity_candidate": "high" if change_type == "updated" else "medium",
                "credibility": float(item.get("credibility", 0.0)),
                "source_url": item.get("source_url", ""),
                "detected_at": item.get("crawl_date", current_date()),
            }
        )
    return change_events
