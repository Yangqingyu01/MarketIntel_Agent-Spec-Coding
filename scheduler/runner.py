"""Scheduler bootstrap helpers."""

from __future__ import annotations

from typing import Any, Dict, Optional

from scheduler.jobs import run_and_dispatch_summary

try:
    from apscheduler.schedulers.background import BackgroundScheduler
except Exception:  # pragma: no cover
    BackgroundScheduler = None


def create_scheduler() -> Optional[Any]:
    if BackgroundScheduler is None:
        return None
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_and_dispatch_summary, "cron", hour=9, minute=0, args=["daily"], id="daily_summary", replace_existing=True)
    scheduler.add_job(run_and_dispatch_summary, "cron", day_of_week="mon", hour=9, minute=30, args=["weekly"], id="weekly_summary", replace_existing=True)
    return scheduler


def describe_scheduler() -> Dict[str, Any]:
    scheduler = create_scheduler()
    if scheduler is None:
        return {"enabled": False, "jobs": []}
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({"id": job.id, "name": job.name, "trigger": str(job.trigger)})
    return {"enabled": True, "jobs": jobs}
