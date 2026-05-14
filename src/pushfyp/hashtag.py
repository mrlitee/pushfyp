"""Rekomendasi hashtag per niche."""
from __future__ import annotations

import json
from pathlib import Path
from random import sample

_DATA = Path(__file__).parent / "data" / "hashtags.json"


def _load() -> dict[str, list[str]]:
    with _DATA.open("r", encoding="utf-8") as f:
        return json.load(f)


def niches() -> list[str]:
    return sorted(_load().keys())


def suggest(niche: str, count: int = 5, include_fyp: bool = True) -> list[str]:
    """Rekomendasi hashtag untuk niche tertentu.

    Args:
        niche: nama niche (lihat `niches()`).
        count: jumlah hashtag niche yang diambil.
        include_fyp: jika True, tambah 1-2 hashtag generic fyp/viral.
    """
    data = _load()
    key = niche.lower().strip()
    if key not in data:
        raise ValueError(f"Niche '{niche}' tidak dikenal. Tersedia: {', '.join(niches())}")

    pool = data[key]
    picks = sample(pool, min(count, len(pool)))

    if include_fyp and key != "fyp":
        fyp_pool = data.get("fyp", [])
        picks += sample(fyp_pool, min(2, len(fyp_pool)))

    return [f"#{t}" for t in picks]
