from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from main import app


def test_auth_register_login_and_me_flow() -> None:
    client = TestClient(app)
    unique = uuid4().hex[:8]
    email = f"demo-{unique}@example.com"

    register_response = client.post(
        "/api/auth/register",
        json={
            "organization_name": f"Demo Org {unique}",
            "full_name": "Demo Presenter",
            "email": email,
            "password": "demo123",
        },
    )
    assert register_response.status_code == 200
    register_payload = register_response.json()
    assert register_payload["token_type"] == "bearer"
    assert register_payload["user"]["organization_name"].startswith("Demo Org")

    login_response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "demo123"},
    )
    assert login_response.status_code == 200
    login_payload = login_response.json()
    assert login_payload["access_token"]

    me_response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {login_payload['access_token']}"},
    )
    assert me_response.status_code == 200
    me_payload = me_response.json()
    assert me_payload["user"]["email"] == email
    assert me_payload["user"]["role"] == "admin"

