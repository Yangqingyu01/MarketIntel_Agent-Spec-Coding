from __future__ import annotations

from agents.analysis_agent import analyze_results


def test_analyze_results_preserves_requested_dimension() -> None:
    search_results = [
        {
            "dimension": "strategy",
            "title": "Feishu MCP update",
            "url": "https://example.com/feishu-strategy",
            "source_name": "example.com",
            "source_type": "official",
            "publish_date": "2026-04-20",
            "crawl_date": "2026-04-23",
            "content": "飞书推出 MCP Server，进一步强化 AI 工作流生态布局。",
            "fallback_used": False,
            "degradation_note": "",
            "compliance_note": "",
        }
    ]

    analysis_results, _ = analyze_results("Feishu", search_results)

    assert len(analysis_results) == 1
    assert analysis_results[0]["dimension"] == "strategy"
