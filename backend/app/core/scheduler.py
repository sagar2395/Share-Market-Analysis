"""APScheduler setup — runs the daily EOD ingestion job.

Indian market closes ~15:30 IST; we schedule an evening pull. The scheduler is
best-effort: if data fetch fails (e.g. offline sandbox), it logs and moves on.
"""

from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.logging import get_logger
from app.services import ingestion

log = get_logger(__name__)
_scheduler: BackgroundScheduler | None = None


def start_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        return
    _scheduler = BackgroundScheduler(timezone="Asia/Kolkata")
    # 18:30 IST on weekdays — after the NSE/BSE close.
    _scheduler.add_job(
        ingestion.run,
        CronTrigger(day_of_week="mon-fri", hour=18, minute=30),
        id="eod_ingestion",
        replace_existing=True,
    )
    _scheduler.start()
    log.info("Scheduler started: daily EOD ingestion at 18:30 IST (Mon-Fri).")


def shutdown_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
