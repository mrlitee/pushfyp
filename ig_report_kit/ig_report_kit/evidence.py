"""Evidence collector.

Saves a tamper-evident record of a public Instagram URL:
  - raw HTML snapshot
  - OpenGraph preview image (if available)
  - SHA-256 hash of each artifact
  - evidence.json manifest with timestamp (UTC, ISO-8601) and reporter notes

Only fetches PUBLIC pages with a normal User-Agent. No login, no scraping of
private content, no circumvention of access controls.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

USER_AGENT = (
    "Mozilla/5.0 (ig_report_kit evidence collector; "
    "contact: set REPORTER_EMAIL env var)"
)
TIMEOUT = 20


@dataclass
class Artifact:
    filename: str
    sha256: str
    size_bytes: int
    content_type: str


@dataclass
class EvidenceRecord:
    url: str
    captured_at_utc: str
    reporter_name: str
    reporter_contact: str
    category: str
    notes: str
    artifacts: list[Artifact] = field(default_factory=list)
    og_title: str | None = None
    og_image: str | None = None


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_slug(url: str) -> str:
    p = urlparse(url)
    raw = f"{p.netloc}{p.path}".strip("/").replace("/", "_")
    return re.sub(r"[^A-Za-z0-9_.-]", "_", raw)[:80] or "evidence"


def _extract_og(html: str, prop: str) -> str | None:
    m = re.search(
        rf'<meta[^>]+property=["\']{re.escape(prop)}["\'][^>]+content=["\']([^"\']+)["\']',
        html,
        re.IGNORECASE,
    )
    return m.group(1) if m else None


def collect(
    url: str,
    out_dir: Path,
    reporter_name: str,
    reporter_contact: str,
    category: str,
    notes: str,
) -> EvidenceRecord:
    """Download public evidence for `url` into a new folder under `out_dir`."""
    if not url.startswith(("http://", "https://")):
        raise ValueError("URL must start with http:// or https://")

    slug = _safe_slug(url)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    case_dir = out_dir / f"{ts}_{slug}"
    case_dir.mkdir(parents=True, exist_ok=True)

    rec = EvidenceRecord(
        url=url,
        captured_at_utc=datetime.now(timezone.utc).isoformat(),
        reporter_name=reporter_name,
        reporter_contact=reporter_contact,
        category=category,
        notes=notes,
    )

    # 1) HTML snapshot
    headers = {"User-Agent": USER_AGENT, "Accept-Language": "en,id;q=0.8"}
    resp = requests.get(url, headers=headers, timeout=TIMEOUT, allow_redirects=True)
    html_path = case_dir / "page.html"
    html_path.write_bytes(resp.content)
    rec.artifacts.append(
        Artifact(
            filename="page.html",
            sha256=_sha256(resp.content),
            size_bytes=len(resp.content),
            content_type=resp.headers.get("Content-Type", "text/html"),
        )
    )

    # 2) OpenGraph metadata & preview image
    text = resp.text
    rec.og_title = _extract_og(text, "og:title")
    rec.og_image = _extract_og(text, "og:image")

    if rec.og_image:
        try:
            img_resp = requests.get(
                rec.og_image, headers=headers, timeout=TIMEOUT
            )
            if img_resp.ok and img_resp.content:
                ext = ".jpg"
                ctype = img_resp.headers.get("Content-Type", "")
                if "png" in ctype:
                    ext = ".png"
                elif "webp" in ctype:
                    ext = ".webp"
                img_path = case_dir / f"preview{ext}"
                img_path.write_bytes(img_resp.content)
                rec.artifacts.append(
                    Artifact(
                        filename=img_path.name,
                        sha256=_sha256(img_resp.content),
                        size_bytes=len(img_resp.content),
                        content_type=ctype or "image/jpeg",
                    )
                )
        except requests.RequestException:
            # preview download is best-effort; the HTML snapshot is the primary record
            pass

    # 3) Manifest
    manifest_path = case_dir / "evidence.json"
    manifest_path.write_text(
        json.dumps(_to_dict(rec), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return rec


def _to_dict(rec: EvidenceRecord) -> dict:
    d = asdict(rec)
    return d


def case_dir_for(rec: EvidenceRecord, out_dir: Path) -> Path:
    """Recompute the case directory path for a given record (helper for CLI)."""
    slug = _safe_slug(rec.url)
    ts = datetime.fromisoformat(rec.captured_at_utc).strftime("%Y%m%dT%H%M%SZ")
    return out_dir / f"{ts}_{slug}"
