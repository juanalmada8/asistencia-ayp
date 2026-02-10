# ui/login.py
from datetime import datetime, timedelta

import streamlit as st

MAX_INTENTOS = 5
BLOQUEO_MINUTOS = 5


def login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "login_attempts" not in st.session_state:
        st.session_state.login_attempts = 0
    if "login_blocked_until" not in st.session_state:
        st.session_state.login_blocked_until = None

    if not st.session_state.logged_in:
        st.markdown("### Ingreso de entrenador")

        blocked_until = st.session_state.login_blocked_until
        if blocked_until and datetime.now() < blocked_until:
            restante = int((blocked_until - datetime.now()).total_seconds() // 60) + 1
            st.warning(f"Demasiados intentos fallidos. Reintentá en {restante} minuto(s).")
            return False

        with st.form("login_form"):
            pwd = st.text_input("Clave de acceso", type="password")
            submitted = st.form_submit_button("Ingresar", type="primary")

        if submitted and pwd:
            if pwd == st.secrets["app"]["password"]:
                st.session_state.logged_in = True
                st.session_state.login_attempts = 0
                st.session_state.login_blocked_until = None
                st.rerun()
                return False

            st.session_state.login_attempts += 1
            intentos_restantes = MAX_INTENTOS - st.session_state.login_attempts

            if intentos_restantes <= 0:
                st.session_state.login_blocked_until = datetime.now() + timedelta(minutes=BLOQUEO_MINUTOS)
                st.error("Se bloqueó temporalmente el acceso por seguridad.")
            else:
                st.error(f"Clave incorrecta. Intentos restantes: {intentos_restantes}")

        return False
    return True
