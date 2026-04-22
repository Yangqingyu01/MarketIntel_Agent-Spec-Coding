from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from config import config
from main import app
from tools import knowledge_base


def test_end_to_end_analysis_alert_and_health(monkeypatch, tmp_path: Path) -> None:
    config.sqlite_path = tmp_path / "intel.db"
    config.intel_history_path = tmp_path / "intel_history"
    config.config_path = tmp_path / "config" / "competitors.json"
    config.vector_store_path = tmp_path / "vector_store"
    knowledge_base._client = None
    knowledge_base._collection = None
    knowledge_base.initialize_storage()

    states = [
        [
            {
                "dimension": "product",
                "title": "飞书协作功能更新",
                "url": "https://example.com/%E9%A3%9E%E4%B9%A6/product-update",
                "source_name": "example.com",
                "source_type": "mock_public_source",
                "publish_date": "2026-04-20",
                "crawl_date": "2026-04-20",
                "content": "飞书 发布基础协作功能 2026-04-20",
                "full_text_available": True,
                "initial_relevance": 0.9,
                "time_range": "近3个月",
            }
        ],
        [
            {
                "dimension": "product",
                "title": "飞书AI纪要能力上线",
                "url": "https://example.com/%E9%A3%9E%E4%B9%A6/product-update",
                "source_name": "example.com",
                "source_type": "mock_public_source",
                "publish_date": "2026-04-22",
                "crawl_date": "2026-04-22",
                "content": "飞书 发布全新AI纪要功能 2026-04-22",
                "full_text_available": True,
                "initial_relevance": 0.9,
                "time_range": "近3个月",
            }
        ],
    ]

    def fake_run_search(target, dimensions, time_range):
        del target
        del dimensions
        del time_range
        return states.pop(0)

    monkeypatch.setattr("agents.orchestrator.run_search", fake_run_search)

    client = TestClient(app)
    first = client.post(
        "/api/analyze",
        json={"targets": ["飞书"], "dimensions": ["product"], "time_range": "近3个月"},
    )
    second = client.post(
        "/api/analyze",
        json={"targets": ["飞书"], "dimensions": ["product"], "time_range": "近3个月"},
    )
    alerts = client.get("/api/alerts")
    health = client.get("/health")

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["alerts"]
    assert alerts.status_code == 200
    assert alerts.json()["alerts"]
    assert health.status_code == 200
    assert health.json()["scheduler"]["enabled"] in {True, False}
