from __future__ import annotations

import json
from pathlib import Path

from config import config
from scheduler.jobs import run_and_dispatch_summary


def test_scheduler_summary_aggregates_reports_and_alerts(
    monkeypatch,
    tmp_path: Path,
) -> None:
    config.config_path = tmp_path / "config" / "competitors.json"
    config.config_path.parent.mkdir(parents=True, exist_ok=True)
    config.config_path.write_text(
        json.dumps(
            {
                "competitors": [
                    {"name": "飞书", "monitoring_frequency": "daily"},
                    {"name": "钉钉", "monitoring_frequency": "weekly"},
                ]
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    def fake_run_analysis(targets, dimensions=None, time_range=None, output_format="web"):
        del dimensions
        del time_range
        return {
            "report": {"target": targets[0], "report_id": "RPT-1"},
            "alerts": [{"company": targets[0], "severity": "medium"}],
        }

    monkeypatch.setattr("scheduler.jobs.run_analysis", fake_run_analysis)

    payload = run_and_dispatch_summary("daily")
    assert payload["summary"]["summary_type"] == "daily"
    assert payload["summary"]["report_count"] == 1
    assert payload["summary"]["alert_count"] == 1
    assert payload["delivery"]["ok"] is True
