"""
Funciones de utilidad para el frontend de ComercioConecta
"""
import streamlit as st
import requests
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://127.0.0.1:5000"

def api_request(method, endpoint, data=None):
    """Make API request and handle response"""
    url = f"{API_BASE_URL}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        else:
            raise ValueError(f"Unsupported method: {method}")

        if response.status_code in [200, 201]:
            return response.json(), None
        else:
            try:
                error_data = response.json()
                return None, error_data.get("error", f"HTTP {response.status_code}")
            except:
                return None, f"HTTP {response.status_code}: {response.text}"
    except requests.exceptions.ConnectionError:
        return None, "No se puede conectar a la API. Asegúrese de que esté ejecutándose en http://127.0.0.1:5000"
    except Exception as e:
        return None, str(e)

def initialize_session_state():
    """Initialize session state variables"""
    if 'products' not in st.session_state:
        st.session_state.products = []
    if 'relationships' not in st.session_state:
        st.session_state.relationships = []
    if 'graph_info' not in st.session_state:
        st.session_state.graph_info = {}
    if 'exploration_results' not in st.session_state:
        st.session_state.exploration_results = {}
    if 'components' not in st.session_state:
        st.session_state.components = []
    if 'last_update' not in st.session_state:
        st.session_state.last_update = None

def load_data():
    """Load data from API"""
    # Load products
    products_data, error = api_request("GET", "/products")
    if error:
        st.error(f"Error cargando productos: {error}")
    else:
        st.session_state.products = products_data.get("products", [])

    # Load relationships
    relationships_data, error = api_request("GET", "/relationships")
    if error:
        st.error(f"Error cargando relaciones: {error}")
    else:
        st.session_state.relationships = relationships_data.get("relationships", [])

    # Load graph info
    graph_info, error = api_request("GET", "/graph/info")
    if error:
        st.error(f"Error cargando información del grafo: {error}")
    else:
        st.session_state.graph_info = graph_info

    # Load components
    components_data, error = api_request("GET", "/components")
    if error:
        st.error(f"Error cargando componentes: {error}")
    else:
        st.session_state.components = components_data.get("components", [])

    st.session_state.last_update = datetime.now().strftime("%H:%M:%S")

def get_relationship_strength_color(weight):
    """Return color based on relationship strength"""
    if weight >= 0.8:
        return "#4CAF50"  # Green - strong
    elif weight >= 0.6:
        return "#FFC107"  # Amber - medium
    elif weight >= 0.4:
        return "#FF9800"  # Orange - weak
    else:
        return "#F44336"  # Red - very weak