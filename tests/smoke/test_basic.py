from __future__ import annotations

from pathlib import Path

from storage.client import StorageClient


def test_storage_client_initializes_without_side_effects() -> None:
    client = StorageClient(Path("."))
    assert client.base_path.exists()
    assert client.vector_store_path.name == "vector_store"
    assert client.history_path.name == "intel_history"


def test_project_core_files_exist() -> None:
    assert Path("config.py").exists()
    assert Path("main.py").exists()
    assert Path("storage/client.py").exists()
