import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import CREDENTIALS_DICT

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
REQUIRED_COLUMNS = ["Fecha", "Jugadora", "Asistió", "Llegó tarde"]


def generar_resumen(sheet_id):
    creds = ServiceAccountCredentials.from_json_keyfile_dict(CREDENTIALS_DICT, SCOPE)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(sheet_id)
    ws = spreadsheet.worksheet("Asistencias")
    raw_data = ws.get_all_values()

    if not raw_data or len(raw_data) < 2:
        return None

    headers = raw_data[0]
    missing = [c for c in REQUIRED_COLUMNS if c not in headers]
    if missing:
        raise ValueError(f"Faltan columnas requeridas en 'Asistencias': {', '.join(missing)}")

    df = pd.DataFrame(raw_data[1:], columns=headers)
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df = df.dropna(subset=["Fecha", "Jugadora"])

    df["Jugadora"] = df["Jugadora"].astype(str).str.strip()
    df["Asistió"] = df["Asistió"].astype(str).str.strip().str.upper()
    df["Llegó tarde"] = df["Llegó tarde"].astype(str).str.strip().str.upper()
    df["Mes"] = df["Fecha"].dt.to_period("M")

    entrenamientos_por_mes = df.groupby("Mes")["Fecha"].nunique().reset_index(name="Entrenamientos del mes")

    presencias_por_jugadora_mes = (
        df[df["Asistió"] == "SÍ"].groupby(["Mes", "Jugadora"]).size().reset_index(name="Presencias")
    )

    llegadas_tarde_mes = (
        df[(df["Asistió"] == "SÍ") & (df["Llegó tarde"] == "SÍ")]
        .groupby(["Mes", "Jugadora"])
        .size()
        .reset_index(name="Tardanzas")
    )

    ranking = (
        df[df["Asistió"] == "SÍ"]
        .groupby("Jugadora")
        .size()
        .reset_index(name="Total presencias")
        .sort_values("Total presencias", ascending=False)
    )

    return {
        "entrenamientos_por_mes": entrenamientos_por_mes,
        "presencias_por_jugadora_mes": presencias_por_jugadora_mes,
        "llegadas_tarde_mes": llegadas_tarde_mes,
        "ranking": ranking,
        "spreadsheet": spreadsheet,
    }
