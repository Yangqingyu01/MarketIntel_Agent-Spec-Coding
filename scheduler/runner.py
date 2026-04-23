"""Scheduler bootstrap helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from scheduler.jobs import run_and_dispatch_summary

try:
    from apscheduler.schedulers.background import BackgroundScheduler
except Exception:  # pragma: no cover
    BackgroundScheduler = None


@dataclass
class _DemoJob:
    id: str
    name: str
    trigger: str


class _DemoScheduler:
    def __init__(self) -> None:
        self._jobs: List[_DemoJob] = [
            _DemoJob(
                id="daily_summary",
                name="run_and_dispatch_summary",
                trigger="cron[hour='9', minute='0']",
            ),
            _DemoJob(
                id="weekly_summary",
                name="run_and_dispatch_summary",
                trigger="cron[day_of_week='mon', hour='9', minute='30']",
            ),
        ]

    def get_jobs(self) -> List[_DemoJob]:
        return self._jobs


def create_scheduler() -> Optional[Any]:
    if BackgroundScheduler is None:
        return _DemoScheduler()
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        run_and_dispatch_summary,
        "cron",
        hour=9,
        minute=0,
        args=["daily"],
        id="daily_summary",
        replace_existing=True,
    )
    scheduler.add_job(
        run_and_dispatch_summary,
        "cron",
        day_of_week="mon",
        hour=9,
        minute=30,
        args=["weekly"],
        id="weekly_summary",
        replace_existing=True,
    )
    return scheduler


def describe_scheduler() -> Dict[str, Any]:
    scheduler = create_scheduler()
    if scheduler is None:
        return {"enabled": False, "jobs": []}
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({"id": job.id, "name": job.name, "trigger": str(job.trigger)})
    return {"enabled": bool(jobs), "jobs": jobs}
