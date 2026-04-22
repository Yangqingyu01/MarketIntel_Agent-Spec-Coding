from __future__ import annotations

import pytest

from config import config


@pytest.mark.skipif(not config.llm_api_key, reason="LLM API key not configured")
def test_llm_env_present() -> None:
    assert config.llm_api_key
