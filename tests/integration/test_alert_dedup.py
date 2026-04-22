from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from agents.orchestrator import run_analysis
from config import config
from tools import knowledge_base
from tools.knowledge_base import list_recent_alerts


def test_change_detection_and_dedup_flow(
    monkeypatch,
    tmp_path: Path,
) -> None:
    config.sqlite_path = tmp_path / "intel.db"
    config.intel_history_path = tmp_path / "intel_history"
    config.config_path = tmp_path / "config" / "competitors.json"
    config.vector_store_path = tmp_path / "vector_store"
    knowledge_base._client = None
    knowledge_base._collection = None
    knowledge_base.initialize_storage()

    runs: List[List[Dict[str, str]]] = [
        [
            {
                "dimension": "product",
                "title": "钉钉 协作功能更新",
                "url": "https://example.com/%E9%92%89%E9%92%89/product-update",
                "source_name": "example.com",
                "source_type": "official",
                "publish_date": "2026-04-20",
                "crawl_date": "2026-04-20",
                "content": "钉钉 发布基础协作功能 2026-04-20",
                "full_text_available": True,
                "initial_relevance": 0.9,
                "time_range": "近3个月",
            }
        ],
        [
            {
                "dimension": "product",
                "title": "钉钉 AI 纪要能力上线",
                "url": "https://example.com/%E9%92%89%E9%92%89/product-update",
                "source_name": "example.com",
                "source_type": "official",
                "publish_date": "2026-04-22",
                "crawl_date": "2026-04-22",
                "content": "钉钉 发布全新AI纪要功能 2026-04-22",
                "full_text_available": True,
                "initial_relevance": 0.9,
                "time_range": "近3个月",
            }
        ],
        [
            {
                "dimension": "product",
                "title": "钉钉 AI 纪要能力上线",
                "url": "https://example.com/%E9%92%89%E9%92%89/product-update",
                "source_name": "example.com",
                "source_type": "official",
                "publish_date": "2026-04-22",
                "crawl_date": "2026-04-22",
                "content": "钉钉 发布全新AI纪要功能 2026-04-22",
                "full_text_available": True,
                "initial_relevance": 0.9,
                "time_range": "近3个月",
            }
        ],
    ]

    def fake_run_search(target: str, dimensions: List[str], time_range: str) -> List[Dict]:
        del target
        del dimensions
        del time_range
        return runs.pop(0)

    monkeypatch.setattr("agents.orchestrator.run_search", fake_run_search)

    first = run_analysis(["钉钉"], dimensions=["product"])
    second = run_analysis(["钉钉"], dimensions=["product"])
    third = run_analysis(["钉钉"], dimensions=["product"])

    assert first["alerts"] == []
    assert len(second["change_events"]) == 1
    assert len(second["alerts"]) == 1
    assert third["alerts"] == []

    recent_alerts = list_recent_alerts()
    assert len(recent_alerts) == 1
    assert recent_alerts[0]["company"] == "钉钉"
