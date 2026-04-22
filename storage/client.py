"""Minimal storage client that is safe to initialize without side effects."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class StorageClient:
    """Lightweight local storage client.

    Initialization is intentionally side-effect free:
    it only stores resolved paths and does not open databases,
    create network connections, or call external services.
    """

    base_path: Path
    vector_store_path: Optional[Path] = None
    history_path: Optional[Path] = None
    config_path: Optional[Path] = None

    def __post_init__(self) -> None:
        self.base_path = Path(self.base_path).resolve()
        if self.vector_store_path is None:
            self.vector_store_path = self.base_path / "data" / "vector_store"
        else:
            self.vector_store_path = Path(self.vector_store_path).resolve()

        if self.history_path is None:
            self.history_path = self.base_path / "data" / "intel_history"
        else:
            self.history_path = Path(self.history_path).resolve()

        if self.config_path is None:
            self.config_path = self.base_path / "data" / "config" / "competitors.json"
        else:
            self.config_path = Path(self.config_path).resolve()
