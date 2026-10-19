"""
app.py
------
Tampilan SISTA dengan Streamlit.
Jalankan dengan:  streamlit run app.py
"""

import streamlit as st

import experiment
import providers
import ui_eksperimen
from providers import NAMA_PARAM, ProviderError

st.set_page_config(page_title="SISTA", page_icon="🎓", layout="wide")


@st.cache_data(ttl=600, show_spinner=False)
def daftar_model(nama_api):
    """Daftar model dari API (disimpan 10 menit). Kosong jika gagal diambil."""
    try:
        return providers.list_models(nama_api)
    except ProviderError:
        return []



st.title("🎓 SISTA")
st.caption(
    "Smart Information System Assistant — asisten AI serbaguna yang ramah dan mudah dipahami."
)

# ---------------------------------------------------------------------------
# SIDEBAR: pilih API dan atur parameter
# ---------------------------------------------------------------------------
siap = providers.available_providers()

with st.sidebar:
    st.header("Pengaturan")

    if not siap:
        st.error(
            "Belum ada API key. Salin `.env.example` menjadi `.env`, isi minimal satu "
            "API key, lalu jalankan ulang aplikasi."
        )
        st.stop()

    api = st.selectbox("Pilih API", siap)
    info = providers.PROVIDERS[api]

    # Model bisa diganti di sini tanpa mengubah .env dan tanpa menjalankan ulang aplikasi
    model_awal = providers.get_model(api)
    pilihan_model = [model_awal] + [m for m in daftar_model(api) if m != model_awal]
    model_pilih = st.selectbox(
        "Model", pilihan_model, key=f"model_{api}",
        help="Daftar diambil dari API. Model teratas = model dari .env / bawaan. "
             "Beberapa model di daftar mungkin bukan model chat.",
    )
    model_ketik = st.text_input(
        "Atau ketik nama model sendiri (opsional)", key=f"model_ketik_{api}",
        help="Jika diisi, nama ini dipakai menggantikan pilihan di atas.",
    )
    model = model_ketik.strip() or model_pilih
    st.info(f"Model aktif: `{model}`")

    st.subheader("Parameter")
    params = {}
    for nama, cfg in info["params"].items():
        if nama == "top_k":
            params[nama] = st.slider(
                NAMA_PARAM[nama], int(cfg["min"]), int(cfg["max"]) if cfg["max"] <= 100 else 100,
                int(cfg["default"]), int(cfg["step"]), key=f"{api}_{nama}",
            )
        else:
            params[nama] = st.slider(
                NAMA_PARAM[nama], float(cfg["min"]), float(cfg["max"]),
                float(cfg["default"]), float(cfg["step"]), key=f"{api}_{nama}",
            )

    if info["note"]:
        st.caption("ℹ️ " + info["note"])

    st.subheader("Pencatatan ke CSV")
    st.caption("Setiap pertanyaan di Chat otomatis dicatat ke results/hasil_pengujian.csv.")
    diuji_chat = st.selectbox(
        "Parameter yang sedang diuji",
        [""] + list(info["params"].keys()),
        format_func=lambda x: "(tidak ada)" if x == "" else NAMA_PARAM[x],
        key=f"diuji_{api}",
        help="Hanya label di kolom parameter_diuji pada CSV. Ubah slider parameter itu "
             "antar pertanyaan, dan biarkan parameter lain tetap.",
    )
    peneliti = st.text_input("Nama peneliti (opsional)", key="peneliti")
    nomor_kombinasi = st.text_input(
        "Nomor kombinasi prompt (opsional)", key="nomor_kombinasi",
        help="Nomor dari tabel Kombinasi Struktur dan Teknik Prompting dari dosen, "
             "contoh: 1, 3.2, 14. Ganti setiap kali kamu mengganti gaya prompt.",
    )
    nilai_ai = st.checkbox(
        "Nilai kualitas jawaban dengan AI",
        value=True,
        help="Memakai 1 panggilan API tambahan per jawaban (menghabiskan kuota lebih cepat).",
    )

    st.divider()
    if st.button("🗑️ Bersihkan percakapan"):
        st.session_state.pesan = []
        st.rerun()

# ---------------------------------------------------------------------------
# TAB
# ---------------------------------------------------------------------------
tab_chat, tab_eksp = st.tabs(["💬 Chat", "🧪 Eksperimen"])

# ---------------------------- TAB CHAT -------------------------------------
with tab_chat:
    if "pesan" not in st.session_state:
        st.session_state.pesan = []

    st.caption(
        f"API: **{api}** · Model: **{model}** · "
        + " · ".join(f"{k}={v}" for k, v in params.items())
    )

    for p in st.session_state.pesan:
        with st.chat_message(p["role"]):
            st.markdown(p["content"])
            if p.get("info"):
                st.caption(p["info"])

    pertanyaan = st.chat_input("Tulis pertanyaanmu di sini...")
    if pertanyaan:
        st.session_state.pesan.append({"role": "user", "content": pertanyaan})
        with st.chat_message("user"):
            st.markdown(pertanyaan)

        with st.chat_message("assistant"):
            with st.spinner("SISTA sedang berpikir..."):
                baris = experiment.tanya(
                    api, st.session_state.pesan, params,
                    parameter_diuji=diuji_chat, sumber="chat",
                    peneliti=peneliti.strip(), nilai_ai=nilai_ai,
                    catat_gagal=False, model=model,
                    nomor_kombinasi=nomor_kombinasi.strip(),
                )
            if baris["status"] == "OK":
                st.markdown(baris["jawaban"])
                info_teks = experiment.ringkas_baris(baris)
                st.caption(info_teks)
                st.session_state.pesan.append(
                    {"role": "assistant", "content": baris["jawaban"], "info": info_teks}
                )
            else:
                st.error(baris["status"].replace("ERROR: ", "", 1))
                # hapus pertanyaan yang gagal agar riwayat tetap rapi
                st.session_state.pesan.pop()

# -------------------------- TAB EKSPERIMEN ---------------------------------
with tab_eksp:
    ui_eksperimen.render(
        api, info, params, peneliti.strip(), nilai_ai,
        model=model, nomor_kombinasi=nomor_kombinasi.strip(),
    )
