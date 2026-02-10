# config.py
from pytz import timezone
import streamlit as st

# Zona horaria Argentina
ARG_TZ = timezone("America/Argentina/Buenos_Aires")

# ID del Google Sheet
SHEET_ID = "1MIzfkUB9kOsHyvNKVfBcS0VzmGbJnE4w8ufnvxHd5Po"

# Credenciales (dict ya cargado desde secrets.toml)
CREDENTIALS_DICT = st.secrets["credentials"]
