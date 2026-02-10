# ui/login.py
import streamlit as st
from PIL import Image

def login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.markdown("### 🔐 Ingreso de entrenador")
        pwd = st.text_input("Clave de acceso", type="password")
        if pwd == st.secrets["app"]["password"]:
            st.session_state.logged_in = True
            st.rerun()
        elif pwd != "":
            st.error("❌ Clave incorrecta")
        return False

    logo = Image.open("icon.jpg")
    st.image(logo, width=120)
    return True
