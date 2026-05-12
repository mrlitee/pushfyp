"""Bilingual (ID + EN) report draft generator.

Output is a neutral, factual letter suitable for pasting into:
  - Instagram in-app report forms (free-text fields)
  - Instagram Help Center forms
  - Police / Kominfo / NCMEC complaints

The draft intentionally avoids accusations beyond what the reporter asserts,
and states only observed facts + the requested remedy.
"""

from __future__ import annotations

from .categories import Category, get as get_category
from .evidence import EvidenceRecord


def _hashes_block(rec: EvidenceRecord) -> str:
    lines = []
    for a in rec.artifacts:
        lines.append(f"  - {a.filename}  sha256={a.sha256}  ({a.size_bytes} bytes)")
    return "\n".join(lines) if lines else "  (no artifacts captured)"


def draft_report(rec: EvidenceRecord) -> str:
    """Return a bilingual (ID + EN) report draft as a single string."""
    cat: Category = get_category(rec.category)

    id_text = f"""=== BAHASA INDONESIA ===

Perihal: Laporan pelanggaran - {cat.label_id}

Kepada Tim Kepercayaan & Keamanan Instagram / pihak yang berwenang,

Saya, {rec.reporter_name} (kontak: {rec.reporter_contact}), ingin melaporkan
konten/akun pada tautan berikut karena diduga melanggar {cat.guideline_ref}:

  URL        : {rec.url}
  Judul (OG) : {rec.og_title or "-"}
  Kategori   : {cat.label_id}
  Diambil    : {rec.captured_at_utc} (UTC)

Uraian fakta (diisi oleh pelapor):
{rec.notes or "- (kosong)"}

Bukti yang dilampirkan (hash SHA-256 untuk memastikan integritas berkas):
{_hashes_block(rec)}

Permintaan tindak lanjut:
  1. Tinjau konten/akun tersebut sesuai kebijakan yang berlaku.
  2. Jika terbukti melanggar, mohon ditindak sesuai prosedur (penghapusan
     konten, pembatasan, atau penonaktifan akun).
  3. Mohon konfirmasi tindak lanjut ke kontak pelapor di atas.

Saya menyatakan bahwa informasi di atas benar sepanjang pengetahuan saya."""

    en_text = f"""=== ENGLISH ===

Subject: Abuse report - {cat.label_en}

To the Instagram Trust & Safety team / relevant authority,

I, {rec.reporter_name} (contact: {rec.reporter_contact}), am reporting the
following content/account for suspected violation of {cat.guideline_ref}:

  URL        : {rec.url}
  OG title   : {rec.og_title or "-"}
  Category   : {cat.label_en}
  Captured   : {rec.captured_at_utc} (UTC)

Statement of facts (from reporter):
{rec.notes or "- (empty)"}

Attached evidence (SHA-256 hashes for file integrity):
{_hashes_block(rec)}

Requested action:
  1. Please review the content/account under the applicable policy.
  2. If the violation is confirmed, please take appropriate enforcement
     action (content removal, restriction, or account disablement).
  3. Please confirm the outcome via the reporter contact above.

I affirm that the information above is true to the best of my knowledge."""

    channels = "\n".join(f"  - {c}" for c in cat.extra_channels)
    footer = f"""=== SUGGESTED CHANNELS / JALUR YANG DISARANKAN ===

In-app path: {cat.ig_report_path}

External / non-Instagram channels:
{channels}
"""

    return "\n\n".join([id_text, en_text, footer])
