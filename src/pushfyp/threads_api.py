"""Klien Threads Graph API resmi (Meta).

Dokumentasi: https://developers.facebook.com/docs/threads

Endpoint utama yang dipakai:
  POST /{user-id}/threads       -> buat media container
  POST /{user-id}/threads_publish -> publish container ke timeline
"""
from __future__ import annotations

import time
from dataclasses import dataclass

import requests

from .config import config

API_BASE = "https://graph.threads.net/v1.0"


class ThreadsAPIError(RuntimeError):
    pass


@dataclass
class PublishedPost:
    creation_id: str
    media_id: str | None


def _post(path: str, params: dict, timeout: float = 30.0) -> dict:
    token = config.threads_access_token
    url = f"{API_BASE}{path}"
    full = {**params, "access_token": token}
    resp = requests.post(url, data=full, timeout=timeout)
    if not resp.ok:
        raise ThreadsAPIError(f"POST {path} gagal ({resp.status_code}): {resp.text}")
    return resp.json()


def create_text_container(text: str) -> str:
    """Buat media container untuk postingan teks. Return: creation_id."""
    config.require_threads()
    data = _post(
        f"/{config.threads_user_id}/threads",
        {"media_type": "TEXT", "text": text},
    )
    cid = data.get("id")
    if not cid:
        raise ThreadsAPIError(f"Response tidak punya id: {data}")
    return cid


def publish_container(creation_id: str, max_retries: int = 5, backoff: float = 3.0) -> PublishedPost:
    """Publish container. Threads butuh ~10-30 detik untuk siap, jadi retry."""
    config.require_threads()
    last_err: Exception | None = None
    for attempt in range(max_retries):
        try:
            data = _post(
                f"/{config.threads_user_id}/threads_publish",
                {"creation_id": creation_id},
            )
            return PublishedPost(creation_id=creation_id, media_id=data.get("id"))
        except ThreadsAPIError as e:
            last_err = e
            time.sleep(backoff * (attempt + 1))
    raise ThreadsAPIError(f"Publish gagal setelah {max_retries}x retry: {last_err}")


def post_text(text: str) -> PublishedPost:
    """Shortcut: buat container + publish."""
    cid = create_text_container(text)
    # Meta rekomendasi tunggu >=30 detik sebelum publish
    time.sleep(30)
    return publish_container(cid)
