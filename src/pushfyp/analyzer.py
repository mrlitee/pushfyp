"""Analisa postingan Threads dari link publik.

Hanya mengambil metadata yang sudah di-expose Threads via Open Graph tags
(tidak membuka/bypass apapun). Output: skor FYP-readiness + saran perbaikan.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from urllib.parse import urlparse

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)

THREADS_URL_RE = re.compile(
    r"^https?://(?:www\.)?threads\.(?:net|com)/@[^/]+/post/[A-Za-z0-9_-]+/?",
    re.IGNORECASE,
)


@dataclass
class PostMetadata:
    url: str
    author: str | None = None
    caption: str | None = None
    image: str | None = None
    hashtags: list[str] = field(default_factory=list)
    mentions: list[str] = field(default_factory=list)


@dataclass
class AnalysisResult:
    meta: PostMetadata
    score: int
    breakdown: dict[str, int]
    suggestions: list[str]

    def to_dict(self) -> dict:
        return {
            "meta": asdict(self.meta),
            "score": self.score,
            "breakdown": self.breakdown,
            "suggestions": self.suggestions,
        }


def _validate_url(url: str) -> None:
    if not THREADS_URL_RE.match(url):
        raise ValueError(
            "URL harus format Threads publik: https://www.threads.net/@user/post/XXXXX"
        )


def fetch_metadata(url: str, timeout: float = 10.0) -> PostMetadata:
    """Ambil metadata postingan via Open Graph tags (publik)."""
    import requests
    from bs4 import BeautifulSoup

    _validate_url(url)

    resp = requests.get(
        url,
        headers={"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"},
        timeout=timeout,
        allow_redirects=True,
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    def og(prop: str) -> str | None:
        tag = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
        return tag.get("content") if tag and tag.get("content") else None

    caption = og("og:description") or og("description")
    image = og("og:image")
    title = og("og:title") or ""

    # Author biasanya ada di path URL (@user) atau og:title ("Username on Threads: ...")
    parsed = urlparse(url)
    author = None
    m = re.match(r"/@([^/]+)/", parsed.path)
    if m:
        author = m.group(1)
    elif " on Threads" in title:
        author = title.split(" on Threads")[0].strip()

    hashtags = re.findall(r"#(\w+)", caption or "")
    mentions = re.findall(r"@(\w+)", caption or "")

    return PostMetadata(
        url=url,
        author=author,
        caption=caption,
        image=image,
        hashtags=hashtags,
        mentions=mentions,
    )


# --- Scoring heuristics ---------------------------------------------------

WEAK_OPENERS = {
    "hi", "hello", "hey", "halo", "hai", "guys", "so", "jadi", "gue", "aku",
    "today", "hari", "just", "ok", "oke",
}

HOOK_WORDS = {
    "why", "how", "stop", "never", "everyone", "nobody", "secret", "truth",
    "kenapa", "gimana", "jangan", "rahasia", "ternyata", "fakta", "bahaya",
}


def _score_caption_length(caption: str) -> tuple[int, str | None]:
    n = len(caption)
    if n < 20:
        return 5, "Caption terlalu pendek (<20 karakter). Target 100-400 karakter untuk ruang storytelling."
    if n < 100:
        return 12, "Caption masih pendek. Tambah konteks atau cerita singkat (ideal 150-400 karakter)."
    if n <= 500:
        return 20, None
    return 14, "Caption kepanjangan (>500 char). Potong sampai punchy — Threads FYP suka yang scannable."


def _score_hook(caption: str) -> tuple[int, str | None]:
    first = caption.strip().split()
    if not first:
        return 0, "Tidak ada caption."
    first_word = re.sub(r"[^\w]", "", first[0].lower())
    if first_word in WEAK_OPENERS:
        return 5, (
            f"Kata pertama '{first[0]}' termasuk opener lemah. "
            "Ganti dengan pertanyaan, klaim kontroversial, atau angka."
        )
    lower_cap = caption.lower()
    if any(h in lower_cap[:80] for h in HOOK_WORDS):
        return 20, None
    if caption.strip().endswith("?") or "?" in caption[:80]:
        return 18, None
    if re.search(r"\b\d+\b", caption[:80]):
        return 16, None
    return 10, "Hook pembuka kurang kuat. Coba mulai dengan pertanyaan, angka, atau klaim kontras."


def _score_hashtags(tags: list[str]) -> tuple[int, str | None]:
    n = len(tags)
    if n == 0:
        return 8, "Tidak ada hashtag. Tambah 1-3 hashtag relevan (Threads menoleransi sedikit hashtag)."
    if n <= 3:
        return 15, None
    if n <= 5:
        return 10, "Hashtag agak banyak. Threads algoritma lebih suka 1-3 hashtag tertarget."
    return 5, f"Terlalu banyak hashtag ({n}). Pangkas jadi 1-3 yang paling relevan."


def _score_media(image: str | None) -> tuple[int, str | None]:
    if image:
        return 15, None
    return 8, "Tidak ada media. Postingan dengan gambar/video punya dwell-time lebih tinggi di FYP."


def _score_cta(caption: str) -> tuple[int, str | None]:
    lower = caption.lower()
    if "?" in caption:
        return 15, None
    cta_keywords = ("setuju", "menurutmu", "kamu gimana", "agree", "what do you", "share", "komen")
    if any(k in lower for k in cta_keywords):
        return 15, None
    return 7, "Tambah CTA/pertanyaan di akhir untuk memancing reply (reply > like untuk sinyal FYP)."


def _score_readability(caption: str) -> tuple[int, str | None]:
    lines = [ln for ln in caption.splitlines() if ln.strip()]
    if len(lines) >= 3 and len(caption) > 150:
        return 15, None
    if len(caption) > 200 and len(lines) < 2:
        return 7, "Wall of text. Pecah jadi 2-4 baris pendek biar scannable."
    return 12, None


def analyze(url: str) -> AnalysisResult:
    meta = fetch_metadata(url)
    caption = meta.caption or ""

    checks = {
        "caption_length": _score_caption_length(caption),
        "hook": _score_hook(caption),
        "hashtags": _score_hashtags(meta.hashtags),
        "media": _score_media(meta.image),
        "cta": _score_cta(caption),
        "readability": _score_readability(caption),
    }

    breakdown = {k: v[0] for k, v in checks.items()}
    suggestions = [v[1] for v in checks.values() if v[1]]
    score = sum(breakdown.values())

    return AnalysisResult(
        meta=meta,
        score=score,
        breakdown=breakdown,
        suggestions=suggestions,
    )
