import base64
import streamlit as st

from config import SHEET_ID
from ui.login import login
from ui.registro import mostrar_registro_tab
from ui.resumen import mostrar_resumen_insights

st.set_page_config(page_title="Registro de Asistencia", page_icon="icon.jpg", layout="centered")

with open("icon.jpg", "rb") as logo_file:
    logo_b64 = base64.b64encode(logo_file.read()).decode("utf-8")

css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=DM+Sans:wght@400;600&display=swap');

    :root {
        --bg: #0f1117;
        --card: #171a21;
        --card-2: #1d212a;
        --text: #f2f4f8;
        --muted: #9aa4b2;
        --accent: #7cf4b5;
        --accent-2: #f5c169;
        --border: rgba(255, 255, 255, 0.08);
    }

    html, body, [class*="css"]  {
        font-family: "DM Sans", system-ui, -apple-system, sans-serif;
    }

    .stApp {
        background: radial-gradient(120% 120% at 0% 0%, #141824 0%, var(--bg) 55%);
        color: var(--text);
    }

    header, footer, #MainMenu { visibility: hidden; }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 4rem;
        max-width: 720px;
    }

    .app-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.75rem;
        padding: 0.8rem 1rem;
        border-radius: 16px;
        background: linear-gradient(135deg, #141a2b 0%, #0f121a 100%);
        border: 1px solid var(--border);
        margin-bottom: 0.9rem;
    }

    .banner-wrap button {
        display: block;
        width: 100%;
        height: 140px;
        padding: 0;
        border-radius: 18px;
        border: 2px solid #ffffff;
        background-color: #121522;
        background-image: url("data:image/jpeg;base64,LOGO_B64");
        background-repeat: no-repeat;
        background-position: center;
        background-size: contain;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.35);
        margin-bottom: 0.9rem;
        font-size: 0;
    }

    .banner-wrap button:active {
        transform: scale(0.995);
    }

    .app-title {
        font-family: "Space Grotesk", system-ui, sans-serif;
        font-weight: 700;
        font-size: 1.35rem;
        margin: 0;
        letter-spacing: 0.2px;
    }

    .app-subtitle {
        color: var(--muted);
        font-size: 0.95rem;
        margin-top: 0.25rem;
    }

    .metrics {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.6rem;
        margin: 0.8rem 0 1.1rem;
    }

    .metric-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 0.9rem 1rem;
    }

    .metric-label {
        color: var(--muted);
        font-size: 0.85rem;
        margin-bottom: 0.35rem;
    }

    .metric-value {
        font-family: "Space Grotesk", system-ui, sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
    }

    .section-title {
        font-family: "Space Grotesk", system-ui, sans-serif;
        font-size: 1.1rem;
        margin: 1.1rem 0 0.2rem;
    }

    .section-caption {
        color: var(--muted);
        margin-bottom: 0.6rem;
        font-size: 0.95rem;
    }

    .stButton > button {
        border-radius: 14px;
        font-weight: 700;
        padding: 0.7rem 1rem;
        width: 100%;
    }

    .stDateInput > label {
        font-weight: 600;
    }

    @media (max-width: 640px) {
        .block-container { padding-left: 0.9rem; padding-right: 0.9rem; }
        .metrics { grid-template-columns: 1fr; }
        .metric-card { display: flex; align-items: center; justify-content: space-between; }
        .metric-value { font-size: 1.6rem; }
        .app-title { font-size: 1.15rem; }
        .banner-wrap button { height: 110px; }
    }
    </style>
    """

st.markdown(css.replace("LOGO_B64", logo_b64), unsafe_allow_html=True)

st.markdown('<div class="banner-wrap">', unsafe_allow_html=True)
if st.button("Inicio", key="banner_home"):
    st.session_state["tab_seleccion"] = "Registro"
    st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

if not login():
    st.stop()

tab_seleccion = st.radio(
    "Secciones",
    ["Registro", "Resumen"],
    horizontal=True,
    label_visibility="collapsed",
    key="tab_seleccion",
)

if tab_seleccion == "Registro":
    mostrar_registro_tab(SHEET_ID)

if tab_seleccion == "Resumen":
    mostrar_resumen_insights(SHEET_ID)
