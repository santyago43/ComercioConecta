"""
Sección del analista para registrar y consultar relaciones de co-compra
"""
from html import escape

import streamlit as st

from frontend.utils import ui
from frontend.utils.helpers import api_request, format_pct, load_data


def render_relationship_tab():
    """Renderiza las relaciones y su formulario"""
    ui.page_header(
        "Relaciones",
        "Cada relación une dos productos que se compran juntos. A–B vale lo mismo que B–A.",
    )

    relationships = st.session_state.get('relationships', [])
    bands = [ui.strength_band(r['weight'])[0] for r in relationships]
    ui.stats([
        (len(relationships), "Relaciones registradas"),
        (bands.count("Fuerte"), "Fuertes: 70 % o más"),
        (bands.count("Moderada"), "Moderadas: 40 % a 69 %"),
        (bands.count("Débil"), "Débiles: menos de 40 %"),
    ])

    list_col, form_col = st.columns([3, 2], gap="large")
    with list_col:
        ui.section("Red de co-compra", "De la más fuerte a la más débil")
        if relationships:
            ui.render(_relationship_table(relationships))
        else:
            ui.empty_state("Aún no hay relaciones", "Registre al menos dos productos y conéctelos con el formulario.")
    with form_col:
        ui.section("Agregar relación", "El peso es un índice simétrico de co-compra")
        _render_form(relationships)


def _names():
    return {p['id']: p['name'] for p in st.session_state.get('products', [])}


def _relationship_table(relationships):
    names = _names()
    rows = [
        [
            f"<strong>{escape(names.get(r['product_a'], r['product_a']))}</strong> ↔ "
            f"<strong>{escape(names.get(r['product_b'], r['product_b']))}</strong>",
            format_pct(r['weight']),
            ui.meter(r['weight']),
            ui.strength(r['weight']),
        ]
        for r in sorted(relationships, key=lambda r: -r['weight'])
    ]
    return ui.table([("Productos", False), ("Co-compra", True), ("", False), ("Fuerza", False)], rows)


def _form_fields(names):
    """Dibuja los campos del formulario y devuelve (producto A, producto B, porcentaje, enviado)"""
    options = list(names)
    label = lambda product_id: f"{names[product_id]} · {product_id}"

    with st.form("add_relationship_form", border=True):
        product_a = st.selectbox("Producto A", options, index=0, format_func=label, key="rel_a")
        product_b = st.selectbox("Producto B", options, index=1, format_func=label, key="rel_b")
        percent = st.slider("Co-compra (%)", min_value=5, max_value=100, value=50, step=5)
        submitted = st.form_submit_button("Agregar relación", type="primary", width="stretch")
    return product_a, product_b, percent, submitted


def _render_form(relationships):
    names = _names()
    if len(names) < 2:
        ui.empty_state("Faltan productos", "Necesita al menos dos productos para crear una relación.")
        return

    product_a, product_b, percent, submitted = _form_fields(names)
    if not submitted:
        return

    if product_a == product_b:
        st.error("Elija dos productos diferentes.")
        return

    # La relación es simétrica: A-B y B-A son la misma
    if any({r['product_a'], r['product_b']} == {product_a, product_b} for r in relationships):
        st.error(f"Ya existe una relación entre {names[product_a]} y {names[product_b]}.")
        return

    _, error = api_request("POST", "/relationships", {
        "product_a": product_a,
        "product_b": product_b,
        "weight": percent / 100,
    })
    if error:
        st.error(f"No se pudo agregar la relación: {error}")
        return

    st.toast(f"Relación agregada: {names[product_a]} ↔ {names[product_b]} ({percent} %)")
    load_data()
    st.rerun()
