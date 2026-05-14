"""Hook generator — bikin 10 variasi kalimat pembuka dari topik.

Rule-based default. Kalau OPENAI_API_KEY ada, pakai LLM untuk hasil lebih kaya.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .config import config


TEMPLATES = [
    "Kenapa {topic} selalu gagal? Ini 3 alasannya.",
    "Jangan {topic} sebelum kamu baca ini.",
    "Ternyata {topic} bukan soal bakat. Tapi...",
    "Saya habis {amount} untuk {topic}. Hasilnya?",
    "Stop {topic}. Mulai lakukan ini.",
    "{topic} dalam 30 hari: apa yang saya pelajari.",
    "Kalau saya bisa mulai {topic} dari nol lagi, saya akan...",
    "Rahasia {topic} yang nggak pernah diajarin guru.",
    "99% orang salah soal {topic}. Termasuk saya dulu.",
    "Ini kenapa {topic} kamu stuck di level yang sama.",
    "{topic}: yang viral vs yang beneran jalan.",
    "Pertanyaan jujur: kamu beneran butuh {topic}?",
]


@dataclass
class Hook:
    text: str
    style: str


def _rule_based(topic: str, amount: str = "jutaan rupiah") -> list[Hook]:
    styles = [
        "curiosity", "warning", "myth-break", "story", "command",
        "journey", "reflection", "secret", "contrarian", "problem",
        "comparison", "honest",
    ]
    hooks = []
    for tpl, style in zip(TEMPLATES, styles):
        text = tpl.format(topic=topic, amount=amount)
        hooks.append(Hook(text=text, style=style))
    return hooks[:10]


def _llm_based(topic: str) -> list[Hook] | None:
    if not config.openai_api_key:
        return None
    try:
        import json
        import requests

        prompt = (
            f"Buatkan 10 kalimat pembuka (hook) untuk postingan Threads tentang topik: '{topic}'. "
            "Maksimal 80 karakter per hook. Variasikan gaya: pertanyaan, klaim kontroversial, angka, cerita. "
            "Bahasa Indonesia informal. "
            "Balas HANYA JSON array of objects dengan field 'text' dan 'style'. Tidak ada teks lain."
        )
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {config.openai_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.9,
                "response_format": {"type": "json_object"},
            },
            timeout=30,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        data = json.loads(content)
        items = data if isinstance(data, list) else data.get("hooks") or data.get("data") or []
        return [Hook(text=x["text"], style=x.get("style", "llm")) for x in items][:10]
    except Exception:
        return None


def generate(topic: str, use_llm: bool = True) -> list[Hook]:
    """Generate 10 hook variations untuk topic."""
    if use_llm:
        result = _llm_based(topic)
        if result:
            return result
    return _rule_based(topic)
