from __future__ import annotations

from tools.knowledge_base import load_competitors


def test_config_store_loads() -> None:
    payload = load_competitors()
    assert "competitors" in payload
