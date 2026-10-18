# Kerangka Presentasi SISTA (sekitar 10-12 slide)

1. **Judul dan anggota**: SISTA, mata kuliah Sistem Cerdas, nama tiga anggota.
2. **Latar belakang dan tujuan**: pengguna butuh asisten serbaguna yang mudah dipahami; tujuan tugas: memahami parameter generasi dan Zero-Shot Prompting.
3. **Profil dan persona SISTA**: asisten AI serbaguna; ramah, sopan, profesional, sistematis.
4. **Teknik prompting: Zero-Shot**: definisi, tampilkan system prompt SISTA, alasan tanpa contoh.
5. **Parameter: Temperature**: arti (tingkat keacakan), nilai rendah vs tinggi, contoh hasil.
6. **Parameter: Top-P dan Top-K**: nucleus sampling vs batas jumlah kandidat kata, perbedaannya.
7. **Arsitektur aplikasi**: diagram alur (Streamlit -> providers/ -> API -> CSV), alasan memakai tiga API.
8. **Pemilihan API dan model**: tabel Gemini / Groq / Cohere, status gratis, dukungan parameter (Groq tanpa Top-K).
9. **Demo langsung**: chat, ubah slider, jalankan eksperimen.
10. **Hasil eksperimen**: tabel per anggota (E1, E2, E3) dan temuan utama.
11. **Analisis dan keterbatasan**: kecenderungan pengaruh parameter; model berbeda antar API; hasil acak; kuota gratis.
12. **Backlog dan pembagian tugas**: ringkasan tugas tiap anggota.
13. **Kesimpulan dan saran**: apa yang dipelajari, pengembangan berikutnya.

## Pertanyaan yang mungkin ditanyakan dosen

- *Mengapa Zero-Shot?* Karena instruksi sudah cukup jelas dan tidak memerlukan contoh; lebih sederhana dan hemat token.
- *Beda Top-P dan Top-K?* Top-P memilih kata dari kelompok probabilitas kumulatif tertentu; Top-K membatasi jumlah kandidat kata teratas.
- *Mengapa Groq tidak ada Top-K?* Antarmukanya tidak menyediakan parameter itu, jadi dinonaktifkan dan dijelaskan sebagai keterbatasan.
- *Mengapa eksperimen tidak membandingkan antar-API?* Modelnya berbeda, sehingga perbedaan jawaban tidak bisa dipastikan berasal dari parameter.
