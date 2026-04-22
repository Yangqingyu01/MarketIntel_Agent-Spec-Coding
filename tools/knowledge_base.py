"""Persistence helpers for competitor config, vector memory, snapshots, and alert history."""

from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import chromadb
except Exception:  # pragma: no cover
    chromadb = None

from config import config
from tools.report_builder import current_date, utc_now_iso


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
            dimension TEXT,
            severity TEXT,
            title TEXT,
            description TEXT NOT NULL,
            recommended_actions TEXT,
            dedup_key TEXT,
            source_url TEXT,
            detected_at TEXT NOT NULL
        )
        """
    )
    existing_columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(alert_history)").fetchall()
    }
    expected_columns = {
        "dimension": "TEXT",
        "severity": "TEXT",
        "title": "TEXT",
        "recommended_actions": "TEXT",
        "dedup_key": "TEXT",
        "source_url": "TEXT",
    }
    for column, column_type in expected_columns.items():
        if column not in existing_columns:
            connection.execute(
                "ALTER TABLE alert_history ADD COLUMN {column} {column_type}".format(
                    column=column,
                    column_type=column_type,
                )
            )
    connection.commit()
    return connection


def initialize_storage() -> None:
    """Ensure local persistence backends exist for first-run startup."""
    config.vector_store_path.mkdir(parents=True, exist_ok=True)
    config.intel_history_path.mkdir(parents=True, exist_ok=True)
    config.config_path.parent.mkdir(parents=True, exist_ok=True)
    config.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
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
    record_type = intel.get("record_type", "intel")
    doc_id = (
        f"{record_type}_"
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
                "record_type": record_type,
            }
        ],
    )


def _sanitize_filename(value: str) -> str:
    return re.sub(r'[\\/:*?"<>|]+', "_", value).strip() or "unknown"


def _snapshot_dir() -> Path:
    path = config.intel_history_path / "snapshots"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _serialize_snapshot_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    serialized = []
    for item in items:
        serialized.append(
            {
                "company": item.get("company", ""),
                "dimension": item.get("dimension", "unknown"),
                "content_type": item.get("content_type", ""),
                "credibility": float(item.get("credibility", 0.0)),
                "extracted_data": item.get("extracted_data", ""),
                "evidence_quote": item.get("evidence_quote", ""),
                "source_url": item.get("source_url", ""),
                "source_name": item.get("source_name", ""),
                "publish_date": item.get("publish_date", ""),
                "crawl_date": item.get("crawl_date", current_date()),
            }
        )
    return serialized


def save_snapshot(company: str, items: List[Dict[str, Any]]) -> None:
    """Persist a baseline snapshot to local JSON for later retrieval."""
    if not items:
        return
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    serialized_items = _serialize_snapshot_items(items)
    payload = {
        "snapshot_id": "SNP-{company}-{timestamp}".format(
            company=_sanitize_filename(company),
            timestamp=timestamp,
        ),
        "company": company,
        "snapshot_date": utc_now_iso(),
        "baseline_status": "cold_start",
        "dimensions": sorted(
            {item.get("dimension", "unknown") for item in serialized_items}
        ),
        "overall_confidence": max(
            float(item.get("credibility", 0.0)) for item in serialized_items
        ),
        "source_count": len(serialized_items),
        "items": serialized_items,
    }
    snapshot_path = _snapshot_dir() / "{company}_{timestamp}.json".format(
        company=_sanitize_filename(company),
        timestamp=timestamp,
    )
    snapshot_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
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
    snapshot_files = sorted(
        _snapshot_dir().glob("{company}_*.json".format(company=_sanitize_filename(company))),
        reverse=True,
    )
    if not snapshot_files:
        return None
    try:
        return json.loads(snapshot_files[0].read_text(encoding="utf-8"))
    except Exception:
        return None


def record_alert(alert: Dict[str, Any]) -> None:
    connection = _connect_sqlite()
    connection.execute(
        """
        INSERT OR REPLACE INTO alert_history (
            alert_id,
            company,
            change_type,
            dimension,
            severity,
            title,
            description,
            recommended_actions,
            dedup_key,
            source_url,
            detected_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            alert.get("alert_id"),
            alert.get("company", ""),
            alert.get("change_type", ""),
            alert.get("dimension", ""),
            alert.get("severity", ""),
            alert.get("title", ""),
            alert.get("description", ""),
            json.dumps(alert.get("recommended_actions", []), ensure_ascii=False),
            alert.get("dedup_key", ""),
            alert.get("source_url", ""),
            alert.get("detected_at", current_date()),
        ),
    )
    connection.commit()
    connection.close()


def find_similar_alert(
    company: str,
    change_type: str,
    dimension: str,
    dedup_key: str,
    days: int = 30,
) -> Optional[Dict[str, Any]]:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).replace(
        microsecond=0
    ).isoformat()
    connection = _connect_sqlite()
    row = connection.execute(
        """
        SELECT * FROM alert_history
        WHERE company = ? AND change_type = ? AND dimension = ? AND dedup_key = ? AND detected_at >= ?
        ORDER BY detected_at DESC
        LIMIT 1
        """,
        (company, change_type, dimension, dedup_key, cutoff),
    ).fetchone()
    connection.close()
    if row is None:
        return None
    payload = dict(row)
    try:
        payload["recommended_actions"] = json.loads(
            payload.get("recommended_actions") or "[]"
        )
    except Exception:
        payload["recommended_actions"] = []
    return payload


def list_recent_alerts(limit: int = 20) -> List[Dict[str, Any]]:
    connection = _connect_sqlite()
    rows = connection.execute(
        """
        SELECT * FROM alert_history
        ORDER BY detected_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    connection.close()
    alerts = []
    for row in rows:
        payload = dict(row)
        try:
            payload["recommended_actions"] = json.loads(
                payload.get("recommended_actions") or "[]"
            )
        except Exception:
            payload["recommended_actions"] = []
        alerts.append(payload)
    return alerts
