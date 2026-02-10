import pandas as pd
import streamlit as st
from datetime import datetime

from config import ARG_TZ
from services.google_sheets import (
    cargar_jugadoras_con_categoria,
    obtener_asistencias_previas,
    upsert_asistencias,
)
from ui.categorias import selector_categoria, filtrar_jugadoras


def mostrar_formulario_asistencia(jugadoras_faltantes, fecha):
    st.markdown('<div class="section-title">Jugadoras pendientes</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Usá tarjetas en el celu o la tabla en desktop.</div>',
        unsafe_allow_html=True,
    )

    modo_celu = st.toggle("Modo celular", value=True, help="Tarjetas más cómodas en pantalla chica.")

    if modo_celu:
        filas = []
        for jugadora in jugadoras_faltantes:
            key_base = f"{fecha.strftime('%Y%m%d')}_{jugadora}"
            with st.container(border=True):
                st.markdown(f"**{jugadora}**")
                c1, c2 = st.columns(2)
                asistio = c1.checkbox("Asistió", key=f"{key_base}_asistio")
                tarde = c2.checkbox("Tarde", key=f"{key_base}_tarde", disabled=not asistio)
                comentario = st.text_input(
                    "Comentario",
                    key=f"{key_base}_coment",
                    placeholder="Opcional",
                    max_chars=120,
                )
            filas.append(
                [
                    fecha.strftime("%Y-%m-%d"),
                    jugadora.strip(),
                    "SÍ" if asistio else "NO",
                    "SÍ" if asistio and tarde else "NO",
                    str(comentario).strip().upper(),
                ]
            )

        if st.button("Guardar asistencia", type="primary"):
            return filas

        return []

    default_df = pd.DataFrame(
        {
            "Jugadora": jugadoras_faltantes,
            "Asistió": [False] * len(jugadoras_faltantes),
            "Llegó tarde": [False] * len(jugadoras_faltantes),
            "Comentario": ["" for _ in jugadoras_faltantes],
        }
    )

    edited_df = st.data_editor(
        default_df,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            "Jugadora": st.column_config.TextColumn(disabled=True),
            "Asistió": st.column_config.CheckboxColumn(default=False, width="small", label="Asistió"),
            "Llegó tarde": st.column_config.CheckboxColumn(default=False, width="small", label="Tarde"),
            "Comentario": st.column_config.TextColumn(max_chars=120, width="medium"),
        },
        key=f"asistencia_editor_{fecha.strftime('%Y%m%d')}",
    )

    if st.button("Guardar asistencia", type="primary"):
        filas = []
        for _, row in edited_df.iterrows():
            asistio = bool(row["Asistió"])
            tarde = bool(row["Llegó tarde"]) if asistio else False
            comentario = str(row["Comentario"]).strip().upper()
            filas.append(
                [
                    fecha.strftime("%Y-%m-%d"),
                    str(row["Jugadora"]).strip(),
                    "SÍ" if asistio else "NO",
                    "SÍ" if asistio and tarde else "NO",
                    comentario,
                ]
            )
        return filas

    return []


def mostrar_registro_tab(sheet_id):
    st.markdown(
        """
        <div class="app-header">
            <div>
                <div class="app-title">Registro de Asistencia</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-title">Fecha</div>', unsafe_allow_html=True)
    fecha = st.date_input("Fecha", value=datetime.now(ARG_TZ).date(), label_visibility="collapsed")

    categoria = selector_categoria()

    if "jugadoras_data" not in st.session_state:
        with st.spinner("Cargando jugadoras..."):
            st.session_state.jugadoras_data = cargar_jugadoras_con_categoria()

    if any(j.get("ambas") for j in st.session_state.jugadoras_data):
        st.caption("Hay jugadoras marcadas con ambas categorías. Se asignan solo a la primera detectada.")

    jugadoras = filtrar_jugadoras(st.session_state.jugadoras_data, categoria)
    if not jugadoras:
        st.warning("No hay jugadoras para esta categoría.")
        return

    if "asistencias_previas" not in st.session_state or st.session_state.get("asistencia_fecha") != fecha:
        with st.spinner("Buscando asistencias previas..."):
            st.session_state.asistencias_previas = obtener_asistencias_previas(fecha)
            st.session_state.asistencia_fecha = fecha

    jugadoras_presentes = [j for j in st.session_state.asistencias_previas if j in jugadoras]
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
        st.success("Todas las jugadoras ya tienen registrada la asistencia para esta fecha.")
        return

    nuevas_filas = mostrar_formulario_asistencia(jugadoras_faltantes, fecha)
    if nuevas_filas:
        with st.spinner("Guardando asistencia..."):
            try:
                resultado = upsert_asistencias(sheet_id, "Asistencias", nuevas_filas)
                total = sum(1 for fila in nuevas_filas if fila[2] == "SÍ")
                st.success(
                    "Asistencia guardada. "
                    f"{total} jugadoras asistieron. "
                    f"(Actualizadas: {resultado['actualizadas']} | Agregadas: {resultado['agregadas']})"
                )
                del st.session_state["asistencias_previas"]
                obtener_asistencias_previas.clear()
            except Exception as e:
                st.error("Error al guardar la asistencia.")
                st.exception(e)
