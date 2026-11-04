# Panduan Struktur dan Teknik Prompting

Prompt yang baik dapat disusun dari beberapa unsur struktur dan satu atau beberapa teknik prompting. Tabel kombinasi dari dosen memasangkan keduanya, dan setiap pasangan diberi nomor kombinasi.

## Unsur struktur prompt

Task description adalah uraian tugas yang harus dikerjakan AI, misalnya menulis artikel tentang manfaat diet nabati.

Persona atau role menentukan peran AI, misalnya koki TV yang bersemangat atau perencana perjalanan.

Response format menentukan bentuk jawaban, misalnya terdiri dari pendahuluan, isi, dan kesimpulan, atau dibatasi 200 kata.

Input data atau context memberi latar belakang atau data yang perlu dipakai AI.

Instruction berisi langkah-langkah yang harus diikuti AI.

Constraints atau exclusions berisi larangan atau batasan, misalnya tidak membahas berat badan.

## Teknik prompting

Zero-shot prompting memberi instruksi tanpa contoh jawaban. Teknik ini sederhana dan hemat token, sehingga dipakai pada system prompt SISTA.

Single-shot prompting memberi satu contoh pasangan tugas dan jawaban sebelum meminta AI mengerjakan tugas baru. Few-shot prompting memberi beberapa contoh, biasanya tiga atau lebih, sehingga pola jawaban lebih terarah tetapi token input bertambah.

Action-oriented prompting memakai kata kerja yang tegas dan langsung, misalnya tulis, buat, atau ringkas.

Negative prompting menyebutkan hal yang tidak boleh ada di jawaban.

Chain of thought (CoT) meminta AI bernalar langkah demi langkah sebelum menjawab. Tree of thought (ToT) meminta AI mempertimbangkan beberapa jalur alternatif, menilai kelebihan dan kekurangannya, lalu memilih yang terbaik. Keduanya biasanya menghasilkan jawaban lebih panjang sehingga memakai lebih banyak token output.

Tool-based prompting meminta AI memakai alat atau API luar, misalnya API cuaca. Aplikasi SISTA saat ini belum mendukung pemanggilan alat.

## Contoh nomor kombinasi

Kombinasi 1 memakai task description dengan zero-shot prompting. Kombinasi 3 menambahkan persona atau role. Kombinasi 3.2 menambahkan negative prompting pada kombinasi 3. Kombinasi 14 memakai enam unsur struktur lengkap dengan chain of thought.

## Hubungan dengan token

Semakin banyak unsur struktur dan contoh yang dimasukkan, semakin besar token input. Teknik bernalar seperti CoT dan ToT cenderung menambah token output. Prompt yang efisien adalah prompt dengan token paling sedikit yang tetap menghasilkan jawaban valid dan memuaskan.
