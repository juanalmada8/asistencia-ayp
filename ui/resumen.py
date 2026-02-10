# ui/resumen.py
import streamlit as st
import pandas as pd
import gspread
from datetime import datetime, timedelta

from config import ARG_TZ
from services.asistencia import generar_resumen
from services.google_sheets import cargar_jugadoras_con_categoria
from ui.categorias import selector_categoria, filtrar_jugadoras


def exportar_df_a_hoja(ws, df, fila_inicio):
    valores = [df.columns.tolist()] + df.astype(str).fillna("").values.tolist()
    if not valores:
        return fila_inicio + 1

    filas_necesarias = fila_inicio + len(valores) - 1
    cols_necesarias = len(valores[0])

    if filas_necesarias > ws.row_count or cols_necesarias > ws.col_count:
        ws.resize(rows=max(ws.row_count, filas_necesarias), cols=max(ws.col_count, cols_necesarias))

    ws.update(f"A{fila_inicio}", valores, value_input_option="USER_ENTERED")
    return fila_inicio + len(df) + 2


def mostrar_boton_resumen(sheet_id, fecha_desde=None, fecha_hasta=None, jugadoras_filtro=None):
    if st.button("📊 Generar resumen de asistencia"):
        with st.spinner("Generando resumen..."):
            generar_y_exportar_resumen(sheet_id, fecha_desde, fecha_hasta, jugadoras_filtro)


def _render_metrics(cards):
    html = '<div class="metrics">'
    for label, value in cards:
        html += (
            '<div class="metric-card">'
            f'<div class="metric-label">{label}</div>'
            f'<div class="metric-value">{value}</div>'
            "</div>"
        )
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def _mes_str(mes):
    try:
        return mes.strftime("%Y-%m")
    except Exception:
        return str(mes)


def _listar_nombres(nombres, limite=12):
    if not nombres:
        return None
    nombres = sorted(nombres)
    texto = ", ".join(nombres[:limite])
    if len(nombres) > limite:
        texto += " ..."
    return texto


def _df_asistencia(resumen_data, jugadoras_categoria):
    if not resumen_data:
        return pd.DataFrame(columns=["Jugadora", "Presencias", "% Asistencia"]), 0, pd.DataFrame()

    entrenamientos = resumen_data["entrenamientos_por_mes"]
    ranking = resumen_data["ranking"]
    total_entrenamientos = int(entrenamientos["Entrenamientos del mes"].sum()) if not entrenamientos.empty else 0
    ranking_presencias = ranking.rename(columns={"Total presencias": "Presencias"})
    presencias_por_jugadora = {
        row["Jugadora"]: int(row["Presencias"]) for _, row in ranking_presencias.iterrows()
    }
    resumen_jugadoras = []
    for jugadora in jugadoras_categoria:
        presencias_j = presencias_por_jugadora.get(jugadora, 0)
        porcentaje_j = round((presencias_j / total_entrenamientos) * 100, 1) if total_entrenamientos > 0 else 0
        resumen_jugadoras.append(
            {"Jugadora": jugadora, "Presencias": presencias_j, "% Asistencia": porcentaje_j}
        )
    return pd.DataFrame(resumen_jugadoras), total_entrenamientos, ranking_presencias


