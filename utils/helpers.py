# utils/helpers.py

def normalizar_asistio(valor: str) -> str:
    return valor.strip().upper() if valor else "NO"

def normalizar_tarde(valor: str) -> str:
    return valor.strip().upper() if valor else "NO"

def limpiar_texto(texto: str) -> str:
    return texto.strip().upper() if texto else ""

def to_str_fecha(fecha) -> str:
    return fecha.strftime("%Y-%m-%d")
