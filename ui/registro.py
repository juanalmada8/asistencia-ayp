import pandas as pd
import streamlit as st


def mostrar_formulario_asistencia(jugadoras_faltantes, fecha):
    st.markdown('<div class="section-title">Jugadoras pendientes</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Marcá asistencia, tardanza y comentario en una sola tabla.</div>',
        unsafe_allow_html=True,
    )

    default_df = pd.DataFrame(
        {
            "Jugadora": jugadoras_faltantes,
            "Asistió": [False] * len(jugadoras_faltantes),
            "Llegó tarde": [False] * len(jugadoras_faltantes),
            "Comentario": [""] * len(jugadoras_faltantes),
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
