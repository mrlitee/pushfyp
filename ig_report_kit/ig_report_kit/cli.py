"""Command-line entry point for ig_report_kit.

Usage examples:

    # 1) Capture public evidence for a URL
    python -m ig_report_kit capture \\
        --url https://www.instagram.com/some_public_account/ \\
        --category scam \\
        --reporter-name "Jane Doe" \\
        --reporter-contact "jane@example.com" \\
        --notes "Account DMed me a fake investment link on 2026-05-10." \\
        --out ./cases

    # 2) Generate bilingual report draft from a case folder
    python -m ig_report_kit draft --case ./cases/20260510T...

    # 3) Build a single PDF bundle for filing
    python -m ig_report_kit bundle --case ./cases/20260510T...

    # List supported categories
    python -m ig_report_kit categories
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .categories import CATEGORIES, list_categories
from .evidence import EvidenceRecord, collect
from .report_templates import draft_report


def _cmd_capture(args: argparse.Namespace) -> int:
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    rec = collect(
        url=args.url,
        out_dir=out_dir,
        reporter_name=args.reporter_name,
        reporter_contact=args.reporter_contact,
        category=args.category,
        notes=args.notes or "",
    )
    # find case dir by scanning: evidence.collect() already wrote manifest there
    case_dir = _latest_case_dir_for(out_dir, rec.url)
    print(f"[ok] evidence captured: {case_dir}")
    print(f"     artifacts: {len(rec.artifacts)}")
    print(f"     next: python -m ig_report_kit draft --case '{case_dir}'")
    return 0


def _cmd_draft(args: argparse.Namespace) -> int:
    case_dir = Path(args.case).resolve()
    manifest = case_dir / "evidence.json"
    if not manifest.exists():
        print(f"[err] not a case dir (missing evidence.json): {case_dir}", file=sys.stderr)
        return 2
    data = json.loads(manifest.read_text(encoding="utf-8"))
    rec = _record_from_dict(data)
    text = draft_report(rec)
    out = case_dir / "report.txt"
    out.write_text(text, encoding="utf-8")
    print(f"[ok] draft written: {out}")
    print(f"     next: python -m ig_report_kit bundle --case '{case_dir}'")
    return 0


def _cmd_bundle(args: argparse.Namespace) -> int:
    # Import here so `capture` and `draft` work even if reportlab is missing.
    from .pdf_bundle import build_pdf

    case_dir = Path(args.case).resolve()
    pdf = build_pdf(case_dir)
    print(f"[ok] PDF bundle built: {pdf}")
    print("     attach this PDF to your Instagram Help Center / police / NCMEC filing.")
    return 0


def _cmd_categories(_: argparse.Namespace) -> int:
    for key in list_categories():
        c = CATEGORIES[key]
        print(f"{key:14}  {c.label_en}  |  {c.label_id}")
    return 0


def _record_from_dict(d: dict) -> EvidenceRecord:
    from .evidence import Artifact

    rec = EvidenceRecord(
        url=d["url"],
        captured_at_utc=d["captured_at_utc"],
        reporter_name=d["reporter_name"],
        reporter_contact=d["reporter_contact"],
        category=d["category"],
        notes=d.get("notes", ""),
        og_title=d.get("og_title"),
        og_image=d.get("og_image"),
    )
    rec.artifacts = [Artifact(**a) for a in d.get("artifacts", [])]
    return rec


def _latest_case_dir_for(out_dir: Path, url: str) -> Path:
    from .evidence import _safe_slug  # internal helper, fine within the package

    slug = _safe_slug(url)
    candidates = sorted(
        (p for p in out_dir.iterdir() if p.is_dir() and p.name.endswith(f"_{slug}")),
        key=lambda p: p.name,
        reverse=True,
    )
    if not candidates:
        raise FileNotFoundError(f"no case dir produced for {url}")
    return candidates[0]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ig_report_kit",
        description=(
            "Document abusive Instagram accounts and generate clean report "
            "drafts for official channels. This tool does NOT perform mass "
            "or automated reporting."
        ),
    )
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="cmd", required=True)

    cap = sub.add_parser("capture", help="capture public evidence for a URL")
    cap.add_argument("--url", required=True)
    cap.add_argument(
        "--category", required=True, choices=list_categories(),
        help="violation category",
    )
    cap.add_argument("--reporter-name", required=True)
    cap.add_argument("--reporter-contact", required=True,
                     help="email or phone the platform can reach you at")
    cap.add_argument("--notes", default="",
                     help="your plain-text description of what happened")
    cap.add_argument("--out", default="./cases", help="output folder (default: ./cases)")
    cap.set_defaults(func=_cmd_capture)

    drf = sub.add_parser("draft", help="generate bilingual report draft from a case")
    drf.add_argument("--case", required=True, help="path to the case folder")
    drf.set_defaults(func=_cmd_draft)

    bnd = sub.add_parser("bundle", help="build a single PDF from a case")
    bnd.add_argument("--case", required=True, help="path to the case folder")
    bnd.set_defaults(func=_cmd_bundle)

    cats = sub.add_parser("categories", help="list supported violation categories")
    cats.set_defaults(func=_cmd_categories)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
