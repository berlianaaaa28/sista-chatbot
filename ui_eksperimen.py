"""
ui_eksperimen.py
----------------
Tampilan tab "Eksperimen" di aplikasi SISTA.
Dipanggil dari app.py:  ui_eksperimen.render(api, info, params, peneliti, nilai_ai)
"""

import streamlit as st

import experiment
import providers
from providers import NAMA_PARAM

SARAN_NILAI = {
    "temperature": "0.2, 0.5, 0.8",
    "top_p": "0.5, 0.7, 0.9",
    "top_k": "10, 20, 40",
}


def render(api, info, params, peneliti, nilai_ai):
    st.subheader("Eksperimen parameter")
    st.write(
        "Uji cepat: satu parameter diuji dengan beberapa nilai, parameter lain tetap "
        "(diambil dari sidebar). Pertanyaan dan system prompt sama untuk setiap nilai. "
        f"API dan model yang dipakai: **{api}** / `{providers.get_model(api)}`."
    )

    c1, c2 = st.columns(2)
    with c1:
        diuji = st.selectbox(
            "Parameter yang diuji",
            list(info["params"].keys()),
            format_func=lambda x: NAMA_PARAM[x],
        )
        teks_nilai = st.text_input(
            "Nilai yang diuji (pisahkan dengan koma)",
            value=SARAN_NILAI[diuji],
            key=f"nilai_{api}_{diuji}",
        )
    with c2:
        teks_pertanyaan = st.text_area(
            "Pertanyaan (satu pertanyaan per baris)",
            value="Jelaskan apa itu fotosintesis.\nBuatkan slogan untuk warung kopi mahasiswa.",
            height=120,
        )

    if "top_k" not in info["params"]:
        st.caption("Top-K tidak tersedia di API ini, jadi tidak bisa diuji di sini.")

    daftar_pertanyaan = [q.strip() for q in teks_pertanyaan.splitlines() if q.strip()]
    try:
        nilai = [float(x.strip()) for x in teks_nilai.split(",") if x.strip()]
        if diuji == "top_k":
            nilai = [int(v) for v in nilai]
        nilai_valid = True
    except ValueError:
        nilai, nilai_valid = [], False

    if nilai_valid and nilai and daftar_pertanyaan:
        perkiraan = len(nilai) * len(daftar_pertanyaan) * (2 if nilai_ai else 1)
        st.caption(
            f"Perkiraan panggilan API: {perkiraan} "
            f"({len(daftar_pertanyaan)} pertanyaan x {len(nilai)} nilai"
            f"{' x 2 karena penilaian AI aktif' if nilai_ai else ''})."
        )

    if st.button("▶️ Jalankan eksperimen", type="primary"):
        cfg = info["params"][diuji]
        if not nilai_valid:
            st.error("Nilai harus berupa angka, dipisahkan koma. Contoh: 0.2, 0.5, 0.8")
        elif not nilai:
            st.error("Isi minimal satu nilai.")
        elif any(v < cfg["min"] or v > cfg["max"] for v in nilai):
            st.error(
                f"Nilai {NAMA_PARAM[diuji]} untuk {api} harus antara {cfg['min']} dan {cfg['max']}."
            )
        elif not daftar_pertanyaan:
            st.error("Isi minimal satu pertanyaan.")
        else:
            bar = st.progress(0.0, text="Memulai...")

            def laporan(selesai, total, baris):
                bar.progress(selesai / total, text=f"Selesai {selesai} dari {total}")

            tetap = {k: v for k, v in params.items() if k != diuji}
            hasil = experiment.jalankan_eksperimen(
                api, diuji, nilai, tetap, daftar_pertanyaan,
                peneliti=peneliti, nilai_ai=nilai_ai, on_progress=laporan,
            )
            st.success("Selesai. Hasil sudah tersimpan di results/hasil_pengujian.csv")
            for h in hasil:
                judul = f"{h['pertanyaan'][:45]} | {NAMA_PARAM[diuji]} = {h[diuji]} | {h['status'][:30]}"
                with st.expander(judul):
                    st.write(h["jawaban"] or h["status"])
                    if h["status"] == "OK":
                        st.caption(experiment.ringkas_baris(h))

    st.divider()
    st.subheader("Semua hasil tersimpan")
    df = experiment.baca_csv()
    if df is None:
        st.caption("Belum ada hasil. Kirim pertanyaan di tab Chat atau jalankan eksperimen.")
    else:
        st.dataframe(df)
        st.download_button(
            "⬇️ Unduh CSV (bisa dibuka di Excel)",
            data=df.to_csv(index=False).encode("utf-8-sig"),
            file_name="hasil_pengujian.csv",
            mime="text/csv",
        )
