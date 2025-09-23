# ---------------------

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from typing import Optional

FREQ_SECONDS = {
    "minutely": 60,
    "hourly": 3600,
    "daily": 86400,
    "weekly": 604800,
}

_scheduler: Optional[BackgroundScheduler] = None

def get_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler is None:
        # SQLite file under ./data (persisted via docker volume)
        jobstores = {"default": SQLAlchemyJobStore(url="sqlite:///data/jobs.db")}
        _scheduler = BackgroundScheduler(timezone="UTC", jobstores=jobstores)
    return _scheduler

def _job_id(kind: str, entity_id: int) -> str:
    return f"{kind}:{entity_id}"

def add_interval_job(kind: str, entity_id: int, seconds: int, func, **job_kwargs):
    sch = get_scheduler()
    job_id = _job_id(kind, entity_id)
    try:
        sch.remove_job(job_id)
    except Exception:
        pass
    sch.add_job(
        func,
        IntervalTrigger(seconds=seconds),
        id=job_id,
        replace_existing=True,
        kwargs=job_kwargs,
    )

def remove_job(kind: str, entity_id: int):
    sch = get_scheduler()
    try:
        sch.remove_job(_job_id(kind, entity_id))
    except Exception:
        pass

def start_scheduler():
    sch = get_scheduler()
    if not sch.running:
        sch.start()

def shutdown_scheduler():
    sch = get_scheduler()
    if sch.running:
        sch.shutdown(wait=False)
