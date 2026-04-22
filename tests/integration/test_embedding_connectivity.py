from __future__ import annotations

import pytest

from config import config


@pytest.mark.skipif(not config.embedding_api_key, reason="Embedding API not configured")
def test_embedding_env_present() -> None:
    assert config.embedding_api_key
