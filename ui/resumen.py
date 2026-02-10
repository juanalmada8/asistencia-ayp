# ui/resumen.py
import streamlit as st
import pandas as pd
import gspread

from services.asistencia import generar_resumen
from services.google_sheets import cargar_jugadoras


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


def mostrar_boton_resumen(sheet_id):
    if st.button("📊 Generar resumen de asistencia"):
        with st.spinner("Generando resumen..."):
            generar_y_exportar_resumen(sheet_id)


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

    if st.button("🔄 Actualizar insights", type="primary"):
        with st.spinner("Calculando resumen..."):
            try:
                st.session_state.resumen_cache = generar_resumen(sheet_id)
            except Exception as e:
                st.error("❌ Error al generar el resumen.")
                st.exception(e)

    resumen_data = st.session_state.get("resumen_cache")
    if not resumen_data:
        st.info("Tocá “Actualizar insights” para ver el resumen.")
        mostrar_boton_resumen(sheet_id)
        return

    entrenamientos = resumen_data["entrenamientos_por_mes"]
    presencias = resumen_data["presencias_por_jugadora_mes"]
    tardanzas = resumen_data["llegadas_tarde_mes"]
    ranking = resumen_data["ranking"]

    total_entrenamientos = int(entrenamientos["Entrenamientos del mes"].sum()) if not entrenamientos.empty else 0
    total_presencias = int(presencias["Presencias"].sum()) if not presencias.empty else 0
    total_tardanzas = int(tardanzas["Tardanzas"].sum()) if not tardanzas.empty else 0
    top_jugadora = ranking.iloc[0]["Jugadora"] if not ranking.empty else "-"

    if "jugadoras" not in st.session_state:
        with st.spinner("Cargando jugadoras..."):
            st.session_state.jugadoras = cargar_jugadoras()
    total_jugadoras = len(st.session_state.jugadoras)

    asistencia_promedio = round(total_presencias / total_entrenamientos, 1) if total_entrenamientos > 0 else 0
    porcentaje_asistencia = (
        round((total_presencias / (total_entrenamientos * total_jugadoras)) * 100, 1)
        if total_entrenamientos > 0 and total_jugadoras > 0
        else 0
    )
    porcentaje_tardanzas = round((total_tardanzas / total_presencias) * 100, 1) if total_presencias > 0 else 0

    ranking_presencias = ranking.rename(columns={"Total presencias": "Presencias"})
    ranking_tardanzas = (
        tardanzas.groupby("Jugadora")["Tardanzas"].sum().reset_index().sort_values("Tardanzas", ascending=False)
        if not tardanzas.empty
        else tardanzas
    )
    sin_asistencia = sorted(set(st.session_state.jugadoras) - set(ranking["Jugadora"])) if not ranking.empty else []

    if total_entrenamientos > 0 and not ranking_presencias.empty:
        ranking_faltas = ranking_presencias.copy()
        ranking_faltas["Faltas"] = total_entrenamientos - ranking_faltas["Presencias"]
        ranking_faltas = ranking_faltas.sort_values("Faltas", ascending=False)
    else:
        ranking_faltas = ranking_presencias

    presencias_por_jugadora = {
        row["Jugadora"]: int(row["Presencias"]) for _, row in ranking_presencias.iterrows()
    }
    resumen_jugadoras = []
    for jugadora in st.session_state.jugadoras:
        presencias_j = presencias_por_jugadora.get(jugadora, 0)
        porcentaje_j = round((presencias_j / total_entrenamientos) * 100, 1) if total_entrenamientos > 0 else 0
        resumen_jugadoras.append(
            {"Jugadora": jugadora, "Presencias": presencias_j, "% Asistencia": porcentaje_j}
        )

    df_asistencia = pd.DataFrame(resumen_jugadoras)
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
    en_riesgo = (
        df_asistencia[df_asistencia["% Asistencia"] < 50]["Jugadora"].tolist()
        if total_entrenamientos > 0
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
            ("En riesgo (<50%)", len(en_riesgo)),
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

    st.markdown('<div class="section-title">Faltas (Top 5)</div>', unsafe_allow_html=True)
    if not ranking_faltas.empty:
        st.dataframe(
            ranking_faltas[["Jugadora", "Faltas"]].head(5),
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
        st.markdown('<div class="section-title">En riesgo (<50%)</div>', unsafe_allow_html=True)
        st.caption(_listar_nombres(en_riesgo))

    mostrar_boton_resumen(sheet_id)


def generar_y_exportar_resumen(sheet_id):
    resumen_data = generar_resumen(sheet_id)

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
