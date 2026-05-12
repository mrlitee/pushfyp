# 🚀 Push FYP Threads

**Auto Push FYP Tool untuk Threads** - Boost postingan Threads ke For You Page (FYP) secara otomatis hanya dengan memasukkan link postingan!

Tool ini menggunakan multiple akun untuk memberikan engagement (like, repost, dan comment) pada postingan target, sehingga meningkatkan peluang postingan masuk ke FYP.

---

## ✨ Fitur

- 🔗 **Cukup pakai link** - Input link postingan Threads, tool handle sisanya
- 👍 **Auto Like** - Like otomatis dari multiple akun
- 🔄 **Auto Repost** - Repost otomatis untuk boost reach
- 💬 **Auto Comment** - Komentar random dari daftar yang sudah disiapkan
- 🤖 **Anti-Detection** - Random user agent, human-like typing, random delay
- 📊 **Laporan Hasil** - Ringkasan lengkap setelah proses selesai
- ⚙️ **Konfigurasi Mudah** - Setup via file `.env`

---

## 📋 Requirements

- Python 3.8+
- Google Chrome browser
- Akun Threads/Instagram (minimal 1, rekomendasi 5+)

---

## 🚀 Instalasi

```bash
# Clone repository
git clone https://github.com/mrlitee/pushfyp.git
cd pushfyp

# Install dependencies
pip install -r requirements.txt

# Copy dan edit konfigurasi
cp .env.example .env
```

---

## ⚙️ Konfigurasi

Edit file `.env` dengan akun dan pengaturan:

```env
# Daftar akun (format: username:password, pisah dengan koma)
ACCOUNTS=akun1:pass1,akun2:pass2,akun3:pass3

# Pengaturan
HEADLESS=true          # true = tanpa tampilan browser
DELAY_MIN=5            # Delay minimum (detik)
DELAY_MAX=15           # Delay maximum (detik)
LIKE=true              # Aktifkan auto like
REPOST=true            # Aktifkan auto repost
COMMENT=true           # Aktifkan auto comment

# Komentar random (pisahkan dengan |)
COMMENTS=keren banget!|mantap|bagus sekali|suka ini|top!|amazing|nice post|fire!
```

---

## 📖 Cara Penggunaan

### Metode 1: Langsung dengan link

```bash
python pushfyp.py https://www.threads.net/@username/post/XXXXX
```

### Metode 2: Input interaktif

```bash
python pushfyp.py
# Lalu masukkan link saat diminta
```

### Format Link yang Didukung

```
https://www.threads.net/@username/post/XXXXX
https://www.threads.net/t/XXXXX
```

---

## 📊 Contoh Output

```
╔══════════════════════════════════════════════════╗
║                                                  ║
║  🚀 PUSH FYP THREADS - Auto Engagement Tool     ║
║                                                  ║
╚══════════════════════════════════════════════════╝

  [→] Target: https://www.threads.net/@target/post/ABC123

  [ℹ] Ditemukan 3 akun
  [ℹ] Mode: Like Repost Comment

  ┌─── Akun 1/3: @akun1 ───┐
    [✓] Login berhasil sebagai @akun1
    [✓] Postingan berhasil dimuat
    [✓] Berhasil like postingan
    [✓] Berhasil repost postingan
    [✓] Berhasil komentar: 'keren banget!'
  └──────────────────────────────────────┘

══════════════════════════════════════════════════
  📊 RINGKASAN HASIL
══════════════════════════════════════════════════
  Total Akun      : 3
  Login Berhasil  : 3/3
  Like Berhasil   : 3/3
  Repost Berhasil : 3/3
  Comment Berhasil: 3/3

  🚀 Postingan berhasil di-push! Engagement +9
```

---

## 🛡️ Tips Keamanan

1. **Gunakan akun dummy** - Jangan gunakan akun utama
2. **Jangan berlebihan** - 5-10 akun per postingan sudah cukup
3. **Atur delay** - Jangan terlalu cepat, biarkan delay 5-15 detik
4. **Rotasi akun** - Jangan gunakan akun yang sama berulang kali
5. **Gunakan proxy** (opsional) - Untuk keamanan ekstra

---

## 📁 Struktur File

```
pushfyp/
├── pushfyp.py          # Script utama (entry point)
├── threads_actions.py  # Modul aksi (login, like, repost, comment)
├── browser.py          # Browser management & anti-detection
├── config.py           # Konfigurasi & parser
├── requirements.txt    # Dependencies Python
├── .env.example        # Template konfigurasi
├── .gitignore          # Ignore rules
└── README.md           # Dokumentasi
```

---

## ⚠️ Disclaimer

Tool ini dibuat untuk tujuan edukasi dan riset. Penggunaan tool ini sepenuhnya menjadi tanggung jawab pengguna. Penulis tidak bertanggung jawab atas penyalahgunaan tool ini.

---

## 📝 License

MIT License - Bebas digunakan dan dimodifikasi.

---

## 🤝 Kontribusi

Pull requests welcome! Untuk perubahan besar, silakan buka issue terlebih dahulu.

---

**Made with ❤️ by [@mrlitee](https://github.com/mrlitee)**
