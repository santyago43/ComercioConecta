"""
Barra lateral: marca, navegación por tipo de usuario y estado de la red
"""
import streamlit as st

from frontend.utils.ui import render

# Las secciones se agrupan según quién las usa: encargado de ventas o analista
NAVIGATION = (
    ("Consultar", (
        ("propuesta", "Recomendaciones", ":material/storefront:"),
        ("grupos", "Grupos de productos", ":material/workspaces:"),
    )),
    ("Registrar", (
        ("productos", "Productos", ":material/inventory_2:"),
        ("relaciones", "Relaciones", ":material/link:"),
    )),
    ("Ayuda", (
        ("ayuda", "Cómo funciona", ":material/help:"),
    )),
)


def _go_to(section):
    st.session_state.section = section


def render_sidebar():
    """Dibuja la barra lateral y devuelve la sección activa"""
    active = st.session_state.setdefault("section", "propuesta")

    with st.sidebar:
        render(
            '<div class="cc-brand"><div class="cc-brand-name">ComercioConecta</div>'
            '<div class="cc-brand-tag">Red comercial de tiendas de barrio</div></div>'
        )

        for group, items in NAVIGATION:
            render(f'<div class="cc-nav-label">{group}</div>')
            for key, label, icon in items:
                st.button(
                    label,
                    key=f"nav_{key}",
                    icon=icon,
                    type="primary" if key == active else "tertiary",
                    width="stretch",
                    on_click=_go_to,
                    args=(key,),
                )

        products = len(st.session_state.get('products', []))
        relationships = len(st.session_state.get('relationships', []))
        groups = len(st.session_state.get('components', []))
        render(
            f'<div class="cc-network"><strong>{products}</strong> productos · '
            f'<strong>{relationships}</strong> relaciones · <strong>{groups}</strong> grupos<br>'
            'Datos sintéticos de demostración</div>'
        )

    return active
