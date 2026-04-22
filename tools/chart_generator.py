"""Chart data builders for report and dashboard output."""

from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List


DIMENSION_LABELS = {
    "product": "产品",
    "pricing": "定价",
    "funding": "融资",
    "talent": "人才",
    "strategy": "战略",
}


def build_dimension_comparison(analysis_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    counts = Counter(item.get("dimension", "product") for item in analysis_results)
    return [
        {
            "chart": "dimension_comparison",
            "dimension": dimension,
            "label": DIMENSION_LABELS.get(dimension, dimension),
            "count": count,
        }
        for dimension, count in sorted(counts.items())
    ]


def build_timeline_chart(analysis_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    timeline = Counter(item.get("crawl_date", "") for item in analysis_results if item.get("crawl_date"))
    return [
        {"chart": "timeline", "date": date, "count": count}
        for date, count in sorted(timeline.items())
    ]


def build_report_charts(analysis_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return build_dimension_comparison(analysis_results) + build_timeline_chart(analysis_results)
