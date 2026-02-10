
# Asistencia App - Hockey

Aplicación profesional construida con **Streamlit** para registrar y analizar asistencias de jugadoras en entrenamientos deportivos. Guarda la información en Google Sheets y genera un resumen automático con métricas por fecha, jugadora y mes.

---

## Características

- Registro de asistencia por jugadora y fecha
- Marcar si llegó tarde y agregar comentarios
- Prevención de duplicados (upsert)
- Filtro inteligente: muestra solo jugadoras que faltan
- Cálculo de estadísticas mensuales
- Generación de resumen en una hoja adicional del mismo Google Sheet
- Autenticación por clave para acceso restringido

---

## Estructura del proyecto

ASISTENCIA_APP/
├── main.py                # app principal (Streamlit)
├── config.py              # configuración global (IDs, timezone)
├── requirements.txt       # dependencias del proyecto
├── favicon.png            # icono de la página
├── icon.jpg               # logo principal
├── services/
│   ├── google_sheets.py   # acceso a Sheets (leer/escribir)
│   └── asistencia.py      # generación de resumen, cálculos
├── ui/
│   ├── login.py           # login por clave
│   ├── registro.py        # formulario de asistencia
│   └── resumen.py         # botón para generar resumen
├── utils/
│   └── helpers.py         # utilidades auxiliares

---

## Requisitos

- Python 3.9+
- Cuenta de Google con acceso a Google Sheets
- Archivo de credenciales `secrets.toml` o configurado en `st.secrets`

---

## Instalación

python -m venv venv
source venv/bin/activate  # o venv\Scripts\activate en Windows
pip install -r requirements.txt
streamlit run main.py

---

## Configuración de credenciales

En `.streamlit/secrets.toml`:

[app]
password = "tu_clave_secreta"

[credentials]
type = "..."
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n..."
client_email = "..."
client_id = "..."
...

---

## Futuras mejoras

- Gráficos en Streamlit (asistencia por semana, top 5 jugadoras, etc.)
- Exportación a Excel o PDF
- Filtros por categoría (ej: Sub 14, Primera)
- Dashboard visual

---

## Autor

Desarrollado por **Juan Almada**, 2025.

---

## Licencia

Uso privado / educativo.
