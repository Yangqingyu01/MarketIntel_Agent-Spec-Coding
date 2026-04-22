from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient


def build_auth_headers(client: TestClient) -> dict[str, str]:
    unique = uuid4().hex[:8]
    email = f"contract-{unique}@example.com"
    response = client.post(
        "/api/auth/register",
        json={
            "organization_name": f"Contract Org {unique}",
            "full_name": "Contract User",
            "email": email,
            "password": "demo123",
        },
    )
    payload = response.json()
    return {"Authorization": f"Bearer {payload['access_token']}"}

