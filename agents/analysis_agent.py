"""Analysis agent for extraction, credibility scoring, and baseline lookup."""

from __future__ import annotations

from typing import Any

from tools.data_extractor import extract_intel
from tools.knowledge_base import get_latest_snapshot
from tools.report_builder import current_date


SOURCE_BASE_SCORE = {
    "official": 0.90,
    "authoritative_media": 0.75,
    "search_result": 0.60,
    "community": 0.30,
}


def score_item(item: dict[str, Any], extracted: dict[str, Any]) -> float:
    base = SOURCE_BASE_SCORE.get(item.get("source_type", "search_result"), 0.52)
    publish_date = item.get("publish_date", "")
    recency_penalty = 0.0 if publish_date else 0.05
    score = max(0.0, min(1.0, base - recency_penalty))
    return round(score, 2)


def analyze_results(
    target: str, search_results: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    analysis_results: list[dict[str, Any]] = []
    for item in search_results:
        extracted = extract_intel(item.get("content", ""), target)
        if not extracted:
            continue
        extracted["credibility"] = score_item(item, extracted)
        extracted["source_url"] = item.get("url", "")
        extracted["source_name"] = item.get("source_name", "")
        extracted["publish_date"] = item.get("publish_date", "")
        extracted["crawl_date"] = item.get("crawl_date", current_date())
        extracted["raw_title"] = item.get("title", "")
        analysis_results.append(extracted)

    baseline = get_latest_snapshot(target)
    return analysis_results, baseline
