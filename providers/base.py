"""
providers/base.py
-----------------
Bagian yang dipakai bersama oleh semua API:
  - System prompt Zero-Shot SISTA
  - Kelas error ProviderError
  - Fungsi bantu untuk mengirim permintaan HTTP dan membungkus hasil
"""

from pathlib import Path

import requests
from dotenv import load_dotenv

# Baca API key dari file .env (di folder utama proyek, sejajar dengan app.py)
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


# ---------------------------------------------------------------------------
# ZERO-SHOT SYSTEM PROMPT
# Berisi profil + persona + aturan menjawab, TANPA contoh pasangan
# pertanyaan-jawaban. Itulah yang disebut Zero-Shot Prompting.
# Prompt yang sama dipakai oleh semua API.
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """Kamu adalah SISTA (Smart Information System Assistant), asisten AI serbaguna yang membantu pengguna menjawab pertanyaan, menjelaskan konsep, menulis, merangkum, dan memberi ide.

Kepribadian:
Ramah, sopan, profesional, sistematis, dan mudah dipahami.

Aturan menjawab:
1. Jawab dengan bahasa yang sama dengan bahasa pertanyaan pengguna.
2. Jelaskan dengan bahasa sederhana, urut, dan terstruktur.
3. Jangan mengarang informasi. Jika tidak tahu atau tidak yakin, katakan terus terang.
4. Jika pertanyaan kurang jelas, ajukan satu pertanyaan klarifikasi.
5. Buat jawaban ringkas (sekitar 200 kata atau kurang) kecuali pengguna meminta penjelasan lebih rinci.
6. Tolak dengan sopan permintaan yang berbahaya atau melanggar hukum."""


class ProviderError(Exception):
    """Error dengan pesan yang sudah ramah untuk pengguna."""


def detail_error(respons):
    """Ambil teks pesan error dari respons API (formatnya beda-beda)."""
    try:
        data = respons.json()
        if isinstance(data, dict):
            err = data.get("error")
            if isinstance(err, dict) and err.get("message"):
                return str(err["message"])[:300]
            if isinstance(err, str):
                return err[:300]
            if data.get("message"):
                return str(data["message"])[:300]
    except ValueError:
        pass
    return respons.text[:300]


def pesan_http(nama, status, detail):
    """Pesan error berbahasa Indonesia berdasarkan kode status HTTP."""
    if status in (401, 403):
        awal = f"API key {nama} ditolak. Pastikan key benar, tanpa spasi, dan akunmu punya akses."
    elif status == 404:
        awal = (
            f"Model tidak ditemukan di {nama}. Cek nama model di file .env "
            "(jalankan `python -m providers` untuk melihat daftar model)."
        )
    elif status == 429:
        awal = f"Kuota gratis {nama} habis atau permintaan terlalu cepat. Tunggu 1-2 menit lalu coba lagi."
    elif status == 400:
        awal = f"{nama} menolak permintaan (kemungkinan parameter atau nama model tidak cocok)."
    elif status >= 500:
        awal = f"Server {nama} sedang bermasalah. Coba lagi beberapa saat."
    else:
        awal = f"{nama} mengembalikan error {status}."
    return f"{awal} Detail: {detail}"


def kirim(metode, url, headers, nama, body=None, params=None):
    """Kirim permintaan HTTP dan ubah semua kegagalan menjadi ProviderError."""
    try:
        respons = requests.request(
            metode, url, headers=headers, json=body, params=params, timeout=60
        )
    except requests.exceptions.Timeout:
        raise ProviderError(f"{nama} terlalu lama merespons (lebih dari 60 detik). Coba lagi.")
    except requests.exceptions.ConnectionError:
        raise ProviderError("Tidak bisa terhubung ke internet. Periksa koneksimu lalu coba lagi.")
    except requests.exceptions.RequestException as e:
        raise ProviderError(f"Gagal menghubungi {nama}: {e}")

    if respons.status_code != 200:
        raise ProviderError(pesan_http(nama, respons.status_code, detail_error(respons)))
    try:
        return respons.json()
    except ValueError:
        raise ProviderError(f"Jawaban dari {nama} bukan JSON yang valid.")


def pesan_bersih(riwayat):
    """Ambil hanya role dan content dari riwayat percakapan."""
    return [{"role": m["role"], "content": m["content"]} for m in riwayat]


def bungkus_hasil(teks, masuk, keluar):
    """Bungkus jawaban + jumlah token. Token kosong ("") jika API tidak memberikannya."""
    return {
        "teks": teks,
        "token_input": masuk if isinstance(masuk, (int, float)) else "",
        "token_output": keluar if isinstance(keluar, (int, float)) else "",
    }
