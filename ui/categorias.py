import streamlit as st

CATEGORIAS = ["Primera", "Intermedia", "Todas"]


def selector_categoria(key="categoria_seleccion"):
    st.markdown('<div class="section-title">Categoría</div>', unsafe_allow_html=True)
    return st.radio(
        "Categoría",
        CATEGORIAS,
        horizontal=True,
        label_visibility="collapsed",
        key=key,
    )


def filtrar_jugadoras(jugadoras_con_categoria, categoria):
    if categoria == "Todas":
        nombres = [j.get("jugadora", "") for j in jugadoras_con_categoria if j.get("jugadora")]
        return sorted(set(nombres))

    codigo = "1" if categoria == "Primera" else "2"
    nombres = [
        j.get("jugadora", "")
        for j in jugadoras_con_categoria
        if j.get("categoria") == codigo
    ]
    return sorted(set(nombres))
