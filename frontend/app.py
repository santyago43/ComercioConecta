"""
ComercioConecta Frontend (Streamlit)
====================================

Interfaz para registrar productos y relaciones, y consultar propuestas comerciales.
Se comunica con la API en http://127.0.0.1:5000.
"""

import sys
import os
# Permite importar frontend al ejecutar con streamlit desde cualquier carpeta
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st

from frontend.components.sidebar import render_sidebar
from frontend.components.product_tab import render_product_tab
from frontend.components.relationship_tab import render_relationship_tab
from frontend.components.exploration_tab import render_exploration_tab
from frontend.components.component_tab import render_component_tab
from frontend.components.how_it_works_tab import render_how_it_works_tab
from frontend.theme import apply_theme
from frontend.utils.helpers import initialize_session_state, load_data

PAGES = {
    "propuesta": render_exploration_tab,
    "grupos": render_component_tab,
    "productos": render_product_tab,
    "relaciones": render_relationship_tab,
    "ayuda": render_how_it_works_tab,
}


def main():
    st.set_page_config(
        page_title="ComercioConecta",
        page_icon=":material/storefront:",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_theme()
    initialize_session_state()

    if not st.session_state.get('data_loaded', False):
        load_data()
        st.session_state.data_loaded = True

    PAGES[render_sidebar()]()


if __name__ == "__main__":
    main()
