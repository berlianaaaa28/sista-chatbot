"""
app.py
------
Tampilan SISTA dengan Streamlit.
Jalankan dengan:  streamlit run app.py
"""

import streamlit as st

import providers
from providers import NAMA_PARAM

st.set_page_config(page_title="SISTA", page_icon="🎓", layout="wide")

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
    st.info(f"Model aktif: `{providers.get_model(api)}`")

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

    st.divider()
    if st.button("🗑️ Bersihkan percakapan"):
        st.session_state.pesan = []
        st.rerun()

# ---------------------------------------------------------------------------
# TAB
# ---------------------------------------------------------------------------
(tab_chat,) = st.tabs(["💬 Chat"])

# ---------------------------- TAB CHAT -------------------------------------
with tab_chat:
    if "pesan" not in st.session_state:
        st.session_state.pesan = []

    st.caption(
        f"API: **{api}** · Model: **{providers.get_model(api)}** · "
        + " · ".join(f"{k}={v}" for k, v in params.items())
    )

    for p in st.session_state.pesan:
        with st.chat_message(p["role"]):
            st.markdown(p["content"])

    pertanyaan = st.chat_input("Tulis pertanyaanmu di sini...")
    if pertanyaan:
        st.session_state.pesan.append({"role": "user", "content": pertanyaan})
        with st.chat_message("user"):
            st.markdown(pertanyaan)

        with st.chat_message("assistant"):
            with st.spinner("SISTA sedang berpikir..."):
                try:
                    jawaban = providers.chat(api, st.session_state.pesan, params)
                    st.markdown(jawaban)
                    st.session_state.pesan.append({"role": "assistant", "content": jawaban})
                except providers.ProviderError as e:
                    st.error(str(e))
                    # hapus pertanyaan yang gagal agar riwayat tetap rapi
                    st.session_state.pesan.pop()
