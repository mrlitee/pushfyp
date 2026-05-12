"""PDF bundle generator.

Takes a completed case directory (manifest + artifacts + report.txt) and
produces a single PDF suitable for attaching to a police / Kominfo / NCMEC
complaint. The preview image is embedded so the reviewer can see the
visual context without opening separate files.
"""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


def build_pdf(case_dir: Path) -> Path:
    manifest_path = case_dir / "evidence.json"
    report_path = case_dir / "report.txt"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing evidence.json in {case_dir}")
    if not report_path.exists():
        raise FileNotFoundError(f"Missing report.txt in {case_dir}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    report_text = report_path.read_text(encoding="utf-8")

    out_path = case_dir / "bundle.pdf"
    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    mono = ParagraphStyle(
        "mono",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=9,
        leading=11,
    )
    h1 = styles["Heading1"]
    h2 = styles["Heading2"]
    normal = styles["BodyText"]

    story: list = []
    story.append(Paragraph("Instagram Abuse Report Bundle", h1))
    story.append(Paragraph(f"URL: {manifest['url']}", normal))
    story.append(Paragraph(f"Captured (UTC): {manifest['captured_at_utc']}", normal))
    story.append(Paragraph(f"Category: {manifest['category']}", normal))
    story.append(
        Paragraph(
            f"Reporter: {manifest['reporter_name']} &lt;{manifest['reporter_contact']}&gt;",
            normal,
        )
    )
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("Manifest (evidence.json)", h2))
    story.append(
        Paragraph(
            "<br/>".join(
                _escape_line(line)
                for line in json.dumps(manifest, indent=2, ensure_ascii=False).splitlines()
            ),
            mono,
        )
    )
    story.append(PageBreak())

    preview = _find_preview(case_dir)
    if preview is not None:
        story.append(Paragraph("Captured preview image", h2))
        try:
            img = Image(str(preview))
            img._restrictSize(16 * cm, 20 * cm)
            story.append(img)
        except Exception as exc:  # pragma: no cover - defensive
            story.append(Paragraph(f"(could not embed preview: {exc})", normal))
        story.append(PageBreak())

    story.append(Paragraph("Report draft (ID + EN)", h2))
    for line in report_text.splitlines() or [""]:
        story.append(Paragraph(_escape_line(line) or "&nbsp;", mono))

    doc.build(story)
    return out_path


def _find_preview(case_dir: Path) -> Path | None:
    for name in ("preview.jpg", "preview.png", "preview.webp"):
        p = case_dir / name
        if p.exists():
            return p
    return None


def _escape_line(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
