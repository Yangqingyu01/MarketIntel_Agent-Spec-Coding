from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from main import app
from config import config
from tools import knowledge_base
from tools.knowledge_base import record_alert
from tools.report_builder import utc_now_iso


def test_alerts_api_returns_contract_shape(tmp_path: Path) -> None:
    config.sqlite_path = tmp_path / "intel.db"
    config.intel_history_path = tmp_path / "intel_history"
    config.config_path = tmp_path / "config" / "competitors.json"
    config.vector_store_path = tmp_path / "vector_store"
    knowledge_base._client = None
    knowledge_base._collection = None
    knowledge_base.initialize_storage()

    record_alert(
        {
            "alert_id": "ALT-1",
            "company": "飞书",
            "change_type": "updated",
            "dimension": "product",
            "severity": "high",
            "title": "飞书 product change detected",
            "description": "飞书 appeared to have a new product signal: AI 会议纪要",
            "recommended_actions": [{"department": "product", "action": "Review the change"}],
            "dedup_key": "feishu|product|updated|ai-note",
            "source_url": "https://example.com/%E9%A3%9E%E4%B9%A6/product-update",
            "detected_at": utc_now_iso(),
        }
    )

    client = TestClient(app)
    response = client.get("/api/alerts")
    assert response.status_code == 200
    payload = response.json()
    assert "alerts" in payload
    assert len(payload["alerts"]) == 1
    alert = payload["alerts"][0]
    assert {
        "alert_id",
        "severity",
        "company",
        "change_type",
        "dimension",
        "title",
        "description",
        "detected_at",
        "recommended_actions",
    } <= set(alert)

