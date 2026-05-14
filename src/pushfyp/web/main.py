"""FastAPI app — UI + JSON API untuk pushfyp toolkit.

Jalankan:
    uvicorn pushfyp.web.main:app --reload
atau:
    pushfyp serve
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .. import analyzer, hashtag, hook

app = FastAPI(
    title="pushfyp",
    description="Toolkit optimasi postingan Threads secara organik.",
    version="0.1.0",
)

_BASE = Path(__file__).parent
app.mount("/static", StaticFiles(directory=_BASE / "static"), name="static")


# ---------- Schemas ------------------------------------------------------

class AnalyzeIn(BaseModel):
    url: str = Field(..., description="Link postingan Threads publik.")


class HookIn(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200)
    use_llm: bool = True


class PostIn(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)


class ScheduleIn(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)
    when: str | None = Field(None, description="ISO-8601 datetime; kosongkan untuk slot rekomendasi.")


# ---------- UI ----------------------------------------------------------

@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(_BASE / "templates" / "index.html")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": "0.1.0"}


# ---------- API ---------------------------------------------------------

@app.post("/api/analyze")
def api_analyze(body: AnalyzeIn) -> dict:
    try:
        return analyzer.analyze(body.url).to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Gagal fetch: {e}")


@app.post("/api/hook")
def api_hook(body: HookIn) -> dict:
    hooks = hook.generate(body.topic, use_llm=body.use_llm)
    return {"topic": body.topic, "hooks": [{"text": h.text, "style": h.style} for h in hooks]}


@app.get("/api/niches")
def api_niches() -> dict:
    return {"niches": hashtag.niches()}


@app.get("/api/hashtags")
def api_hashtags(niche: str, count: int = 5, include_fyp: bool = True) -> dict:
    try:
        tags = hashtag.suggest(niche, count=count, include_fyp=include_fyp)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"niche": niche, "hashtags": tags}


@app.post("/api/post")
def api_post(body: PostIn) -> dict:
    from .. import threads_api
    try:
        result = threads_api.post_text(body.text)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except threads_api.ThreadsAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))
    return {"media_id": result.media_id, "creation_id": result.creation_id}


@app.post("/api/schedule")
def api_schedule(body: ScheduleIn) -> dict:
    from .. import schedule
    if body.when:
        try:
            target = datetime.fromisoformat(body.when)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Format waktu salah: {body.when}")
    else:
        target = schedule.next_recommended_slot()

    # Non-blocking: enqueue ke background scheduler dengan SQLite jobstore.
    job_id = schedule.schedule_once(body.text, target, blocking=False)
    return {"job_id": job_id, "scheduled_at": target.isoformat()}
