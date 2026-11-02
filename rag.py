"""
rag.py
------
RAG (Retrieval-Augmented Generation) sederhana, tanpa library tambahan.

Alur RAG di SISTA:
  1. Dokumen (.txt, .md, .pdf) dibaca, lalu DIPECAH menjadi potongan kecil.
  2. Setiap potongan diberi bobot kata (TF-IDF) dan dibuat indeks pencarian.
  3. Saat pengguna bertanya, dicari potongan yang paling MIRIP dengan pertanyaan
     (cosine similarity).
  4. Potongan terpilih ditempel ke prompt sebagai KONTEKS, lalu dikirim ke AI.
     AI diminta menjawab hanya dari konteks itu, dan sumbernya ditampilkan.

Pencarian ini berbasis kata kunci (bukan makna), jadi sederhana dan mudah dijelaskan.
"""

import io
import math
import re
from collections import Counter
from pathlib import Path

FOLDER_PENGETAHUAN = Path(__file__).parent / "knowledge"
EKSTENSI = (".txt", ".md", ".pdf")

# Kata umum yang tidak membantu pencarian
STOPWORD = set(
    "yang dan di ke dari untuk pada dengan adalah itu ini atau juga dalam akan ada "
    "sebagai oleh karena agar saya kamu apa bagaimana berapa kenapa mengapa siapa "
    "kapan dapat bisa tidak jika the a of to is".split()
)


class RAGError(Exception):
    """Kesalahan RAG dengan pesan yang mudah dipahami pengguna."""


# ---------------------------------------------------------------------------
# 1. MEMBACA DOKUMEN
# ---------------------------------------------------------------------------
def baca_file(nama, isi_bytes):
    """Ubah isi file (bytes) menjadi teks."""
    if nama.lower().endswith(".pdf"):
        try:
            from pypdf import PdfReader
        except ImportError:
            raise RAGError("Untuk membaca PDF, pasang pypdf dulu: pip install pypdf")
        try:
            pembaca = PdfReader(io.BytesIO(isi_bytes))
            teks = "\n\n".join((halaman.extract_text() or "") for halaman in pembaca.pages)
        except Exception as e:  # PDF rusak, terkunci, dsb.
            raise RAGError(f"File {nama} tidak bisa dibaca sebagai PDF ({type(e).__name__}).")
        if not teks.strip():
            raise RAGError(f"File {nama} tidak berisi teks (mungkin PDF hasil scan/gambar).")
        return teks
    return isi_bytes.decode("utf-8", errors="ignore")


def tanda_folder(folder=FOLDER_PENGETAHUAN):
    """Tanda perubahan isi folder (nama + waktu ubah), dipakai untuk menyegarkan cache."""
    if not Path(folder).exists():
        return ()
    return tuple(
        (p.name, p.stat().st_mtime_ns)
        for p in sorted(Path(folder).iterdir())
        if p.suffix.lower() in EKSTENSI
    )


def muat_folder(folder=FOLDER_PENGETAHUAN):
    """Baca semua dokumen di folder pengetahuan. Mengembalikan list (nama, teks)."""
    hasil = []
    if not Path(folder).exists():
        return hasil
    for p in sorted(Path(folder).iterdir()):
        if p.suffix.lower() in EKSTENSI:
            try:
                hasil.append((p.name, baca_file(p.name, p.read_bytes())))
            except RAGError:
                continue  # lewati file yang tidak bisa dibaca
    return hasil


# ---------------------------------------------------------------------------
# 2. MEMECAH TEKS (CHUNKING)
# ---------------------------------------------------------------------------
def pecah(teks, ukuran=600, tumpang=100):
    """
    Pecah teks menjadi potongan sekitar `ukuran` karakter.
    Potongan mengikuti batas paragraf; paragraf yang terlalu panjang dipotong
    dengan sedikit tumpang tindih (`tumpang`) supaya kalimat tidak terputus makna.
    """
    paragraf = [p.strip() for p in re.split(r"\n\s*\n", teks) if p.strip()]
    potongan, sekarang = [], ""

    for p in paragraf:
        if len(p) > ukuran:  # paragraf panjang: potong per jendela
            if sekarang:
                potongan.append(sekarang)
                sekarang = ""
            mulai = 0
            while mulai < len(p):
                potongan.append(p[mulai:mulai + ukuran].strip())
                if mulai + ukuran >= len(p):
                    break
                mulai += ukuran - tumpang
        elif len(sekarang) + len(p) + 2 <= ukuran:
            sekarang = f"{sekarang}\n\n{p}" if sekarang else p
        else:
            potongan.append(sekarang)
            sekarang = p

    if sekarang:
        potongan.append(sekarang)
    return [x for x in potongan if x]


