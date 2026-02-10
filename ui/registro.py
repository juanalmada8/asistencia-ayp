import streamlit as st

def mostrar_formulario_asistencia(jugadoras_faltantes, fecha):
    st.markdown("### Jugadoras")
    datos_asistencia = []

    for jugadora in jugadoras_faltantes:
        st.markdown(f"**{jugadora}**")
        asistio = st.checkbox("Asistió", key=f"asistio_{jugadora}")
        tarde = False
        comentario = ""

        if asistio:
            tarde = st.checkbox("Llegó tarde", key=f"tarde_{jugadora}")
        comentario = st.text_input("Comentario (opcional)", key=f"comentario_{jugadora}")

        datos_asistencia.append([
            fecha.strftime("%Y-%m-%d"),
            jugadora,
            "SÍ" if asistio else "NO",
            "SÍ" if asistio and tarde else "NO",
            comentario.upper() if comentario else ""
        ])

    if st.button("✅ Guardar asistencia"):
        return datos_asistencia

    return []