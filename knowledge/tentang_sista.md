# Tentang SISTA

SISTA (Smart Information System Assistant) adalah chatbot asisten AI serbaguna yang dibuat untuk tugas mata kuliah Sistem Cerdas, program studi Sistem Informasi semester 7. Aplikasi dibangun dengan Python dan Streamlit, dan dijalankan di laptop sendiri melalui alamat localhost.

SISTA memakai tiga API AI yang punya akses gratis: Gemini dari Google, Groq, dan Cohere. Setiap anggota kelompok memegang satu API. Pengguna memilih API dan model lewat sidebar, lalu bertanya di tab Chat.

## Parameter yang dapat diatur

Temperature mengatur tingkat keacakan jawaban. Nilai rendah membuat jawaban lebih stabil dan seragam, nilai tinggi membuat jawaban lebih bervariasi dan kreatif.

Top-P (nucleus sampling) memilih kata berikutnya dari kelompok kata yang probabilitas kumulatifnya mencapai nilai P. Top-K membatasi pilihan kata berikutnya pada K kandidat teratas. Groq tidak menyediakan parameter Top-K, sehingga pengaturan itu dinonaktifkan jika API Groq dipilih.

## Pencatatan hasil

Setiap pertanyaan yang diajukan di tab Chat otomatis dicatat ke file CSV. Kolomnya mencakup waktu, API, model, parameter, pertanyaan, jawaban, jumlah token input, jumlah token output, jumlah kata, jumlah kalimat, dan deskripsi kualitas. Deskripsi kualitas dibuat oleh AI yang menilai jawabannya sendiri, sehingga bisa bias.

## Pembagian kerja tim

Berliana mengerjakan kerangka proyek, system prompt Zero-Shot, integrasi Gemini, dan tampilan chat dasar. Khusnul mengerjakan integrasi Groq, pencatatan CSV, penilai kualitas AI, serta pilihan model dan nomor kombinasi. Bela mengerjakan integrasi Cohere, tab Eksperimen, dan kerangka presentasi. Kode dikelola lewat GitHub dengan alur branch, Pull Request, dan review.
