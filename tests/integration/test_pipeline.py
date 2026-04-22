from __future__ import annotations

from pathlib import Path


def test_pipeline_modules_exist() -> None:
    assert Path("tools/web_search.py").exists()
    assert Path("tools/web_fetcher.py").exists()
    assert Path("tools/data_extractor.py").exists()
    assert Path("tools/knowledge_base.py").exists()
