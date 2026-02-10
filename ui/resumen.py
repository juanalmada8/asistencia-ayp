# ui/resumen.py
import streamlit as st
import gspread
from services.asistencia import generar_resumen


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
