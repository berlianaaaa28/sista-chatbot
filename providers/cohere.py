"""
providers/cohere.py
-------------------
Integrasi API Cohere (v2 chat).
Parameter: Temperature, p (Top-P), k (Top-K).
"""

from .base import ProviderError, bungkus_hasil, kirim, pesan_bersih

NAMA = "Cohere"

CONFIG = {
    "urutan": 3,  # urutan tampil di dropdown aplikasi
    "key_env": "COHERE_API_KEY",
    "model_env": "COHERE_MODEL",
    "default_model": "command-a-03-2025",
    "delay": 4,  # trial key: 20 permintaan per menit
    "note": (
        "Top-K di Cohere bernama 'k'. Dukungannya perlu dikonfirmasi saat "
        "pengujian; jika API menolaknya, hapus baris \"top_k\" di CONFIG "
        "pada providers/cohere.py."
    ),
    "params": {
        "temperature": {"min": 0.0, "max": 1.0, "default": 0.5, "step": 0.1},
        "top_p": {"min": 0.01, "max": 0.99, "default": 0.9, "step": 0.05},
        "top_k": {"min": 1, "max": 500, "default": 40, "step": 1},
    },
}


def chat(key, model, riwayat, params, system_prompt):
    """Kirim percakapan ke Cohere. Mengembalikan dict teks + token."""
    url = "https://api.cohere.com/v2/chat"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    body = {
        "model": model,
        "messages": [{"role": "system", "content": system_prompt}] + pesan_bersih(riwayat),
    }
    if "temperature" in params:
        body["temperature"] = params["temperature"]
    if "top_p" in params:
        body["p"] = params["top_p"]
    if "top_k" in params:
        body["k"] = int(params["top_k"])

    data = kirim("POST", url, headers, NAMA, body=body)
    try:
        bagian = data["message"]["content"]
        teks = "".join(b.get("text", "") for b in bagian if b.get("type") == "text")
    except (KeyError, TypeError, AttributeError):
        teks = ""
    if not teks.strip():
        raise ProviderError("Cohere tidak mengembalikan jawaban. Coba kirim ulang pertanyaanmu.")
    u = data.get("usage") or {}
    tok = u.get("tokens") or u.get("billed_units") or {}
    return bungkus_hasil(teks, tok.get("input_tokens"), tok.get("output_tokens"))


def list_models(key):
    """Daftar model Cohere yang mendukung chat."""
    data = kirim(
        "GET",
        "https://api.cohere.com/v1/models",
        {"Authorization": f"Bearer {key}"},
        NAMA,
        params={"endpoint": "chat"},
    )
    return sorted(m["name"] for m in data.get("models", []))
