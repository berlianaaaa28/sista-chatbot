# SISTA — Smart Information System Assistant

Chatbot asisten AI serbaguna (profil umum, persona ramah dan sistematis). Dibuat untuk tugas mata kuliah **Sistem Cerdas**.

- Bahasa: Python + Streamlit (aplikasi web yang berjalan di laptop sendiri, `localhost`)
- Teknik prompting: **Zero-Shot Prompting** (instruksi tanpa contoh tanya-jawab)
- Parameter: **Temperature, Top-P, Top-K** (hanya yang didukung API terpilih yang ditampilkan)
- API: **Gemini** (Groq dan Cohere ditambahkan anggota lain pada tahap berikutnya)

---

## 1. Instalasi (Windows, terminal VS Code)

Buka folder `sista-chatbot` di VS Code, lalu buka terminal (`Ctrl + ``) dan jalankan satu per satu:

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Jika `activate` ditolak (error "running scripts is disabled"), jalankan sekali:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` lalu ulangi `venv\Scripts\activate`.
Jika terminalnya Command Prompt (bukan PowerShell), cukup pakai perintah yang sama.

## 2. Mengisi API key

1. Salin `.env.example` menjadi `.env`:
   `copy .env.example .env`
2. Buka `.env`, isi API key milikmu. **Cukup isi satu** (milikmu sendiri); API yang key-nya kosong tidak muncul di aplikasi.

| API | Daftar / ambil key | Catatan |
|---|---|---|
| Gemini | https://aistudio.google.com/apikey | Login akun Google, klik *Create API key* |
| Groq | https://console.groq.com/keys | Daftar, klik *Create API Key* |
| Cohere | https://dashboard.cohere.com/api-keys | Pakai *Trial key* (gratis, hanya untuk belajar) |

Jangan membagikan file `.env` dan jangan mengunggahnya ke GitHub (sudah masuk `.gitignore`).

## 3. Memastikan nama model benar

Nama model gratis bisa berganti. Jalankan:

```
python -m providers
```

Daftar model untuk key-mu akan tampil. Jika model bawaan tidak ada, tulis nama model yang ada di `.env`, misalnya `GEMINI_MODEL=nama-model-dari-daftar`.

## 4. Menjalankan aplikasi

```
streamlit run app.py
```

Browser terbuka otomatis di `http://localhost:8501`. Untuk berhenti, tekan `Ctrl + C` di terminal.
