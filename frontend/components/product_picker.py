"""
Selector del producto que lleva el cliente: desplegable propio dentro del tiquete,
con los productos agrupados, su número de relaciones y búsqueda.
"""
import re
from html import escape

import streamlit as st

from frontend.utils import ui

SELECTED_KEY = "selected_product"
SEARCH_KEY = "picker_search"
POPOVER_KEY = "picker_popover"
MARKDOWN_CHARS = re.compile(r"([\\`*_\[\]()<>:$~|#])")


def relation_counts(relationships):
    """Cuenta cuántas relaciones tiene cada producto."""
    counts = {}
    for relationship in relationships:
        for key in ("product_a", "product_b"):
            counts[relationship[key]] = counts.get(relationship[key], 0) + 1
    return counts


def relation_note(count):
    if count == 0:
        return "sin relaciones"
    return "1 relación" if count == 1 else f"{count} relaciones"


def group_products(components, counts, query=""):
    """Devuelve [(título, [producto])] con la misma numeración de la pantalla de Grupos."""
    query = query.strip().lower()
    groups = []
    for number, component in enumerate(sorted(components, key=len, reverse=True), start=1):
        size = len(component)
        title = f"Grupo {number} · " + ("aislado" if size == 1 else f"{size} productos")
        items = [
            {"id": p["product_id"], "name": p["product_name"], "relations": counts.get(p["product_id"], 0)}
            for p in component
            if query in p["product_name"].lower()
        ]
        if items:
            groups.append((title, items))
    return groups


def current_product(products, relationships):
    """Producto elegido; al inicio, el más conectado."""
    ids = [p["id"] for p in products]
    selected = st.session_state.get(SELECTED_KEY)
    if selected not in ids:
        counts = relation_counts(relationships)
        selected = max(ids, key=lambda product_id: counts.get(product_id, 0))
        st.session_state[SELECTED_KEY] = selected
    return selected


def _pick(product_id):
    st.session_state[SELECTED_KEY] = product_id
    st.session_state[SEARCH_KEY] = ""
    st.session_state[POPOVER_KEY] = False  # cierra el desplegable al elegir


def _markdown_safe(text):
    """Los nombres los escribe el usuario: se evita que se lean como markdown."""
    return MARKDOWN_CHARS.sub(r"\\\1", text)


def render_product_picker(products, selected_id):
    """Dibuja el campo 'El cliente lleva' con su lista desplegable."""
    names = {p["id"]: p["name"] for p in products}
    counts = relation_counts(st.session_state.get("relationships", []))

    ui.render('<div class="cc-pick-label">El cliente lleva</div>')
    with st.container(key="cc_picker"):
        field = f"{_markdown_safe(names[selected_id])}  :gray[{relation_note(counts.get(selected_id, 0))}]"
        with st.popover(field, width="stretch", key=POPOVER_KEY, on_change="rerun"):
            query = st.text_input(
                "Buscar producto", key=SEARCH_KEY, placeholder="Buscar producto…", label_visibility="collapsed"
            )
            groups = group_products(st.session_state.get("components", []), counts, query)
            if not groups:
                st.caption("Ningún producto coincide con la búsqueda.")
            for title, items in groups:
                ui.render(f'<div class="cc-pick-group">{escape(title)}</div>')
                for item in items:
                    chosen = item["id"] == selected_id
                    st.button(
                        f"{_markdown_safe(item['name'])}  :gray[{relation_note(item['relations'])}]",
                        key=f"pick_{item['id']}",
                        type="primary" if chosen else "tertiary",
                        icon=":material/check:" if chosen else None,
                        width="stretch",
                        on_click=_pick,
                        args=(item["id"],),
                    )
