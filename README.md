# SISTA — Smart Information System Assistant

Chatbot asisten AI serbaguna (profil umum, persona ramah dan sistematis). Dibuat untuk tugas mata kuliah **Sistem Cerdas**.

- Bahasa: Python + Streamlit (aplikasi web yang berjalan di laptop sendiri, `localhost`)
- Teknik prompting: **Zero-Shot Prompting** (instruksi tanpa contoh tanya-jawab)
- Parameter: **Temperature, Top-P, Top-K** (hanya yang didukung API terpilih yang ditampilkan)
- API: **Gemini**, **Groq**, **Cohere** (satu API per anggota; semuanya punya akses gratis)

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
- **Tab Eksperimen**: uji cepat. Pilih parameter yang diuji, isi nilai (pisahkan koma), isi pertanyaan (satu per baris, boleh banyak), klik *Jalankan eksperimen*. Semua kombinasi tercatat di CSV yang sama.
- CSV bisa diunduh dari tab Eksperimen atau dibuka langsung di Excel.

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

## 6. Struktur file

```
sista-chatbot/
├── app.py            tampilan Streamlit
├── providers/        semua urusan API
│   ├── __init__.py   pintu masuk, pendaftaran API otomatis, penilai kualitas AI
│   ├── base.py       system prompt Zero-Shot dan fungsi bantu bersama
│   ├── gemini.py     integrasi Gemini
│   ├── groq.py       integrasi Groq
│   └── cohere.py     integrasi Cohere
├── ui_eksperimen.py  tampilan tab Eksperimen
├── experiment.py     mencatat hasil ke CSV dan menjalankan eksperimen
├── requirements.txt  daftar library
├── .env.example      contoh file API key
├── .gitignore
├── results/          hasil eksperimen (CSV)
└── docs/             backlog, tabel eksperimen, kerangka presentasi
```

## 7. Zero-Shot System Prompt

Ada di `providers/base.py` (variabel `SYSTEM_PROMPT`). Berisi peran, kepribadian, dan aturan menjawab **tanpa contoh pasangan input-output**, sehingga termasuk Zero-Shot Prompting. Prompt yang sama dipakai semua API.

## 8. Perbedaan dukungan parameter

| API | Temperature | Top-P | Top-K |
|---|---|---|---|
| Gemini | ya (`temperature`) | ya (`topP`) | ya (`topK`) |
| Groq | ya | ya | **tidak** (dinonaktifkan di aplikasi) |
| Cohere | ya | ya (`p`) | ya (`k`) — *perlu dikonfirmasi saat uji* |

Jika Cohere menolak `k`, hapus baris `"top_k": {...}` di `CONFIG` pada `providers/cohere.py`.

## 9. Error umum dan solusinya

| Pesan | Penyebab / solusi |
|---|---|
| `API key ... belum diisi` | `.env` belum dibuat atau key kosong. Isi lalu jalankan ulang aplikasi. |
| `API key ... ditolak` | Key salah/ada spasi, atau key sudah dicabut. Buat key baru. |
| `Model tidak ditemukan` | Nama model salah. Jalankan `python -m providers`, pakai nama dari daftar. |
| `Kuota gratis habis` | Tunggu 1-2 menit; untuk Cohere ingat batas 1.000 panggilan/bulan. |
| `streamlit tidak dikenali` | Virtual environment belum aktif. Jalankan `venv\Scripts\activate`. |
| `ModuleNotFoundError` | Jalankan `pip install -r requirements.txt` lagi. |
| `.env` tidak terbaca | Pastikan namanya `.env` (bukan `.env.txt`) dan ada di folder yang sama dengan `app.py`. |

## 10. Batasan yang perlu disebut di laporan

- Perbandingan antar-API tidak bisa disimpulkan dari parameter saja, karena modelnya berbeda. Eksperimen parameter dilakukan **di dalam satu API** dengan model tetap.
- Deskripsi kualitas dibuat oleh AI yang sama dengan yang menjawab, sehingga bisa bias. Jelaskan ini di laporan.
- Hasil AI bersifat acak (terutama pada Temperature tinggi); ulangi eksperimen jika ingin melihat konsistensi.
- Free tier Gemini dapat memakai data input untuk memperbaiki produk Google; jangan masukkan data pribadi.
- Trial key Cohere tidak boleh dipakai untuk keperluan komersial.
