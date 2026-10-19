"""
experiment.py
-------------
Mencatat hasil pengujian ke CSV dan menjalankan eksperimen parameter.

Setiap pertanyaan (dari tab Chat maupun tab Eksperimen) menjadi SATU baris di
results/hasil_pengujian.csv, lengkap dengan parameter, jumlah token, jumlah
kata/kalimat, dan deskripsi kualitas dari penilai AI.

Aturan eksperimen:
  - Hanya SATU parameter yang diubah per eksperimen; parameter lain tetap.
  - Pertanyaan dan system prompt sama untuk semua nilai.
  - Satu eksperimen = satu API dan satu model.
"""

import csv
import re
import time
from datetime import datetime
from pathlib import Path

import pandas as pd

import providers
from providers import ProviderError

FOLDER_HASIL = Path(__file__).parent / "results"
FILE_CSV = FOLDER_HASIL / "hasil_pengujian.csv"

KOLOM = [
    "waktu",
    "sumber",            # chat atau eksperimen
    "peneliti",
    "nomor_kombinasi",   # nomor dari tabel kombinasi struktur dan teknik prompting (dosen)
    "api",
    "model",
    "parameter_diuji",   # kosong jika tidak ada parameter khusus yang diuji
    "temperature",
    "top_p",
    "top_k",             # kosong jika API tidak mendukung Top-K
    "pertanyaan",
    "jawaban",
    "token_input",
    "token_output",
    "jumlah_kata",
    "jumlah_kalimat",
    "deskripsi_kualitas",
    "status",
]


def hitung_kata(teks):
    return len(re.findall(r"\w+", teks))


def hitung_kalimat(teks):
    """Hitung kalimat (juga baris poin-poin) pada jawaban."""
    bagian = re.split(r"(?<=[.!?])\s+|\n+", teks.strip())
    return len([b for b in bagian if b.strip()])


def ringkas_baris(baris):
    """Ringkasan satu baris hasil (token, kata, kalimat, kualitas) untuk ditampilkan."""
    tin, tout = baris["token_input"], baris["token_output"]
    teks = (
        f"Token: {tin if tin != '' else '-'} masuk / {tout if tout != '' else '-'} keluar"
        f" · {baris['jumlah_kata']} kata · {baris['jumlah_kalimat']} kalimat"
    )
    if baris["deskripsi_kualitas"]:
        teks += f"\n\nKualitas (penilaian AI): {baris['deskripsi_kualitas']}"
    return teks


def _perbarui_header_lama():
    """
    Jika CSV lama dibuat sebelum ada kolom baru (misalnya nomor_kombinasi),
    tulis ulang dengan header terbaru. Data lama tidak hilang; kolom baru dikosongkan.
    """
    if not FILE_CSV.exists() or FILE_CSV.stat().st_size == 0:
        return
    with open(FILE_CSV, newline="", encoding="utf-8-sig") as f:
        pembaca = csv.DictReader(f)
        if pembaca.fieldnames == KOLOM:
            return
        isi = list(pembaca)
    with open(FILE_CSV, "w", newline="", encoding="utf-8-sig") as f:
        penulis = csv.DictWriter(f, fieldnames=KOLOM, extrasaction="ignore")
        penulis.writeheader()
        for baris in isi:
            penulis.writerow({k: baris.get(k, "") for k in KOLOM})


def simpan_baris(baris):
    """Tambahkan satu baris hasil ke CSV (file dibuat otomatis jika belum ada)."""
    FOLDER_HASIL.mkdir(exist_ok=True)
    _perbarui_header_lama()
    baru = not FILE_CSV.exists() or FILE_CSV.stat().st_size == 0
    # utf-8-sig supaya huruf Indonesia tampil benar saat dibuka di Excel
    with open(FILE_CSV, "a", newline="", encoding="utf-8-sig") as f:
        penulis = csv.DictWriter(f, fieldnames=KOLOM)
        if baru:
            penulis.writeheader()
        penulis.writerow(baris)


