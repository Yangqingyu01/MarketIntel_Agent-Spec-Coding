from __future__ import annotations

import pytest

from config import config


@pytest.mark.skipif(
    not (config.serper_api_key or config.tavily_api_key),
    reason="Search API not configured",
)
def test_search_env_present() -> None:
    assert config.serper_api_key or config.tavily_api_key
