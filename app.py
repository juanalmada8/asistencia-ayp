import streamlit as st

from config import SHEET_ID
from ui.login import login
from ui.registro import mostrar_registro_tab
from ui.resumen import mostrar_resumen_insights

st.set_page_config(page_title="Registro de Asistencia", page_icon="icon.jpg", layout="centered")

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

    .tabbar div[role="radiogroup"],
    div[role="radiogroup"][aria-label="Secciones"] {
        display: flex;
        gap: 0.6rem;
        margin-bottom: 0.6rem;
    }

    .tabbar div[role="radiogroup"] label,
    div[role="radiogroup"][aria-label="Secciones"] label {
        margin: 0;
        padding: 0.45rem 1rem;
        border-radius: 999px;
        border: 1px solid var(--border);
        background: var(--card);
        color: var(--text);
        cursor: pointer;
    }

    .tabbar div[role="radiogroup"] label svg,
    .tabbar div[role="radiogroup"] label input,
    div[role="radiogroup"][aria-label="Secciones"] label svg,
    div[role="radiogroup"][aria-label="Secciones"] label input {
        display: none !important;
    }

    .tabbar div[role="radiogroup"] label:has(input:checked),
    div[role="radiogroup"][aria-label="Secciones"] label:has(input:checked) {
        border-color: #ffffff;
        background: #1b2230;
        box-shadow: 0 8px 18px rgba(0, 0, 0, 0.35);
    }

    @media (max-width: 640px) {
        .block-container { padding-left: 0.9rem; padding-right: 0.9rem; }
        .metrics { grid-template-columns: 1fr; }
        .metric-card { display: flex; align-items: center; justify-content: space-between; }
        .metric-value { font-size: 1.6rem; }
        .app-title { font-size: 1.15rem; }
        .tabbar div[role="radiogroup"],
        div[role="radiogroup"][aria-label="Secciones"] { gap: 0.4rem; }
    }
    </style>
    """

st.markdown(css, unsafe_allow_html=True)

if not login():
    st.stop()

st.image("icon.jpg", width=110)

st.markdown('<div class="tabbar">', unsafe_allow_html=True)
tab_seleccion = st.radio(
    "Secciones",
    ["Registro", "Resumen"],
    horizontal=True,
    label_visibility="collapsed",
    key="tab_seleccion",
)
st.markdown("</div>", unsafe_allow_html=True)

if tab_seleccion == "Registro":
    mostrar_registro_tab(SHEET_ID)

if tab_seleccion == "Resumen":
    mostrar_resumen_insights(SHEET_ID)
