from __future__ import annotations

from fastapi.testclient import TestClient

from main import app
from tests.contract.auth_helpers import build_auth_headers


def test_analyze_api_returns_contract_shape() -> None:
    client = TestClient(app)
    headers = build_auth_headers(client)
    response = client.post(
        "/api/analyze",
        json={"targets": ["Feishu"], "dimensions": ["product"], "time_range": "recent"},
        headers=headers,
    )
    assert response.status_code == 200
    payload = response.json()
    assert {"task_id", "report", "alerts", "intel_count"} <= set(payload)
    assert payload["report"]["report_type"] == "single"
    assert payload["intel_count"] >= 0
