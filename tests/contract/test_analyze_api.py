from __future__ import annotations

from fastapi.testclient import TestClient

from main import app


def test_analyze_api_returns_contract_shape() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/analyze",
        json={"targets": ["飞书"], "dimensions": ["product"], "time_range": "近3个月"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert {"task_id", "report", "alerts", "intel_count"} <= set(payload)
    assert payload["report"]["report_type"] == "single"
    assert payload["intel_count"] >= 1
