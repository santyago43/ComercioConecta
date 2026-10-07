"""
ComercioConecta Frontend (Streamlit)
====================================

This Streamlit application provides a user-friendly interface for interacting with the ComercioConecta API.
It allows users to:
- View and manage products and relationships
- Perform graph explorations (BFS/DFS) from a selected product
- Visualize connected components in the commercial graph

The frontend communicates with the backend API running on http://127.0.0.1:5000.
"""

import sys
import os
# Add the project root to the Python path so that frontend can be imported when running from this directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st

# Import components
from frontend.components.sidebar import render_sidebar
from frontend.components.product_tab import render_product_tab
from frontend.components.relationship_tab import render_relationship_tab
from frontend.components.exploration_tab import render_exploration_tab
from frontend.components.component_tab import render_component_tab

# Import utilities
from frontend.utils.helpers import api_request, initialize_session_state, load_data

# Configuration
API_BASE_URL = "http://127.0.0.1:5000"

def main():
    st.set_page_config(
        page_title="ComercioConecta",
        page_icon="🛒",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for better visual appeal
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .tab-content {
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .strength-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 5px;
    }
    .welcome-box {
        background-color: #94bad6;
        border-left: 4px solid #2196f3;
        padding: 1rem;
        border-radius: 0 0.5rem 0.5rem 0;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="main-header">🛒 ComercioConecta</h1>', unsafe_allow_html=True)
    st.caption("Red comercial para entender relaciones entre productos")

    # Initialize session state
    initialize_session_state()

    # Load data automatically on first execution
    if not st.session_state.get('data_loaded', False):
        with st.spinner("Cargando datos iniciales..."):
            load_data()
            st.session_state.data_loaded = True

    # Sidebar for controls
    with st.sidebar:
        render_sidebar()

    # Main content area with tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📦 Productos", "🔗 Relaciones", "🔍 Exploración", "📊 Componentes"])

    with tab1:
        render_product_tab()

    with tab2:
        render_relationship_tab()

    with tab3:
        render_exploration_tab()

    with tab4:
        render_component_tab()

    # Footer with helpful tips
    st.divider()
    st.caption("""
    💡 **Consejos para sacar el máximo provecho de ComercioConecta:**
    - Empiece con productos cotidianos y cree relaciones reales basadas en su experiencia
    - Use BFS para ver qué productos están naturalmente asociados (ideal para combos)
    - Use DFS para descubrir cadenas de influencia largas (ideal para estrategias de placement)
    - Preste atención a los componentes aislados - representan oportunidades de conexión
    - Los pesos como porcentaje son más intuitivos: 80% significa que en 8 de 10 compras de un producto, se compra el otro también
    """)

if __name__ == "__main__":
    main()