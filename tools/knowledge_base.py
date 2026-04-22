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
            organization_id TEXT,
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
        "organization_id": "TEXT",
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
    cleanup_mock_history()


def _get_collection():
    global _client, _collection
    if chromadb is None:
        return None
    if _collection is None:
        _client = chromadb.PersistentClient(path=str(config.vector_store_path))
        _collection = _client.get_or_create_collection(name="intel_store")
    return _collection


def load_competitors() -> Dict[str, Any]:
    return load_competitors_for_organization()


def _load_competitor_registry() -> Dict[str, Any]:
    initialize_storage()
    if not config.config_path.exists():
        return {"competitors": []}
    payload = json.loads(config.config_path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {"competitors": []}


def _write_competitor_registry(payload: Dict[str, Any]) -> None:
    config.config_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_competitors_for_organization(
    organization_id: Optional[str] = None,
) -> Dict[str, Any]:
    payload = _load_competitor_registry()
    if not organization_id:
        if "organizations" not in payload:
            return payload
        competitors = payload.get("organizations", {}).get("public", {}).get("competitors", [])
        return {"competitors": competitors}

    if "organizations" not in payload:
        return {
            "organization_id": organization_id,
            "competitors": payload.get("competitors", []),
        }

    organization_entry = payload.get("organizations", {}).get(organization_id, {})
    return {
        "organization_id": organization_id,
        "competitors": organization_entry.get("competitors", []),
    }


def save_competitor(
    competitor: Dict[str, Any],
    organization_id: Optional[str] = None,
) -> Dict[str, Any]:
    payload = _load_competitor_registry()
    if not organization_id and "organizations" not in payload:
        payload.setdefault("competitors", []).append(competitor)
        _write_competitor_registry(payload)
        return payload

    normalized_org = organization_id or "public"

    if "organizations" not in payload:
        payload = {
            "organizations": {
                normalized_org: {
                    "organization_id": normalized_org,
                    "competitors": payload.get("competitors", []),
                }
            }
        }

    payload.setdefault("organizations", {}).setdefault(
        normalized_org,
        {"organization_id": normalized_org, "competitors": []},
    )
    payload["organizations"][normalized_org].setdefault("competitors", []).append(competitor)
    _write_competitor_registry(payload)
    return {
        "organization_id": normalized_org,
        "competitors": payload["organizations"][normalized_org]["competitors"],
    }


def list_competitor_organization_ids() -> List[str]:
    payload = _load_competitor_registry()
    if "organizations" not in payload:
        return ["public"] if payload.get("competitors") else []
    return [
        organization_id
        for organization_id, entry in payload.get("organizations", {}).items()
        if entry.get("competitors")
    ]


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


def _archive_snapshot_dir() -> Path:
    path = config.intel_history_path / "archived_mock_snapshots"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _archive_alerts_path() -> Path:
    return config.intel_history_path / "archived_mock_alerts.json"


def _is_mock_source_url(source_url: str) -> bool:
    normalized = (source_url or "").strip().lower()
    if not normalized:
        return False
    return (
        "example.com" in normalized
        or "mock" in normalized
        or "mock_public_source" in normalized
    )


def _is_mock_snapshot_payload(payload: Dict[str, Any]) -> bool:
    items = payload.get("items", [])
    if not items:
        return False
    return any(_is_mock_source_url(str(item.get("source_url", ""))) for item in items)


def cleanup_mock_history() -> None:
    for snapshot_path in _snapshot_dir().glob("*.json"):
        try:
            payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not _is_mock_snapshot_payload(payload):
            continue
        snapshot_path.replace(_archive_snapshot_dir() / snapshot_path.name)

    connection = _connect_sqlite()
    rows = connection.execute(
        """
        SELECT * FROM alert_history
        ORDER BY detected_at DESC
        """
    ).fetchall()
    archived_alerts = []
    for row in rows:
        payload = dict(row)
        if not _is_mock_source_url(payload.get("source_url", "")):
            continue
        try:
            payload["recommended_actions"] = json.loads(
                payload.get("recommended_actions") or "[]"
            )
        except Exception:
            payload["recommended_actions"] = []
        archived_alerts.append(payload)

    if archived_alerts:
        archive_path = _archive_alerts_path()
        try:
            existing = json.loads(archive_path.read_text(encoding="utf-8"))
            if not isinstance(existing, list):
                existing = []
        except Exception:
            existing = []
        deduped: Dict[str, Dict[str, Any]] = {
            str(item.get("alert_id", "")): item for item in existing if item.get("alert_id")
        }
        for item in archived_alerts:
            deduped[str(item.get("alert_id", ""))] = item
        archive_path.write_text(
            json.dumps(list(deduped.values()), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        connection.executemany(
            "DELETE FROM alert_history WHERE alert_id = ?",
            [(item.get("alert_id", ""),) for item in archived_alerts],
        )
        connection.commit()

    connection.close()


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


def save_snapshot(
    company: str,
    items: List[Dict[str, Any]],
    organization_id: Optional[str] = None,
) -> None:
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
        "organization_id": organization_id or "public",
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
    snapshot_path = _snapshot_dir() / "{organization}_{company}_{timestamp}.json".format(
        organization=_sanitize_filename(organization_id or "public"),
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


def list_snapshots(
    company: Optional[str] = None,
    limit: int = 10,
    real_only: bool = True,
    organization_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    snapshot_files = sorted(_snapshot_dir().glob("*.json"), reverse=True)
    snapshots: List[Dict[str, Any]] = []
    for path in snapshot_files:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if company and payload.get("company") != company:
            continue
        if organization_id and payload.get("organization_id", "public") != organization_id:
            continue
        if real_only and _is_mock_snapshot_payload(payload):
            continue
        snapshots.append(payload)
        if len(snapshots) >= limit:
            break
    return snapshots


def get_latest_snapshot(
    company: str,
    organization_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    snapshot_files = sorted(_snapshot_dir().glob("*.json"), reverse=True)
    if not snapshot_files:
        return None
    for snapshot_file in snapshot_files:
        try:
            payload = json.loads(snapshot_file.read_text(encoding="utf-8"))
        except Exception:
            continue
        if payload.get("company") != company:
            continue
        if organization_id and payload.get("organization_id", "public") != organization_id:
            continue
        return payload
    return None


def record_alert(alert: Dict[str, Any], organization_id: Optional[str] = None) -> None:
    connection = _connect_sqlite()
    connection.execute(
        """
        INSERT OR REPLACE INTO alert_history (
            alert_id,
            organization_id,
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
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            alert.get("alert_id"),
            organization_id or alert.get("organization_id", "public"),
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
    organization_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).replace(
        microsecond=0
    ).isoformat()
    connection = _connect_sqlite()
    row = connection.execute(
        """
        SELECT * FROM alert_history
        WHERE organization_id = ? AND company = ? AND change_type = ? AND dimension = ? AND dedup_key = ? AND detected_at >= ?
        ORDER BY detected_at DESC
        LIMIT 1
        """,
        (organization_id or "public", company, change_type, dimension, dedup_key, cutoff),
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


def list_recent_alerts(
    limit: int = 20,
    company: Optional[str] = None,
    real_only: bool = True,
    organization_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    connection = _connect_sqlite()
    query_limit = limit * 5 if real_only else limit
    if company:
        rows = connection.execute(
            """
            SELECT * FROM alert_history
            WHERE organization_id = ? AND company = ?
            ORDER BY detected_at DESC
            LIMIT ?
            """,
            (organization_id or "public", company, query_limit),
        ).fetchall()
    else:
        rows = connection.execute(
            """
            SELECT * FROM alert_history
            WHERE organization_id = ?
            ORDER BY detected_at DESC
            LIMIT ?
            """,
            (organization_id or "public", query_limit),
        ).fetchall()
    connection.close()
    alerts = []
    for row in rows:
        payload = dict(row)
        if real_only and _is_mock_source_url(payload.get("source_url", "")):
            continue
        try:
            payload["recommended_actions"] = json.loads(
                payload.get("recommended_actions") or "[]"
            )
        except Exception:
            payload["recommended_actions"] = []
        alerts.append(payload)
        if len(alerts) >= limit:
            break
    return alerts
