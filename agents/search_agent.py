"""Search agent implementation for public-source market intelligence."""

from __future__ import annotations

from datetime import date
from typing import Dict, Iterable, List, Tuple

from tools.web_fetcher import fetch
from tools.web_search import search


DIMENSION_QUERY_TEMPLATES = {
    "product": ["{company} 新功能 发布 {year}", "{company} product launch {year}"],
    "pricing": ["{company} 定价 价格 调整", "{company} pricing update"],
    "funding": ["{company} 融资 {year}", "{company} funding round {year}"],
    "talent": ["{company} 高管 任命 离职 {year}", "{company} 招聘 {year} 方向"],
    "strategy": ["{company} 战略 合作 {year}", "{company} 海外 扩张 {year}"],
}


def build_queries(company: str, dimensions: Iterable[str]) -> List[Tuple[str, str]]:
    year = str(date.today().year)
    queries: List[Tuple[str, str]] = []
    for dimension in dimensions:
        for template in DIMENSION_QUERY_TEMPLATES.get(dimension, []):
            queries.append((dimension, template.format(company=company, year=year)))
    return queries


def run_search(target: str, dimensions: List[str], time_range: str) -> List[Dict]:
    """Search and optionally fetch high-value sources."""
    collected: List[Dict] = []
    for dimension, query in build_queries(target, dimensions):
        for item in search(query, num=3):
            fetched = fetch(item["url"])
            content = fetched["content"] if fetched["success"] else item.get("snippet", "")
            degradation_messages = []
            if item.get("degradation_note"):
                degradation_messages.append(item["degradation_note"])
            if fetched.get("degradation_note"):
                degradation_messages.append(fetched["degradation_note"])
            collected.append(
                {
                    "dimension": dimension,
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "source_name": item.get("source_name", ""),
                    "source_type": item.get("source_type", "search_result"),
                    "publish_date": item.get("date", ""),
                    "crawl_date": item.get("crawl_date", date.today().isoformat()),
                    "content": content,
                    "full_text_available": fetched["success"],
                    "fallback_used": bool(
                        item.get("source_type") == "mock_public_source"
                        or fetched.get("fallback_used")
                        or not fetched["success"]
                    ),
                    "degradation_note": " ".join(degradation_messages),
                    "compliance_note": " ".join(
                        note
                        for note in [
                            item.get("compliance_note", ""),
                            fetched.get("compliance_note", ""),
                        ]
                        if note
                    ),
                    "initial_relevance": 0.9 if target in item.get("title", "") else 0.6,
                    "time_range": time_range,
                }
            )
    return collected
