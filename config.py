"""Central application configuration and client factories."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


def _fallback_env(primary: str, secondary: str, default: str = "") -> str:
    return os.getenv(primary) or os.getenv(secondary) or default


@dataclass(slots=True)
class AppConfig:
    repo_root: Path = field(default_factory=lambda: Path(__file__).resolve().parent)

    llm_api_key: str = field(default_factory=lambda: os.getenv("LLM_API_KEY", ""))
    llm_base_url: str = field(
        default_factory=lambda: os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    )
    llm_model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "gpt-4o-mini"))
    llm_model_strong: str = field(
        default_factory=lambda: os.getenv("LLM_MODEL_STRONG", "gpt-4o")
    )

    embedding_api_key: str = field(
        default_factory=lambda: _fallback_env("EMBEDDING_API_KEY", "LLM_API_KEY")
    )
    embedding_base_url: str = field(
        default_factory=lambda: _fallback_env(
            "EMBEDDING_BASE_URL", "LLM_BASE_URL", "https://api.openai.com/v1"
        )
    )
    embedding_model: str = field(
        default_factory=lambda: os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    )

    serper_api_key: str = field(default_factory=lambda: os.getenv("SERPER_API_KEY", ""))
    tavily_api_key: str = field(default_factory=lambda: os.getenv("TAVILY_API_KEY", ""))

    vector_store_path: Path = field(
        default_factory=lambda: Path("data/vector_store").resolve()
    )
    intel_history_path: Path = field(
        default_factory=lambda: Path("data/intel_history").resolve()
    )
    sqlite_path: Path = field(default_factory=lambda: Path("data/intel.db").resolve())
    config_path: Path = field(
        default_factory=lambda: Path("data/config/competitors.json").resolve()
    )

    feishu_app_id: str = field(default_factory=lambda: os.getenv("FEISHU_APP_ID", ""))
    feishu_app_secret: str = field(
        default_factory=lambda: os.getenv("FEISHU_APP_SECRET", "")
    )
    feishu_target_chat_id: str = field(
        default_factory=lambda: os.getenv("FEISHU_TARGET_CHAT_ID", "")
    )

    analysis_timeout_seconds: int = field(
        default_factory=lambda: int(os.getenv("ANALYSIS_TIMEOUT_SECONDS", "90"))
    )
    fetch_timeout_seconds: int = field(
        default_factory=lambda: int(os.getenv("FETCH_TIMEOUT_SECONDS", "10"))
    )
    default_time_range: str = "近3个月"
    default_dimensions: tuple[str, ...] = (
        "product",
        "pricing",
        "funding",
        "talent",
        "strategy",
    )

    def ensure_directories(self) -> None:
        self.vector_store_path.mkdir(parents=True, exist_ok=True)
        self.intel_history_path.mkdir(parents=True, exist_ok=True)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)


config = AppConfig()
config.ensure_directories()


def create_openai_client(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> OpenAI:
    return OpenAI(
        api_key=api_key or config.llm_api_key,
        base_url=base_url or config.llm_base_url,
    )


llm_client = create_openai_client()
embedding_client = create_openai_client(
    api_key=config.embedding_api_key,
    base_url=config.embedding_base_url,
)
