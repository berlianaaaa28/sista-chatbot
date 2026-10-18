"""
providers/__init__.py
---------------------
Pintu masuk untuk semua API. File lain (app.py, experiment.py) cukup memakai:

    import providers
    providers.chat_detail("Gemini", riwayat, params)

Untuk MENAMBAH API baru, cukup buat satu file baru di folder ini (contoh:
mistral.py) berisi NAMA, CONFIG, chat(), dan list_models(). Lihat gemini.py
sebagai contoh. File itu otomatis terdaftar, tanpa mengedit file lain.

Cek daftar model yang tersedia untuk API key kamu:
    python -m providers
"""

import importlib
import os
import pkgutil

from .base import SYSTEM_PROMPT, ProviderError

# Label parameter untuk tampilan
NAMA_PARAM = {"temperature": "Temperature", "top_p": "Top-P", "top_k": "Top-K"}

# Temukan semua file API di folder ini (gemini.py, groq.py, cohere.py, ...)
_MODUL = {}
for _info in pkgutil.iter_modules(__path__):
    if _info.name in ("base", "__main__"):
        continue
    _modul = importlib.import_module(f".{_info.name}", __name__)
    if hasattr(_modul, "NAMA") and hasattr(_modul, "CONFIG"):
        _MODUL[_modul.NAMA] = _modul
_MODUL = dict(sorted(_MODUL.items(), key=lambda kv: kv[1].CONFIG.get("urutan", 99)))

# Pengaturan setiap API (key, model bawaan, parameter yang didukung)
PROVIDERS = {nama: modul.CONFIG for nama, modul in _MODUL.items()}


def get_api_key(nama):
    return os.getenv(PROVIDERS[nama]["key_env"], "").strip()


def get_model(nama):
    """Nama model: dari .env jika ada, jika tidak memakai model bawaan."""
    dari_env = os.getenv(PROVIDERS[nama]["model_env"], "").strip()
    return dari_env or PROVIDERS[nama]["default_model"]


def available_providers():
    """Daftar API yang API key-nya sudah diisi di .env."""
    return [nama for nama in PROVIDERS if get_api_key(nama)]


def chat_detail(nama, riwayat, params, system_prompt=None):
    """
    Kirim percakapan ke API yang dipilih.
    Mengembalikan dict: {"teks": ..., "token_input": ..., "token_output": ...}

    nama          : "Gemini", "Groq", atau "Cohere"
    riwayat       : list seperti [{"role": "user", "content": "..."}, ...]
    params        : dict seperti {"temperature": 0.5, "top_p": 0.9, "top_k": 40}
                    (parameter yang tidak didukung API otomatis dibuang)
    system_prompt : kosong = pakai SYSTEM_PROMPT SISTA
    """
    key = get_api_key(nama)
    if not key:
        raise ProviderError(
            f"API key {nama} belum diisi. Isi {PROVIDERS[nama]['key_env']} di file .env, "
            "lalu jalankan ulang aplikasi."
        )
    didukung = PROVIDERS[nama]["params"]
    params = {k: v for k, v in params.items() if k in didukung}
    return _MODUL[nama].chat(
        key, get_model(nama), riwayat, params, system_prompt or SYSTEM_PROMPT
    )


def chat(nama, riwayat, params):
    """Sama seperti chat_detail, tetapi hanya mengembalikan teks jawaban."""
    return chat_detail(nama, riwayat, params)["teks"]


def list_models(nama):
    """Daftar model yang tersedia untuk API key milik `nama`."""
    key = get_api_key(nama)
    if not key:
        raise ProviderError(f"API key {nama} belum diisi.")
    return _MODUL[nama].list_models(key)


# ---------------------------------------------------------------------------
# PENILAI KUALITAS (LLM-as-a-judge): AI memberi deskripsi singkat kualitas jawaban.
# Memakai 1 panggilan API tambahan, dengan API dan model yang sama.
# ---------------------------------------------------------------------------
PROMPT_PENILAI = """Kamu adalah penilai kualitas jawaban chatbot. Nilai jawaban berdasarkan: relevansi dengan pertanyaan, ketepatan isi, kejelasan bahasa, dan kelengkapan. Jangan menilai berdasarkan panjang jawaban saja.

Tulis HANYA satu deskripsi dalam bahasa Indonesia, maksimal 40 kata, diawali salah satu label: "Baik -", "Cukup -", atau "Kurang -", lalu alasan singkat. Tanpa format lain."""


def nilai_kualitas(nama, pertanyaan, jawaban):
    """Kembalikan deskripsi kualitas jawaban (teks pendek). Tidak pernah melempar error."""
    try:
        isi = f"Pertanyaan:\n{pertanyaan}\n\nJawaban chatbot:\n{jawaban}"
        hasil = chat_detail(
            nama,
            [{"role": "user", "content": isi}],
            {"temperature": 0.2},
            system_prompt=PROMPT_PENILAI,
        )
        teks = " ".join(hasil["teks"].split())
        return teks[:300]
    except ProviderError as e:
        return "(Penilaian AI gagal: " + " ".join(str(e).split())[:120] + ")"