# ---------------------------------------------------------------------------
# 3. INDEKS DAN PENCARIAN (TF-IDF + cosine similarity)
# ---------------------------------------------------------------------------
def token(teks):
    """Pecah teks menjadi kata-kata penting (huruf kecil, tanpa stopword)."""
    return [w for w in re.findall(r"\w+", teks.lower()) if w not in STOPWORD and len(w) > 1]


class Indeks:
    """Indeks pencarian dari kumpulan potongan teks."""

    def __init__(self, potongan):
        # potongan: list dict {"sumber": nama file, "no": nomor potongan, "teks": isi}
        self.potongan = potongan
        frekuensi = [Counter(token(p["teks"])) for p in potongan]
        n = len(potongan)
        muncul_di = Counter()  # berapa potongan yang memuat tiap kata
        for f in frekuensi:
            muncul_di.update(f.keys())
        # IDF: kata yang jarang muncul bernilai lebih tinggi
        self._idf = {w: math.log((1 + n) / (1 + d)) + 1 for w, d in muncul_di.items()}
        self._vektor = [self._vektor_dari(f) for f in frekuensi]

    def _vektor_dari(self, frekuensi):
        v = {w: c * self._idf[w] for w, c in frekuensi.items() if w in self._idf}
        panjang = math.sqrt(sum(x * x for x in v.values()))
        return v, panjang

    def cari(self, pertanyaan, k=3, skor_min=0.05):
        """Kembalikan maksimal k potongan paling relevan, urut dari skor tertinggi."""
        q, panjang_q = self._vektor_dari(Counter(token(pertanyaan)))
        if panjang_q == 0:
            return []
        hasil = []
        for p, (v, panjang_v) in zip(self.potongan, self._vektor):
            if panjang_v == 0:
                continue
            skor = sum(x * v.get(w, 0) for w, x in q.items()) / (panjang_q * panjang_v)
            if skor >= skor_min:
                hasil.append({**p, "skor": round(skor, 3)})
        hasil.sort(key=lambda h: h["skor"], reverse=True)
        return hasil[:k]


def buat_indeks(dokumen):
    """Buat indeks dari list (nama_file, teks)."""
    potongan = []
    for nama, teks in dokumen:
        for no, bagian in enumerate(pecah(teks), 1):
            potongan.append({"sumber": nama, "no": no, "teks": bagian})
    return Indeks(potongan)


# ---------------------------------------------------------------------------
# 4. MENYUSUN PROMPT
# ---------------------------------------------------------------------------
def susun_prompt(pertanyaan, hasil):
    """Gabungkan pertanyaan dengan potongan konteks menjadi satu prompt untuk AI."""
    if hasil:
        konteks = "\n\n".join(
            f"[{i}] (sumber: {h['sumber']}, bagian {h['no']})\n{h['teks']}"
            for i, h in enumerate(hasil, 1)
        )
    else:
        konteks = "(tidak ada potongan dokumen yang relevan)"
    return (
        "Jawab pertanyaan berikut berdasarkan KONTEKS di bawah ini. "
        "Jika jawabannya tidak ada di konteks, katakan bahwa informasinya tidak "
        "ditemukan di dokumen dan jangan mengarang. "
        "Sebutkan nomor sumber seperti [1] bila kamu memakainya.\n\n"
        f"KONTEKS:\n{konteks}\n\n"
        f"PERTANYAAN: {pertanyaan}"
    )


def label_sumber(hasil):
    """Ringkasan sumber untuk kolom CSV, contoh: 'tentang_sista.md#2; panduan.md#1'."""
    return "; ".join(f"{h['sumber']}#{h['no']}" for h in hasil)
