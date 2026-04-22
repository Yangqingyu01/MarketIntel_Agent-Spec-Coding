"""Shared state models for the MarketIntel workflow."""

from __future__ import annotations

from typing import Any, Literal, TypedDict


Dimension = Literal["product", "pricing", "funding", "talent", "strategy"]
ContentType = Literal["fact", "inference", "unverified", "noise"]
IntentType = Literal["TYPE_A", "TYPE_B", "TYPE_C", "TYPE_D"]


class SearchResult(TypedDict, total=False):
    dimension: Dimension
    title: str
    url: str
    source_name: str
    source_type: str
    publish_date: str
    crawl_date: str
    content: str
    full_text_available: bool
    initial_relevance: float


class IntelligenceItem(TypedDict, total=False):
    company: str
    dimension: Dimension
    content_type: ContentType
    extracted_data: str
    evidence_quote: str
    credibility: float
    entities: dict[str, list[str]]
    source_url: str
    source_name: str
    publish_date: str
    crawl_date: str
    raw_title: str


class AlertItem(TypedDict, total=False):
    alert_id: str
    severity: Literal["high", "medium", "low"]
    company: str
    change_type: str
    dimension: Dimension
    title: str
    description: str
    detected_at: str
    recommended_actions: list[dict[str, str]]


class IntelState(TypedDict, total=False):
    query: str
    task_id: str
    intent_type: IntentType
    targets: list[str]
    dimensions: list[Dimension]
    time_range: str
    output_format: Literal["web", "feishu", "summary"]
    search_results: list[SearchResult]
    analysis_results: list[IntelligenceItem]
    alerts: list[AlertItem]
    report: dict[str, Any]
    error: str
