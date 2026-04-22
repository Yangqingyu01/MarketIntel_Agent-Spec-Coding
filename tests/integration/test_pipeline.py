from __future__ import annotations

from typing import Any, Dict, List

from agents.analysis_agent import analyze_results
from agents.search_agent import run_search
from tools.knowledge_base import save_intel, save_snapshot


def run_pipeline(company: str, dimensions: List[str]) -> Dict[str, Any]:
    """Scriptable local MVP runner for the search -> analyze -> persist chain."""
    search_results = run_search(company, dimensions, "近3个月")
    analysis_results, baseline = analyze_results(company, search_results)
    for item in analysis_results:
        save_intel(item, item.get("evidence_quote", ""))
    save_snapshot(company, analysis_results)
    return {
        "company": company,
        "search_results": search_results,
        "analysis_results": analysis_results,
        "baseline": baseline,
    }


def test_pipeline_runner_returns_structured_results() -> None:
    result = run_pipeline("飞书", ["product", "pricing"])
    assert result["search_results"]
    assert result["analysis_results"]
    assert result["analysis_results"][0]["source_url"]


if __name__ == "__main__":
    payload = run_pipeline("飞书", ["product", "pricing", "strategy"])
    print(
        "Pipeline complete:",
        len(payload["search_results"]),
        len(payload["analysis_results"]),
    )
