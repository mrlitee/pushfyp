"""Scheduler auto-post pakai APScheduler + SQLite jobstore.

Pilih jam optimal (default: 07:30 / 12:15 / 20:00 WIB) atau custom datetime.

Modes:
- blocking=True  : satu-shot CLI, scheduler.start() block sampai job jalan.
- blocking=False : pakai BackgroundScheduler singleton (untuk web app).
"""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from threading import Lock

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.date import DateTrigger

from . import threads_api

# Jam rata-rata engagement tinggi untuk audiens ID (heuristik)
RECOMMENDED_SLOTS = ["07:30", "12:15", "20:00"]

_DB_URL = f"sqlite:///{Path.cwd() / 'schedule.db'}"

_bg_scheduler: BackgroundScheduler | None = None
_bg_lock = Lock()


def _get_background_scheduler() -> BackgroundScheduler:
    global _bg_scheduler
    with _bg_lock:
        if _bg_scheduler is None:
            sch = BackgroundScheduler(jobstores={"default": SQLAlchemyJobStore(url=_DB_URL)})
            sch.start()
            _bg_scheduler = sch
        return _bg_scheduler


def _job_post(text: str) -> None:
    """Job yang dijalankan scheduler — post via Threads API."""
    result = threads_api.post_text(text)
    print(f"[scheduler] posted: media_id={result.media_id}")


def schedule_once(text: str, when: datetime, blocking: bool = True) -> str:
    """Jadwalkan satu postingan pada waktu `when`.

    blocking=True  : pakai BlockingScheduler (cocok untuk CLI).
    blocking=False : pakai BackgroundScheduler singleton (cocok untuk web/server).
    """
    if blocking:
        sch = BlockingScheduler(jobstores={"default": SQLAlchemyJobStore(url=_DB_URL)})
        job = sch.add_job(_job_post, trigger=DateTrigger(run_date=when), args=[text])
        sch.start()
        return job.id

    sch = _get_background_scheduler()
    job = sch.add_job(_job_post, trigger=DateTrigger(run_date=when), args=[text])
    return job.id


def next_recommended_slot(now: datetime | None = None) -> datetime:
    """Cari slot rekomendasi terdekat dari sekarang."""
    now = now or datetime.now()
    today_slots = []
    for hm in RECOMMENDED_SLOTS:
        h, m = hm.split(":")
        today_slots.append(now.replace(hour=int(h), minute=int(m), second=0, microsecond=0))
    future = [s for s in today_slots if s > now]
    if future:
        return future[0]
    # besok pagi pakai timedelta (lebih aman dari edge case bulan/tahun)
    nxt = today_slots[0] + timedelta(days=1)
    return nxt
