# ig_report_kit

Toolkit dokumentasi dan pelaporan pelanggaran di Instagram —
**dengan cara yang sah**.

Tool ini membantu korban / advokat resmi untuk:

1. **Menangkap bukti publik** (HTML + preview + hash SHA-256) dari URL akun /
   postingan Instagram yang melakukan pelanggaran.
2. **Menyusun draft laporan dua bahasa (ID + EN)** yang faktual, siap ditempel
   ke form resmi Instagram atau dilampirkan ke laporan polisi / Kominfo /
   NCMEC.
3. **Membundel semuanya menjadi satu PDF** yang rapi untuk lampiran.

> **Yang tidak dilakukan tool ini:** mass-report, auto-report, pakai akun palsu,
> atau apa pun yang bertujuan "membuat akun target banned". Praktik seperti itu
> melanggar Terms of Service Meta, biasanya justru membuat **akunmu** yang
> ditindak, dan pada banyak yurisdiksi bisa dikualifikasi sebagai
> _coordinated harassment_ atau _computer misuse_.

## Kategori yang didukung

| key | ID | EN |
|---|---|---|
| `scam` | Penipuan / Scam | Fraud / Scam |
| `threat` | Ancaman Kekerasan | Violent threat |
| `doxxing` | Pembocoran data pribadi | Doxxing |
| `harassment` | Pelecehan / Perundungan | Harassment / Bullying |
| `impersonation` | Akun palsu / Impersonasi | Impersonation |
| `csam` | Eksploitasi seksual anak | Child sexual abuse material |

Untuk **CSAM**, langkah pertama selalu
<https://report.cybertip.org/> (NCMEC) — bukan menunggu proses Instagram.

## Instalasi

```bash
cd ig_report_kit
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Pemakaian

### 1. Capture bukti

```bash
python -m ig_report_kit capture \
  --url "https://www.instagram.com/example_public_account/" \
  --category scam \
  --reporter-name "Nama Kamu" \
  --reporter-contact "email@kamu" \
  --notes "Tanggal 2026-05-10 akun ini DM saya link investasi palsu." \
  --out ./cases
```

Hasil: `./cases/<timestamp>_<slug>/` berisi `page.html`, `preview.jpg`
(jika tersedia), dan `evidence.json` dengan hash SHA-256 tiap file.

### 2. Buat draft laporan

```bash
python -m ig_report_kit draft --case ./cases/<timestamp>_<slug>
```

Menghasilkan `report.txt` berisi versi Bahasa Indonesia + English + daftar
jalur resmi yang direkomendasikan untuk kategori tersebut.

### 3. Bundel jadi PDF

```bash
python -m ig_report_kit bundle --case ./cases/<timestamp>_<slug>
```

Menghasilkan `bundle.pdf` (manifest + preview image + report draft) yang siap
dilampirkan ke form Help Center / polisi / NCMEC.

### Daftar kategori

```bash
python -m ig_report_kit categories
```

## Eskalasi

Lihat [`ESCALATION.md`](./ESCALATION.md) untuk daftar lengkap jalur resmi:
Instagram in-app → Help Center → Kominfo / Polri / NCMEC / IC3.

## Etika & batasan

- Hanya mengambil **halaman publik** dengan User-Agent yang jujur. Tidak
  login, tidak bypass rate limit, tidak meng-scrape konten private.
- Satu kasus = satu invocation. Tidak ada mode batch / otomatisasi massal
  secara desain.
- Jangan gunakan tool ini untuk menyerang akun yang tidak benar-benar
  melanggar. Laporan palsu berulang adalah pelanggaran ToS Meta dan
  berpotensi pidana (mis. Pasal 310-311 KUHP + UU ITE di Indonesia).

## Lisensi

Lihat file `LICENSE` di root repo `pushfyp` (akan ditambahkan terpisah).