def mostrar_resumen_insights(sheet_id):
    st.markdown(
        """
        <div class="app-header">
            <div>
                <div class="app-title">Resumen de Asistencia</div>
                <div class="app-subtitle">Insights rápidos y exportación</div>
            </div>
            <div style="font-size: 1.4rem;">📊</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    categoria = selector_categoria()
    hoy = datetime.now(ARG_TZ).date()
    rango_default = (hoy - timedelta(days=45), hoy)

    if "jugadoras_data" not in st.session_state:
        with st.spinner("Cargando jugadoras..."):
            st.session_state.jugadoras_data = cargar_jugadoras_con_categoria()

    if any(j.get("ambas") for j in st.session_state.jugadoras_data):
        st.warning("Hay jugadoras marcadas con ambas categorías. Se asignan solo a la primera detectada.")

    jugadoras_categoria = filtrar_jugadoras(st.session_state.jugadoras_data, categoria)
    if not jugadoras_categoria:
        st.warning("No hay jugadoras para esta categoría.")
        return

    rango = st.date_input(
        "Rango para baja asistencia",
        value=rango_default,
        help="Este rango se usa solo para detectar baja asistencia.",
    )

    if isinstance(rango, tuple) and len(rango) == 2:
        fecha_desde, fecha_hasta = rango
    else:
        fecha_desde, fecha_hasta = rango_default

    resumen_meta = (categoria,)
    if st.session_state.get("resumen_cache_meta_total") != resumen_meta:
        st.session_state.resumen_cache_total = None
        st.session_state.resumen_cache_meta_total = resumen_meta

    resumen_meta_rango = (categoria, fecha_desde, fecha_hasta)
    if st.session_state.get("resumen_cache_meta_rango") != resumen_meta_rango:
        st.session_state.resumen_cache_rango = None
        st.session_state.resumen_cache_meta_rango = resumen_meta_rango

    if st.button("🔄 Actualizar insights", type="primary"):
        with st.spinner("Calculando resumen..."):
            try:
                resumen_total = generar_resumen(
                    sheet_id,
                    jugadoras_filtro=jugadoras_categoria,
                )
                resumen_rango = generar_resumen(
                    sheet_id,
                    fecha_desde=fecha_desde,
                    fecha_hasta=fecha_hasta,
                    jugadoras_filtro=jugadoras_categoria,
                )

                if not resumen_total:
                    st.warning("❗ No hay datos para esta categoría.")
                    st.session_state.resumen_cache_total = None
                else:
                    st.session_state.resumen_cache_total = resumen_total

                if not resumen_rango:
                    st.warning("❗ No hay datos para el rango seleccionado.")
                    st.session_state.resumen_cache_rango = None
                else:
                    st.session_state.resumen_cache_rango = resumen_rango
            except Exception as e:
                st.error("❌ Error al generar el resumen.")
                st.exception(e)

    resumen_data = st.session_state.get("resumen_cache_total")
    resumen_data_rango = st.session_state.get("resumen_cache_rango")

    if not resumen_data:
        st.info("Tocá “Actualizar insights” para ver el resumen.")
        mostrar_boton_resumen(sheet_id, None, None, jugadoras_categoria)
        return

    entrenamientos = resumen_data["entrenamientos_por_mes"]
    presencias = resumen_data["presencias_por_jugadora_mes"]
    tardanzas = resumen_data["llegadas_tarde_mes"]
    ranking = resumen_data["ranking"]

    total_entrenamientos = int(entrenamientos["Entrenamientos del mes"].sum()) if not entrenamientos.empty else 0
    total_presencias = int(presencias["Presencias"].sum()) if not presencias.empty else 0
    total_tardanzas = int(tardanzas["Tardanzas"].sum()) if not tardanzas.empty else 0
    top_jugadora = ranking.iloc[0]["Jugadora"] if not ranking.empty else "-"

    total_jugadoras = len(jugadoras_categoria)

    asistencia_promedio = round(total_presencias / total_entrenamientos, 1) if total_entrenamientos > 0 else 0
    porcentaje_asistencia = (
        round((total_presencias / (total_entrenamientos * total_jugadoras)) * 100, 1)
        if total_entrenamientos > 0 and total_jugadoras > 0
        else 0
    )
    porcentaje_tardanzas = round((total_tardanzas / total_presencias) * 100, 1) if total_presencias > 0 else 0

    ranking_tardanzas = (
        tardanzas.groupby("Jugadora")["Tardanzas"].sum().reset_index().sort_values("Tardanzas", ascending=False)
        if not tardanzas.empty
        else tardanzas
    )
    sin_asistencia = sorted(set(jugadoras_categoria) - set(ranking["Jugadora"])) if not ranking.empty else []

    df_asistencia, total_entrenamientos_calc, ranking_presencias = _df_asistencia(
        resumen_data, jugadoras_categoria
    )
    if total_entrenamientos_calc > 0:
        total_entrenamientos = total_entrenamientos_calc

    if total_entrenamientos > 0 and not ranking_presencias.empty:
        ranking_faltas = ranking_presencias.copy()
        ranking_faltas["Faltas"] = total_entrenamientos - ranking_faltas["Presencias"]
        ranking_faltas = ranking_faltas.sort_values("Faltas", ascending=False)
    else:
        ranking_faltas = ranking_presencias

    if not ranking_faltas.empty and "Faltas" in ranking_faltas.columns:
        ranking_faltas = ranking_faltas.rename(columns={"Faltas": "Ausencias"})
    if df_asistencia.empty:
        top_asistencia = df_asistencia
        bajo_asistencia = df_asistencia
    else:
        top_asistencia = df_asistencia.sort_values("% Asistencia", ascending=False).head(5)
        bajo_asistencia = df_asistencia.sort_values("% Asistencia", ascending=True).head(5)

    perfectas = (
        df_asistencia[df_asistencia["% Asistencia"] >= 100]["Jugadora"].tolist()
        if total_entrenamientos > 0
        else []
    )
    df_asistencia_rango, total_entrenamientos_rango, _ = _df_asistencia(
        resumen_data_rango, jugadoras_categoria
    )
    en_riesgo = (
        df_asistencia_rango[df_asistencia_rango["% Asistencia"] < 50]["Jugadora"].tolist()
        if total_entrenamientos_rango > 0
        else []
    )

    ultimo_mes = entrenamientos["Mes"].max() if not entrenamientos.empty else None
    entrenamientos_mes = 0
    presencias_mes = 0
    tardanzas_mes = 0
    porcentaje_asistencia_mes = 0
    if ultimo_mes is not None:
        entrenamientos_mes = int(
            entrenamientos[entrenamientos["Mes"] == ultimo_mes]["Entrenamientos del mes"].sum()
        )
        if entrenamientos_mes > 0:
            presencias_mes = int(presencias[presencias["Mes"] == ultimo_mes]["Presencias"].sum()) if not presencias.empty else 0
            tardanzas_mes = int(tardanzas[tardanzas["Mes"] == ultimo_mes]["Tardanzas"].sum()) if not tardanzas.empty else 0
            porcentaje_asistencia_mes = (
                round((presencias_mes / (entrenamientos_mes * total_jugadoras)) * 100, 1)
                if total_jugadoras > 0
                else 0
            )

    mejor_mes = None
    peor_mes = None
    if total_jugadoras > 0 and not entrenamientos.empty:
        entrenamientos_mes_total = entrenamientos.set_index("Mes")["Entrenamientos del mes"]
        presencias_mes_total = presencias.groupby("Mes")["Presencias"].sum() if not presencias.empty else None
        if presencias_mes_total is not None:
            asistencia_mes_pct = (presencias_mes_total / (entrenamientos_mes_total * total_jugadoras) * 100).dropna()
            if not asistencia_mes_pct.empty:
                mejor_mes = asistencia_mes_pct.idxmax()
                peor_mes = asistencia_mes_pct.idxmin()

    _render_metrics(
        [
            ("Entrenamientos", total_entrenamientos),
            ("Presencias", total_presencias),
            ("Tardanzas", total_tardanzas),
        ]
    )

    _render_metrics(
        [
            ("Asistencia promedio", asistencia_promedio),
            ("% asistencia del plantel", f"{porcentaje_asistencia}%"),
            ("% tardanzas vs presencias", f"{porcentaje_tardanzas}%"),
        ]
    )

    _render_metrics(
        [
            ("Último mes (% asistencia)", f"{porcentaje_asistencia_mes}%"),
            ("Perfectas", len(perfectas)),
            ("Baja asistencia (<50%)", len(en_riesgo)),
        ]
    )

    st.markdown('<div class="section-title">Top jugadora</div>', unsafe_allow_html=True)
    st.markdown(f"**{top_jugadora}**", unsafe_allow_html=True)

    if mejor_mes or peor_mes:
        st.markdown('<div class="section-title">Meses clave</div>', unsafe_allow_html=True)
        if mejor_mes:
            st.caption(f"Mejor mes: {_mes_str(mejor_mes)}")
        if peor_mes:
            st.caption(f"Mes más flojo: {_mes_str(peor_mes)}")

    st.markdown('<div class="section-title">Ranking (Top 5)</div>', unsafe_allow_html=True)
    st.dataframe(ranking.head(5), use_container_width=True, hide_index=True)

    st.markdown('<div class="section-title">Asistencia alta (Top 5)</div>', unsafe_allow_html=True)
    if not top_asistencia.empty:
        st.dataframe(top_asistencia, use_container_width=True, hide_index=True)
    else:
        st.caption("Sin datos de asistencia por jugadora.")

    st.markdown('<div class="section-title">Asistencia baja (Bottom 5)</div>', unsafe_allow_html=True)
    if not bajo_asistencia.empty:
        st.dataframe(bajo_asistencia, use_container_width=True, hide_index=True)
    else:
        st.caption("Sin datos de asistencia por jugadora.")

    st.markdown('<div class="section-title">Ausencias (Top 5)</div>', unsafe_allow_html=True)
    if not ranking_faltas.empty:
        st.dataframe(
            ranking_faltas[["Jugadora", "Ausencias"]].head(5),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.caption("Sin datos para calcular faltas.")

    st.markdown('<div class="section-title">Tardanzas (Top 5)</div>', unsafe_allow_html=True)
    if ranking_tardanzas is not None and not ranking_tardanzas.empty:
        st.dataframe(ranking_tardanzas.head(5), use_container_width=True, hide_index=True)
    else:
        st.caption("Sin datos de tardanzas.")

    if sin_asistencia:
        st.markdown('<div class="section-title">Sin asistencia registrada</div>', unsafe_allow_html=True)
        st.caption(_listar_nombres(sin_asistencia))

    if perfectas:
        st.markdown('<div class="section-title">Perfectas (100%)</div>', unsafe_allow_html=True)
        st.caption(_listar_nombres(perfectas))

    if en_riesgo:
        st.markdown('<div class="section-title">Baja asistencia (<50%)</div>', unsafe_allow_html=True)
        st.caption(
            f"Rango: {fecha_desde.strftime('%d/%m/%Y')} - {fecha_hasta.strftime('%d/%m/%Y')}"
        )
        st.caption(_listar_nombres(en_riesgo))

    mostrar_boton_resumen(sheet_id, None, None, jugadoras_categoria)


def generar_y_exportar_resumen(sheet_id, fecha_desde=None, fecha_hasta=None, jugadoras_filtro=None):
    resumen_data = generar_resumen(
        sheet_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        jugadoras_filtro=jugadoras_filtro,
    )

    if not resumen_data:
        st.warning("❗ No hay suficientes datos para generar el resumen.")
        return

    spreadsheet = resumen_data["spreadsheet"]

    try:
        resumen_ws = spreadsheet.worksheet("Resumen")
        resumen_ws.clear()
    except gspread.exceptions.WorksheetNotFound:
        resumen_ws = spreadsheet.add_worksheet(title="Resumen", rows="200", cols="20")

    fila = 1
    fila = exportar_df_a_hoja(resumen_ws, resumen_data["entrenamientos_por_mes"], fila)
    fila = exportar_df_a_hoja(resumen_ws, resumen_data["presencias_por_jugadora_mes"], fila)
    fila = exportar_df_a_hoja(resumen_ws, resumen_data["llegadas_tarde_mes"], fila)
    exportar_df_a_hoja(resumen_ws, resumen_data["ranking"], fila)

    st.success("✅ Resumen generado en la hoja 'Resumen'")
