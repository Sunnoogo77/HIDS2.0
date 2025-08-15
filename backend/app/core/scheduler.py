# app/core/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from typing import Literal, Optional

# Fréquences supportées
Freq = Literal["minutely", "hourly", "daily", "weekly"]
FREQ_SECONDS = {
    "minutely": 60,
    "hourly": 3600,
    "daily": 86400,
    "weekly": 604800,
}

scheduler: Optional[BackgroundScheduler] = None

def get_scheduler() -> BackgroundScheduler:
    global scheduler
    if scheduler is None:
        scheduler = BackgroundScheduler(timezone="UTC")
    return scheduler

def _job_id(kind: str, item_id: int) -> str:
    return f"{kind}:{item_id}"

def add_interval_job(kind: str, item_id: int, seconds: int, func, **kwargs):
    sch = get_scheduler()
    job_id = _job_id(kind, item_id)
    
    try:
        sch.remove_job(job_id)
    except Exception:
        pass
    sch.add_job(func, IntervalTrigger(seconds=seconds), id=job_id, kwargs=kwargs, replace_existing=True)

def remove_job(kind: str, item_id: int):
    sch = get_scheduler()
    job_id = _job_id(kind, item_id)
    try:
        sch.remove_job(job_id)
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
