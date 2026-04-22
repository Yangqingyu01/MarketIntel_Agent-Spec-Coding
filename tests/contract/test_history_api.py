from __future__ import annotations

from fastapi.testclient import TestClient

from main import app
from tests.contract.auth_helpers import build_auth_headers


def test_history_api_returns_snapshot_timeline_and_alerts() -> None:
    client = TestClient(app)
    headers = build_auth_headers(client)
    response = client.get("/api/history?company=Feishu", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert "history" in payload
    history = payload["history"]
    assert {"company", "snapshots", "timeline", "comparisons", "alerts"} <= set(history)


def test_history_overview_api_returns_rows() -> None:
    client = TestClient(app)
    headers = build_auth_headers(client)
    response = client.get("/api/history/overview?companies=Feishu", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert "overview" in payload
    overview = payload["overview"]
    assert {"companies", "rows"} <= set(overview)
