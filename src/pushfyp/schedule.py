"""Scheduler auto-post pakai APScheduler + SQLite jobstore.

Pilih jam optimal (default: 07:30 / 12:15 / 20:00 WIB) atau custom datetime.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.date import DateTrigger

from . import threads_api

# Jam rata-rata engagement tinggi untuk audiens ID (heuristik)
RECOMMENDED_SLOTS = ["07:30", "12:15", "20:00"]

_DB_URL = f"sqlite:///{Path.cwd() / 'schedule.db'}"


def _build_scheduler(blocking: bool = False):
    cls = BlockingScheduler if blocking else BackgroundScheduler
    return cls(jobstores={"default": SQLAlchemyJobStore(url=_DB_URL)})


def _job_post(text: str) -> None:
    """Job yang dijalankan scheduler — post via Threads API."""
    result = threads_api.post_text(text)
    print(f"[scheduler] posted: media_id={result.media_id}")


def schedule_once(text: str, when: datetime, blocking: bool = True) -> str:
    """Jadwalkan satu postingan pada waktu `when`.

    Jika blocking=True, scheduler akan block sampai job selesai (cocok untuk CLI).
    """
    scheduler = _build_scheduler(blocking=blocking)
    job = scheduler.add_job(
        _job_post,
        trigger=DateTrigger(run_date=when),
        args=[text],
        replace_existing=False,
    )
    scheduler.start()
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
    # besok pagi
    nxt = today_slots[0]
    return nxt.replace(day=nxt.day + 1) if nxt.day < 28 else nxt.replace(
        month=(nxt.month % 12) + 1, day=1
    )