def baca_csv():
    """Baca semua hasil tersimpan. Mengembalikan DataFrame, atau None jika belum ada."""
    if not FILE_CSV.exists() or FILE_CSV.stat().st_size == 0:
        return None
    return pd.read_csv(FILE_CSV, encoding="utf-8-sig", dtype=str).fillna("")


def tanya(api, riwayat, params, parameter_diuji="", sumber="chat", peneliti="",
          nilai_ai=True, catat_gagal=True, model=None, nomor_kombinasi=""):
    """
    Kirim pertanyaan (pesan terakhir di `riwayat`) ke API, lalu catat satu baris ke CSV.
    Mengembalikan dict baris. Jika gagal, baris["status"] diawali "ERROR".

    model           : kosong = model dari .env / bawaan
    nomor_kombinasi : nomor dari tabel kombinasi struktur dan teknik prompting (opsional)
    """
    didukung = providers.PROVIDERS[api]["params"]
    params = {k: v for k, v in params.items() if k in didukung}
    pertanyaan = riwayat[-1]["content"]
    model = model or providers.get_model(api)

    baris = {
        "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sumber": sumber,
        "peneliti": peneliti,
        "nomor_kombinasi": nomor_kombinasi,
        "api": api,
        "model": model,
        "parameter_diuji": parameter_diuji,
        # parameter yang tidak didukung API dikosongkan
        "temperature": params.get("temperature", ""),
        "top_p": params.get("top_p", ""),
        "top_k": params.get("top_k", ""),
        "pertanyaan": pertanyaan,
        "jawaban": "",
        "token_input": "",
        "token_output": "",
        "jumlah_kata": "",
        "jumlah_kalimat": "",
        "deskripsi_kualitas": "",
        "status": "OK",
    }

    try:
        hasil = providers.chat_detail(api, riwayat, params, model=model)
    except ProviderError as e:
        baris["status"] = f"ERROR: {e}"
        if catat_gagal:
            simpan_baris(baris)
        return baris

    teks = hasil["teks"]
    baris["jawaban"] = teks
    baris["token_input"] = hasil["token_input"]
    baris["token_output"] = hasil["token_output"]
    baris["jumlah_kata"] = hitung_kata(teks)
    baris["jumlah_kalimat"] = hitung_kalimat(teks)
    if nilai_ai:
        baris["deskripsi_kualitas"] = providers.nilai_kualitas(api, pertanyaan, teks, model=model)
    simpan_baris(baris)
    return baris


def jalankan_eksperimen(api, param_diuji, daftar_nilai, params_tetap, daftar_pertanyaan,
                        peneliti="", nilai_ai=True, on_progress=None, model=None,
                        nomor_kombinasi=""):
    """
    Jalankan eksperimen: untuk setiap pertanyaan, ubah `param_diuji` ke setiap nilai
    di `daftar_nilai`; parameter lain mengikuti `params_tetap`.
    Setiap hasil langsung disimpan ke CSV. Mengembalikan list baris hasil.
    """
    didukung = providers.PROVIDERS[api]["params"]
    if param_diuji not in didukung:
        raise ProviderError(f"{api} tidak mendukung parameter {param_diuji}.")

    jeda = providers.PROVIDERS[api]["delay"]
    total = len(daftar_pertanyaan) * len(daftar_nilai)
    hasil = []
    selesai = 0

    for pertanyaan in daftar_pertanyaan:
        for nilai in daftar_nilai:
            params = {k: v for k, v in params_tetap.items() if k in didukung}
            params[param_diuji] = nilai
            baris = tanya(
                api, [{"role": "user", "content": pertanyaan}], params,
                parameter_diuji=param_diuji, sumber="eksperimen",
                peneliti=peneliti, nilai_ai=nilai_ai,
                model=model, nomor_kombinasi=nomor_kombinasi,
            )
            hasil.append(baris)
            selesai += 1
            if on_progress:
                on_progress(selesai, total, baris)
            if selesai < total:
                time.sleep(jeda)  # jeda agar tidak melewati batas permintaan per menit

    return hasil
