import streamlit as st
from datetime import datetime

from config import SHEET_ID, ARG_TZ
from services.google_sheets import (
    cargar_jugadoras,
    obtener_asistencias_previas,
    upsert_asistencias,
)
from ui.login import login
from ui.registro import mostrar_formulario_asistencia
from ui.resumen import mostrar_boton_resumen

st.set_page_config(page_title="Registro de Asistencia", page_icon="icon.jpg", layout="centered")

st.markdown(
    """
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

    @media (max-width: 640px) {
        .block-container { padding-left: 0.9rem; padding-right: 0.9rem; }
        .metrics { grid-template-columns: 1fr; }
        .metric-card { display: flex; align-items: center; justify-content: space-between; }
        .metric-value { font-size: 1.6rem; }
        .app-title { font-size: 1.15rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if not login():
    st.stop()

st.markdown(
    """
    <div class="app-header">
        <div>
            <div class="app-title">Registro de Asistencia</div>
            <div class="app-subtitle">Marcá rápido y guardá en un toque</div>
        </div>
        <div style="font-size: 1.4rem;">🏑</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-title">Fecha</div>', unsafe_allow_html=True)
fecha = st.date_input("Fecha", value=datetime.now(ARG_TZ).date(), label_visibility="collapsed")

if "jugadoras" not in st.session_state:
    with st.spinner("Cargando jugadoras..."):
        st.session_state.jugadoras = cargar_jugadoras()

if "asistencias_previas" not in st.session_state or st.session_state.get("asistencia_fecha") != fecha:
    with st.spinner("Buscando asistencias previas..."):
        st.session_state.asistencias_previas = obtener_asistencias_previas(fecha)
        st.session_state.asistencia_fecha = fecha

jugadoras = st.session_state.jugadoras
jugadoras_presentes = st.session_state.asistencias_previas
jugadoras_faltantes = [j for j in jugadoras if j not in jugadoras_presentes]

st.markdown(
    f"""
    <div class="metrics">
        <div class="metric-card">
            <div class="metric-label">Total jugadoras</div>
            <div class="metric-value">{len(jugadoras)}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Ya registradas</div>
            <div class="metric-value">{len(jugadoras_presentes)}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Pendientes</div>
            <div class="metric-value">{len(jugadoras_faltantes)}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not jugadoras_faltantes:
    st.success("✅ Todas las jugadoras ya tienen registrada la asistencia para esta fecha.")
else:
    nuevas_filas = mostrar_formulario_asistencia(jugadoras_faltantes, fecha)
    if nuevas_filas:
        with st.spinner("Guardando asistencia..."):
            try:
                resultado = upsert_asistencias(SHEET_ID, "Asistencias", nuevas_filas)
                total = sum(1 for fila in nuevas_filas if fila[2] == "SÍ")
                st.success(
                    "✅ ¡Asistencia guardada! "
                    f"{total} jugadoras asistieron. "
                    f"(Actualizadas: {resultado['actualizadas']} | Agregadas: {resultado['agregadas']})"
                )
                del st.session_state["asistencias_previas"]
                obtener_asistencias_previas.clear()
            except Exception as e:
                st.error("❌ Error al guardar la asistencia.")
                st.exception(e)

mostrar_boton_resumen(SHEET_ID)
