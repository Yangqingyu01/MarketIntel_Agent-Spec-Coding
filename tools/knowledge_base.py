"""Persistence helpers for competitor config, vector memory, and alert history."""

from __future__ import annotations

import json
import sqlite3
from typing import Any, Dict, List, Optional

try:
    import chromadb
except Exception:  # pragma: no cover
    chromadb = None

from config import config
from tools.report_builder import current_date


_client = None
_collection = None


def _connect_sqlite() -> sqlite3.Connection:
    connection = sqlite3.connect(config.sqlite_path)
    connection.row_factory = sqlite3.Row
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS alert_history (
            alert_id TEXT PRIMARY KEY,
            company TEXT NOT NULL,
            change_type TEXT NOT NULL,
            description TEXT NOT NULL,
            detected_at TEXT NOT NULL
        )
        """
    )
    connection.commit()
    return connection


def initialize_storage() -> None:
    """Ensure local persistence backends exist for first-run startup."""
    _connect_sqlite().close()
    if not config.config_path.exists():
        config.config_path.write_text(
            json.dumps({"competitors": []}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def _get_collection():
    global _client, _collection
    if chromadb is None:
        return None
    if _collection is None:
        _client = chromadb.PersistentClient(path=str(config.vector_store_path))
        _collection = _client.get_or_create_collection(name="intel_store")
    return _collection


def load_competitors() -> Dict[str, Any]:
    initialize_storage()
    if not config.config_path.exists():
        return {"competitors": []}
    return json.loads(config.config_path.read_text(encoding="utf-8"))


def save_competitor(competitor: Dict[str, Any]) -> Dict[str, Any]:
    payload = load_competitors()
    payload.setdefault("competitors", []).append(competitor)
    config.config_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return payload


def save_intel(intel: Dict[str, Any], raw_content: str) -> None:
    collection = _get_collection()
    if collection is None:
        return
    doc_id = (
        f"{intel.get('company', 'unknown')}_"
        f"{intel.get('dimension', 'unknown')}_"
        f"{intel.get('crawl_date', current_date())}_"
        f"{abs(hash(intel.get('source_url', raw_content))) % 100000}"
    )
    collection.upsert(
        ids=[doc_id],
        documents=[raw_content or intel.get("evidence_quote", "")],
        metadatas=[
            {
                "company": intel.get("company", ""),
                "dimension": intel.get("dimension", ""),
                "content_type": intel.get("content_type", ""),
                "credibility": float(intel.get("credibility", 0.0)),
                "source_url": intel.get("source_url", ""),
                "crawl_date": intel.get("crawl_date", current_date()),
                "extracted_data": intel.get("extracted_data", ""),
            }
        ],
    )


def save_snapshot(company: str, items: List[Dict[str, Any]]) -> None:
    """Persist a synthetic baseline snapshot document for later retrieval."""
    if not items:
        return
    summary_lines = []
    for item in items[:10]:
        summary_lines.append(
            "{dimension}: {summary}".format(
                dimension=item.get("dimension", "unknown"),
                summary=item.get("extracted_data", ""),
            )
        )
    save_intel(
        {
            "company": company,
            "dimension": "product",
            "content_type": "fact",
            "credibility": max(float(item.get("credibility", 0.0)) for item in items),
            "source_url": items[0].get("source_url", ""),
            "crawl_date": current_date(),
            "extracted_data": " | ".join(summary_lines[:3]),
        },
        "\n".join(summary_lines),
    )


def search_history(company: str, dimension: Optional[str] = None, n: int = 5) -> List[Dict]:
    collection = _get_collection()
    if collection is None:
        return []
    where: Dict[str, Any] = {"company": company}
    if dimension:
        where["dimension"] = dimension
    count = collection.count()
    if count == 0:
        return []
    results = collection.query(
        query_texts=[f"{company} {dimension or '情报'}"],
        n_results=min(n, count),
        where=where,
    )
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    return [{"content": doc, "metadata": meta} for doc, meta in zip(docs, metas)]


def get_latest_snapshot(company: str) -> Optional[Dict[str, Any]]:
    results = search_history(company, n=10)
    if not results:
        return None
    return sorted(
        results,
        key=lambda item: item["metadata"].get("crawl_date", ""),
        reverse=True,
    )[0]


def record_alert(alert: Dict[str, Any]) -> None:
    connection = _connect_sqlite()
    connection.execute(
        """
        INSERT OR REPLACE INTO alert_history (alert_id, company, change_type, description, detected_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            alert.get("alert_id"),
            alert.get("company", ""),
            alert.get("change_type", ""),
            alert.get("description", ""),
            alert.get("detected_at", current_date()),
        ),
    )
    connection.commit()
    connection.close()


def find_similar_alert(
    company: str, change_type: str, description: str
) -> Optional[Dict[str, Any]]:
    connection = _connect_sqlite()
    row = connection.execute(
        """
        SELECT * FROM alert_history
        WHERE company = ? AND change_type = ?
        ORDER BY detected_at DESC
        LIMIT 1
        """,
        (company, change_type),
    ).fetchone()
    connection.close()
    if row is None:
        return None
    return dict(row)
