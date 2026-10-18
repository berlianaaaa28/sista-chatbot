# SISTA — Smart Information System Assistant

Chatbot asisten AI serbaguna (profil umum, persona ramah dan sistematis). Dibuat untuk tugas mata kuliah **Sistem Cerdas**.

- Bahasa: Python + Streamlit (aplikasi web yang berjalan di laptop sendiri, `localhost`)
- Teknik prompting: **Zero-Shot Prompting** (instruksi tanpa contoh tanya-jawab)
- Parameter: **Temperature, Top-P, Top-K** (hanya yang didukung API terpilih yang ditampilkan)
- API: **Gemini**, **Groq** (Cohere ditambahkan pada tahap berikutnya)

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

## 5. Cara memakai

- **Sidebar**: pilih API, lihat model aktif, atur slider Temperature / Top-P / Top-K, tombol bersihkan percakapan.
- **Tab Chat**: tulis pertanyaan di kolom bawah. **Setiap pertanyaan otomatis tercatat** sebagai satu baris di `results/hasil_pengujian.csv`, dengan parameter dari slider saat itu.
- **Sidebar > Pencatatan ke CSV**: pilih label "Parameter yang sedang diuji" (hanya untuk kolom `parameter_diuji`), isi nama peneliti, dan nyalakan/matikan penilaian kualitas oleh AI.
- CSV bisa dibuka langsung di Excel.

### Kolom CSV (`results/hasil_pengujian.csv`)
| Kolom | Isi |
|---|---|
| waktu, sumber | kapan dan dari mana (chat / eksperimen) |
| peneliti, api, model | siapa, API apa, model apa |
| parameter_diuji | label dari sidebar / tab Eksperimen |
| temperature, top_p, top_k | nilai yang dipakai (top_k kosong jika API tidak mendukung) |
| pertanyaan, jawaban | isi tanya-jawab |
| token_input, token_output | jumlah token dari data pemakaian API (bukan perkiraan) |
| jumlah_kata, jumlah_kalimat | dihitung otomatis dari jawaban |
| deskripsi_kualitas | penilaian singkat oleh AI (label Baik / Cukup / Kurang + alasan) |
| status | OK atau pesan error |

Catatan token:
- `token_input` di Chat termasuk system prompt dan seluruh riwayat percakapan, jadi makin lama makin besar.
- `token_output` pada Gemini = total token dikurangi token input, sehingga sudah termasuk token "berpikir" model.
- Token untuk panggilan penilai AI tidak dihitung di kolom ini.
- Jika API tidak memberi data token (mungkin pada Cohere), kolomnya kosong.

Catatan penilai AI:
- Penilaian memakai **1 panggilan API tambahan** per jawaban, dengan API dan model yang sama, jadi kuota habis dua kali lebih cepat. Matikan lewat kotak centang di sidebar jika perlu.
- AI menilai dirinya sendiri, jadi anggap ini penilaian awal. Untuk laporan, tulis keterbatasan ini dan tambahkan pengamatan sendiri.
