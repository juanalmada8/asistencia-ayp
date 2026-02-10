import pandas as pd
import streamlit as st


def mostrar_formulario_asistencia(jugadoras_faltantes, fecha):
    st.markdown('<div class="section-title">Jugadoras pendientes</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Usá tarjetas en el celu o la tabla en desktop.</div>',
        unsafe_allow_html=True,
    )

    modo_celu = st.toggle("Modo celular", value=True, help="Tarjetas más cómodas en pantalla chica.")

    if modo_celu:
        filas = []
        for jugadora in jugadoras_faltantes:
            key_base = f"{fecha.strftime('%Y%m%d')}_{jugadora}"
            with st.container(border=True):
                st.markdown(f"**{jugadora}**")
                c1, c2 = st.columns(2)
                asistio = c1.checkbox("Asistió", key=f"{key_base}_asistio")
                tarde = c2.checkbox("Tarde", key=f"{key_base}_tarde", disabled=not asistio)
                comentario = st.text_input(
                    "Comentario",
                    key=f"{key_base}_coment",
                    placeholder="Opcional",
                    max_chars=120,
                )
            filas.append(
                [
                    fecha.strftime("%Y-%m-%d"),
                    jugadora.strip(),
                    "SÍ" if asistio else "NO",
                    "SÍ" if asistio and tarde else "NO",
                    str(comentario).strip().upper(),
                ]
            )

        if st.button("✅ Guardar asistencia", type="primary"):
            return filas

        return []

    default_df = pd.DataFrame(
        {
            "Jugadora": jugadoras_faltantes,
            "Asistió": [False] * len(jugadoras_faltantes),
            "Llegó tarde": [False] * len(jugadoras_faltantes),
            "Comentario": ["" for _ in jugadoras_faltantes],
        }
    )

    edited_df = st.data_editor(
        default_df,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            "Jugadora": st.column_config.TextColumn(disabled=True),
            "Asistió": st.column_config.CheckboxColumn(default=False, width="small", label="Asistió"),
            "Llegó tarde": st.column_config.CheckboxColumn(default=False, width="small", label="Tarde"),
            "Comentario": st.column_config.TextColumn(max_chars=120, width="medium"),
        },
        key=f"asistencia_editor_{fecha.strftime('%Y%m%d')}",
    )

    if st.button("✅ Guardar asistencia", type="primary"):
        filas = []
        for _, row in edited_df.iterrows():
            asistio = bool(row["Asistió"])
            tarde = bool(row["Llegó tarde"]) if asistio else False
            comentario = str(row["Comentario"]).strip().upper()
            filas.append(
                [
                    fecha.strftime("%Y-%m-%d"),
                    str(row["Jugadora"]).strip(),
                    "SÍ" if asistio else "NO",
                    "SÍ" if asistio and tarde else "NO",
                    comentario,
                ]
            )
        return filas

    return []
