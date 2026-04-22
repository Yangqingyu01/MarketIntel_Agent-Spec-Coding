from __future__ import annotations

from fastapi.testclient import TestClient

from main import app
from tests.contract.auth_helpers import build_auth_headers


def test_scheduler_and_feishu_status_endpoints_return_shape() -> None:
    client = TestClient(app)
    headers = build_auth_headers(client)

    scheduler_response = client.get("/api/scheduler/status", headers=headers)
    assert scheduler_response.status_code == 200
    scheduler_payload = scheduler_response.json()
    assert {"scheduler", "competitor_count", "frequency_counts"} <= set(
        scheduler_payload
    )

    summary_response = client.get("/api/scheduler/summary?frequency=daily", headers=headers)
    assert summary_response.status_code == 200
    summary_payload = summary_response.json()
    assert "summary" in summary_payload

    feishu_response = client.get("/api/feishu/status")
    assert feishu_response.status_code == 200
    feishu_payload = feishu_response.json()
    assert {
        "configured",
        "delivery_mode",
        "webhook_endpoint",
        "preview_delivery",
    } <= set(feishu_payload)
