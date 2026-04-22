from __future__ import annotations

from agents import search_agent


def test_run_search_respects_query_and_fetch_budget(monkeypatch) -> None:
    monkeypatch.setattr(search_agent.config, "max_queries_per_dimension", 1)
    monkeypatch.setattr(search_agent.config, "search_results_per_query", 2)
    monkeypatch.setattr(search_agent.config, "max_fetch_documents_per_target", 2)

    fetch_calls = []

    def fake_search(query: str, num: int):
        return [
            {
                "title": f"{query}-{index}",
                "url": f"https://example.com/result-{index}",
                "snippet": "Feishu launched a new collaboration feature.",
                "source_name": "example.com",
                "source_type": "search_result",
                "date": "2026-04-22",
                "crawl_date": "2026-04-22",
            }
            for index in range(num)
        ]

    def fake_fetch(url: str):
        fetch_calls.append(url)
        return {
            "url": url,
            "content": "Feishu launched a new collaboration feature.",
            "success": True,
            "error": "",
            "fallback_used": False,
            "compliance_note": "",
        }

    monkeypatch.setattr(search_agent, "search", fake_search)
    monkeypatch.setattr(search_agent, "fetch", fake_fetch)

    results = search_agent.run_search(
        "Feishu",
        dimensions=["product", "pricing"],
        time_range="last 3 months",
    )

    assert len(results) == 4
    assert len(fetch_calls) == 2
    assert results[0]["full_text_available"] is True
    assert results[-1]["full_text_available"] is False
    assert results[-1]["content"] == "Feishu launched a new collaboration feature."
