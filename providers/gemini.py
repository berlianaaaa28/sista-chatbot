"""
providers/gemini.py
-------------------
Integrasi API Google Gemini.
Parameter yang didukung: Temperature, Top-P (topP), Top-K (topK).
"""

from .base import ProviderError, bungkus_hasil, kirim

NAMA = "Gemini"

# "params" = parameter yang DIDUKUNG. Parameter yang tidak ada di sini
# tidak akan ditampilkan di aplikasi dan tidak akan dikirim ke API.
CONFIG = {
    "urutan": 1,  # urutan tampil di dropdown aplikasi
    "key_env": "GEMINI_API_KEY",
    "model_env": "GEMINI_MODEL",
    "default_model": "gemini-3.5-flash-lite",
    "delay": 4,  # jeda antar permintaan saat eksperimen (detik)
    "note": "",
    "params": {
        "temperature": {"min": 0.0, "max": 2.0, "default": 0.5, "step": 0.1},
        "top_p": {"min": 0.0, "max": 1.0, "default": 0.9, "step": 0.05},
        "top_k": {"min": 1, "max": 40, "default": 40, "step": 1},
    },
}


def chat(key, model, riwayat, params, system_prompt):
    """Kirim percakapan ke Gemini. Mengembalikan dict teks + token."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    headers = {"x-goog-api-key": key, "Content-Type": "application/json"}

    config = {}
    if "temperature" in params:
        config["temperature"] = params["temperature"]
    if "top_p" in params:
        config["topP"] = params["top_p"]
    if "top_k" in params:
        config["topK"] = int(params["top_k"])

    body = {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": [
            {
                "role": "model" if m["role"] == "assistant" else "user",
                "parts": [{"text": m["content"]}],
            }
            for m in riwayat
        ],
        "generationConfig": config,
    }
    data = kirim("POST", url, headers, NAMA, body=body)
    try:
        bagian = data["candidates"][0]["content"]["parts"]
        teks = "".join(p.get("text", "") for p in bagian)
    except (KeyError, IndexError, TypeError):
        teks = ""
    if not teks.strip():
        raise ProviderError(
            "Gemini tidak mengembalikan jawaban (kosong atau diblokir filter keamanan). "
            "Coba ubah pertanyaanmu."
        )
    u = data.get("usageMetadata") or {}
    masuk = u.get("promptTokenCount")
    total = u.get("totalTokenCount")
    if isinstance(masuk, int) and isinstance(total, int):
        keluar = total - masuk  # termasuk token "berpikir" model
    else:
        keluar = u.get("candidatesTokenCount")
    return bungkus_hasil(teks, masuk, keluar)


def list_models(key):
    """Daftar model Gemini yang bisa dipakai untuk menghasilkan teks."""
    data = kirim(
        "GET",
        "https://generativelanguage.googleapis.com/v1beta/models",
        {"x-goog-api-key": key},
        NAMA,
        params={"pageSize": 200},
    )
    hasil = []
    for m in data.get("models", []):
        if "generateContent" in m.get("supportedGenerationMethods", []):
            hasil.append(m["name"].replace("models/", "", 1))
    return sorted(hasil)
