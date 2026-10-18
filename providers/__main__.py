"""
Menampilkan daftar model untuk setiap API yang key-nya sudah diisi.
Jalankan dengan:  python -m providers
"""

from . import ProviderError, available_providers, get_model, list_models

siap = available_providers()
if not siap:
    print("Belum ada API key di file .env. Isi dulu, lalu jalankan lagi.")

for nama in siap:
    print(f"\n=== {nama} (model aktif di aplikasi: {get_model(nama)}) ===")
    try:
        for model in list_models(nama):
            print(" -", model)
    except ProviderError as e:
        print("Gagal mengambil daftar model:", e)
