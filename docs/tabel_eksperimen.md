# Tabel Eksperimen

Aturan: satu parameter diubah per eksperimen, parameter lain tetap, pertanyaan dan system prompt sama, satu API dan satu model per eksperimen.

## Rancangan (pembagian anggota)

| Eksperimen | Penanggung jawab | API | Parameter diuji | Nilai | Parameter tetap |
|---|---|---|---|---|---|
| E1 | Anggota 1 | Gemini | Temperature | 0.2, 0.5, 0.8 | Top-P 0.9, Top-K 40 |
| E2 | Anggota 2 | Groq | Top-P | 0.5, 0.7, 0.9 | Temperature 0.5 (Top-K tidak ada) |
| E3 | Anggota 3 | Cohere | Top-K | 10, 20, 40 | Temperature 0.5, Top-P 0.9 |

Pertanyaan yang disarankan (sama untuk semua):
1. "Jelaskan apa itu fotosintesis." (faktual: hasil diharapkan stabil, variasi kecil)
2. "Buatkan slogan untuk warung kopi mahasiswa." (kreatif: pengaruh parameter lebih terlihat)

Jika waktu cukup, setiap anggota menambah satu parameter lagi yang didukung API-nya.

## Template hasil (isi dari `results/hasil_eksperimen.csv`)

Kolom hasil mengikuti CSV: `token_input`, `token_output`, `jumlah_kata`, `jumlah_kalimat`, dan `deskripsi_kualitas`.

| No | API / Model | Parameter diuji | Nilai | Parameter tetap | Token in / out | Kata | Deskripsi kualitas (AI) | Catatan sendiri |
|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | |
| 2 | | | | | | | | |
| 3 | | | | | | | | |

## Cara menganalisis

- Bandingkan juga pertanyaan faktual vs kreatif: apakah pengaruh parameter lebih besar pada tugas kreatif?
- Bandingkan jawaban antar nilai: apakah makin acak, makin panjang, makin variatif, atau makin kaku?
- Tulis pengamatan sebagai **kecenderungan**, bukan kepastian. Jawaban AI acak, sehingga satu kali uji belum cukup untuk menyimpulkan; ulangi 2 kali jika memungkinkan.
- Jangan membandingkan jawaban antar API untuk menyimpulkan pengaruh parameter, karena model dan pelatihannya berbeda.
