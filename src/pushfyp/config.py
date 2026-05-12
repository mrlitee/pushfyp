"""Konfigurasi dari environment variables."""
from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    threads_access_token: str | None = os.getenv("THREADS_ACCESS_TOKEN")
    threads_user_id: str | None = os.getenv("THREADS_USER_ID")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")

    def require_threads(self) -> None:
        if not self.threads_access_token or not self.threads_user_id:
            raise RuntimeError(
                "THREADS_ACCESS_TOKEN dan THREADS_USER_ID wajib di-set di .env. "
                "Dapatkan di https://developers.facebook.com/docs/threads"
            )


config = Config()
