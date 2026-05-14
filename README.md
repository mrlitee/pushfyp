# pushfyp

Toolkit + **website** untuk optimasi postingan **Threads** (Meta) secara **organik**.
Bantu kamu naik FYP dengan cara legit: analisa konten, generate hook kuat,
rekomendasi hashtag, dan auto-post di jam optimal via **Threads Graph API resmi**.

> ⚠️ Tool ini **tidak** memanipulasi engagement (views/likes/shares).
> Manipulasi engagement melanggar ToS Meta dan bisa men-suspend akun permanen.

---

## Mode Pemakaian

### 🌐 Mode Web (UI)

Browser-based interface. Cocok untuk pemakaian sehari-hari.

```bash
git clone https://github.com/mrlitee/pushfyp.git
cd pushfyp
pip install -e ".[web]"
pushfyp serve
```

Buka: **http://127.0.0.1:8000**

UI punya 4 tab:
- **Analyze** — paste link Threads → skor 0-100 + saran
- **Hook** — generate 10 variasi pembuka
- **Hashtags** — rekomendasi per niche
- **Schedule** — auto-post via API resmi

### 💻 Mode CLI

```bash
pip install -e .
pushfyp analyze https://www.threads.net/@user/post/ABC
pushfyp hook "topik kamu"
pushfyp hashtags --niche bisnis
pushfyp schedule --text "..." --at "2026-05-15 08:00"
```

---

## Endpoint API (Mode Web)

| Method | Path | Body / Query | Fungsi |
|---|---|---|---|
| GET  | `/` | — | UI |
| GET  | `/health` | — | health check |
| POST | `/api/analyze` | `{"url": "..."}` | analisa link |
| POST | `/api/hook` | `{"topic": "...", "use_llm": true}` | generate hook |
| GET  | `/api/niches` | — | list niche |
| GET  | `/api/hashtags?niche=tech&count=5` | query | rekomendasi tag |
| POST | `/api/schedule` | `{"text": "...", "when": "ISO8601"}` | enqueue post |
| POST | `/api/post` | `{"text": "..."}` | post langsung |

Docs auto-generated: **http://127.0.0.1:8000/docs**

---

## Deploy

### Docker
```bash
docker build -t pushfyp .
docker run -p 8000:8000 --env-file .env pushfyp
```

### Termux (Android)
```bash
pkg install python git -y
git clone https://github.com/mrlitee/pushfyp.git
cd pushfyp && pip install -e ".[web]"
pushfyp serve --host 0.0.0.0 --port 8080
# akses dari device sama: http://127.0.0.1:8080
```

### Railway / Render / Fly.io
Tinggal connect repo. `Procfile` dan `Dockerfile` sudah siap.

### Vercel (serverless)
Endpoint API bisa di-port ke Vercel functions, tapi `schedule` butuh long-running process — pakai Railway/Render.

---

## Setup .env (untuk fitur post & schedule)

```bash
cp .env.example .env
```

Isi:
```
THREADS_ACCESS_TOKEN=xxx
THREADS_USER_ID=xxx
OPENAI_API_KEY=sk-xxx   # opsional, untuk hook LLM
```

Dapatkan credentials Threads: [developers.facebook.com/docs/threads](https://developers.facebook.com/docs/threads)

---

## Struktur

```
pushfyp/
├── src/pushfyp/
│   ├── analyzer.py       # Link → metadata (Open Graph) → skor FYP
│   ├── hook.py           # Generator hook
│   ├── hashtag.py        # Rekomendasi per niche
│   ├── schedule.py       # APScheduler untuk auto-post
│   ├── threads_api.py    # Klien Threads Graph API
│   ├── cli.py            # CLI 'pushfyp'
│   ├── config.py
│   ├── data/hashtags.json
│   └── web/
│       ├── main.py        # FastAPI app
│       ├── templates/
│       │   └── index.html
│       └── static/
│           ├── style.css
│           └── app.js
├── Dockerfile
├── Procfile
├── pyproject.toml
├── requirements.txt
└── .env.example
```

---

## Lisensi

MIT
