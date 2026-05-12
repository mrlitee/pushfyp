# pushfyp

Toolkit optimasi postingan **Threads** (Meta) secara **organik**.
Bantu kamu naik FYP dengan cara legit: analisa konten, generate hook kuat,
rekomendasi hashtag, dan auto-post di jam optimal via **Threads Graph API resmi**.

> ⚠️ Tool ini **tidak** memanipulasi engagement (views/likes/shares). Jika kamu
> mencari bot engagement, tool ini bukan itu — dan memang tidak akan pernah jadi itu.
> Manipulasi engagement melanggar Terms of Service Meta dan bisa menyebabkan akun
> di-suspend permanen.

## Fitur

| Command | Fungsi |
|---|---|
| `pushfyp analyze <url>` | Analisa link postingan Threads publik → skor 0-100 + saran perbaikan |
| `pushfyp hook "<topik>"` | Generate 10 variasi kalimat pembuka (rule-based atau LLM) |
| `pushfyp hashtags --niche <niche>` | Rekomendasi hashtag per niche |
| `pushfyp list-niches` | List niche yang tersedia |
| `pushfyp schedule --text "..." --at "..."` | Auto-post di jam tertentu via API resmi |
| `pushfyp post "..."` | Langsung post ke Threads via API resmi |

## Install

```bash
git clone https://github.com/mrlitee/pushfyp.git
cd pushfyp
python -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env      # isi credentials kalau mau pakai scheduler/post
```

## Quick Start

### 1. Analisa postingan (tanpa login, cukup link publik)

```bash
pushfyp analyze https://www.threads.net/@username/post/C5abcDEF
```

Output:
```
┌─ FYP Readiness ─────────────────┐
│ Score: 72/100                   │
│ Author: @username               │
│ Caption: Kenapa banyak startup..│
└─────────────────────────────────┘

Breakdown:
  caption_length  20
  hook            18
  hashtags        15
  media           8
  cta             15
  readability     12

Saran perbaikan:
  1. Tidak ada media. Postingan dengan gambar/video punya dwell-time lebih tinggi di FYP.
```

### 2. Generate hook

```bash
pushfyp hook "belajar coding otodidak"
```

### 3. Rekomendasi hashtag

```bash
pushfyp hashtags --niche tech --count 4
# -> #webdev #AI #coding #javascript #fyp #trending
```

### 4. Auto-post di jam optimal

```bash
# butuh THREADS_ACCESS_TOKEN dan THREADS_USER_ID di .env
pushfyp schedule --text "Isi postingan..." --at "2026-05-13 08:00"
```

## Dapat Credentials Threads API

1. Daftar di [developers.facebook.com](https://developers.facebook.com/docs/threads)
2. Buat Meta App → tambahkan produk **Threads API**
3. Generate access token untuk akun Threads kamu
4. Salin `user_id` + `access_token` ke `.env`

## Struktur

```
pushfyp/
├── src/pushfyp/
│   ├── analyzer.py      # Link → metadata via Open Graph → skor FYP
│   ├── hook.py          # Generator hook
│   ├── hashtag.py       # Rekomendasi per niche
│   ├── schedule.py      # APScheduler untuk auto-post
│   ├── threads_api.py   # Klien Threads Graph API
│   ├── cli.py           # CLI entry point
│   └── data/hashtags.json
├── examples/
├── pyproject.toml
└── .env.example
```

## Roadmap

- [ ] Best-time analyzer (pelajari jam aktif follower kamu sendiri)
- [ ] Thread-chain builder (rangkai multi-post)
- [ ] Dashboard web (Next.js)
- [ ] Cross-post dari X/IG ke Threads

## Lisensi

MIT
