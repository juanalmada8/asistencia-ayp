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

if not login():
    st.stop()

st.title("Registro de Asistencia 🏑")
fecha = st.date_input("Seleccioná la fecha", value=datetime.now(ARG_TZ).date())

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

col1, col2, col3 = st.columns(3)
col1.metric("Total jugadoras", len(jugadoras))
col2.metric("Ya registradas", len(jugadoras_presentes))
col3.metric("Pendientes", len(jugadoras_faltantes))

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
