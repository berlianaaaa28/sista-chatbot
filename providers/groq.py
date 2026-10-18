"""
providers/groq.py
-----------------
Integrasi API Groq (antarmuka kompatibel OpenAI).
Parameter yang didukung: Temperature dan Top-P.
Top-K TIDAK tersedia di Groq, jadi tidak dicantumkan di bawah.
"""

from .base import ProviderError, bungkus_hasil, kirim, pesan_bersih

NAMA = "Groq"

CONFIG = {
    "urutan": 2,  # urutan tampil di dropdown aplikasi
    "key_env": "GROQ_API_KEY",
    "model_env": "GROQ_MODEL",
    "default_model": "openai/gpt-oss-120b",
    "delay": 3,  # jeda antar permintaan saat eksperimen (detik)
    "note": "Groq tidak menyediakan Top-K, jadi parameter itu dinonaktifkan.",
    "params": {
        "temperature": {"min": 0.0, "max": 2.0, "default": 0.5, "step": 0.1},
        "top_p": {"min": 0.0, "max": 1.0, "default": 0.9, "step": 0.05},
    },
}


def chat(key, model, riwayat, params, system_prompt):
    """Kirim percakapan ke Groq. Mengembalikan dict teks + token."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    body = {
        "model": model,
        "messages": [{"role": "system", "content": system_prompt}] + pesan_bersih(riwayat),
    }
    if "temperature" in params:
        body["temperature"] = params["temperature"]
    if "top_p" in params:
        body["top_p"] = params["top_p"]

    data = kirim("POST", url, headers, NAMA, body=body)
    try:
        teks = data["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError, TypeError):
        teks = ""
    if not teks.strip():
        raise ProviderError("Groq tidak mengembalikan jawaban. Coba kirim ulang pertanyaanmu.")
    u = data.get("usage") or {}
    return bungkus_hasil(teks, u.get("prompt_tokens"), u.get("completion_tokens"))


def list_models(key):
    """Daftar semua model di akun Groq."""
    data = kirim(
        "GET",
        "https://api.groq.com/openai/v1/models",
        {"Authorization": f"Bearer {key}"},
        NAMA,
    )
    return sorted(m["id"] for m in data.get("data", []))
