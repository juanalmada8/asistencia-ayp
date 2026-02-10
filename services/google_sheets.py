import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

from config import SHEET_ID, CREDENTIALS_DICT

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]


def normalizar_texto(value):
    return value.strip().lower().replace("ó", "o")


def get_client():
    creds = ServiceAccountCredentials.from_json_keyfile_dict(CREDENTIALS_DICT, SCOPE)
    return gspread.authorize(creds)


@st.cache_data(ttl=300)
def cargar_jugadoras():
    client = get_client()
    hoja = client.open_by_key(SHEET_ID).worksheet("Jugadoras")
    jugadoras = [j.strip() for j in hoja.col_values(1)[1:] if j.strip()]
    return sorted(set(jugadoras))


def _indices_columnas(encabezados, requeridas):
    encabezados_norm = [normalizar_texto(e) for e in encabezados]
    indices = {}
    for col in requeridas:
        col_norm = normalizar_texto(col)
        if col_norm not in encabezados_norm:
            raise ValueError(col)
        indices[col] = encabezados_norm.index(col_norm)
    return indices


@st.cache_data(ttl=120)
def obtener_asistencias_previas(fecha):
    client = get_client()
    hoja = client.open_by_key(SHEET_ID).worksheet("Asistencias")
    datos = hoja.get_all_values()
    if not datos:
        return []

    encabezados = datos[0]

    try:
        idx = _indices_columnas(encabezados, ["Fecha", "Jugadora", "Asistió"])
    except ValueError:
        st.error(
            "❌ Error al leer los encabezados de la hoja 'Asistencias'. "
            "Verificá que existan las columnas: Fecha, Jugadora, Asistió."
        )
        st.write("Encabezados detectados:", encabezados)
        return []

    fecha_str = fecha.strftime("%Y-%m-%d")
    ultimos_registros = {}

    for fila in datos[1:]:
        if len(fila) <= max(idx.values()):
            continue
        f_fecha = fila[idx["Fecha"]].strip()
        f_jugadora = fila[idx["Jugadora"]].strip()
        f_asistio = fila[idx["Asistió"]].strip().upper()
        if f_fecha == fecha_str:
            ultimos_registros[f_jugadora] = f_asistio

    return [j for j, estado in ultimos_registros.items() if estado == "SÍ"]


def upsert_asistencias(sheet_id, hoja_nombre, nuevas_filas):
    client = get_client()
    hoja = client.open_by_key(sheet_id).worksheet(hoja_nombre)
    datos = hoja.get_all_values()
    if not datos:
        raise ValueError("La hoja de asistencias no tiene encabezados.")

    encabezados = datos[0]
    idx = _indices_columnas(encabezados, ["Fecha", "Jugadora"])

    nuevas_dict = {(f[0].strip(), f[1].strip()): f for f in nuevas_filas}
    filas_existentes = datos[1:]
    filas_actualizadas = set()
    updates = []

    for i, fila in enumerate(filas_existentes):
        if len(fila) <= max(idx.values()):
            continue
        clave = (fila[idx["Fecha"]].strip(), fila[idx["Jugadora"]].strip())
        if clave in nuevas_dict:
            updates.append({"range": f"A{i + 2}", "values": [nuevas_dict[clave]]})
            filas_actualizadas.add(clave)

    if updates:
        hoja.batch_update(updates)

    nuevas_para_agregar = [fila for clave, fila in nuevas_dict.items() if clave not in filas_actualizadas]
    if nuevas_para_agregar:
        hoja.append_rows(nuevas_para_agregar, value_input_option="USER_ENTERED")

    return {
        "actualizadas": len(updates),
        "agregadas": len(nuevas_para_agregar),
    }
