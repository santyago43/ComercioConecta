"""
Sección de grupos de productos (componentes conexos del grafo)
"""
from html import escape

import streamlit as st

from frontend.utils import ui


def render_component_tab():
    """Renderiza los grupos de productos conectados entre sí"""
    ui.page_header(
        "Grupos de productos",
        "Productos que se relacionan entre sí por las compras. "
        "Solo se recomiendan productos del mismo grupo.",
    )

    components = sorted(st.session_state.get('components', []), key=len, reverse=True)
    if not components:
        ui.empty_state("Aún no hay grupos", "Los grupos aparecen al registrar productos y relaciones.")
        return

    isolated = sum(1 for component in components if len(component) == 1)
    ui.stats([
        (len(components), "Grupos"),
        (len(components[0]), "Productos en el grupo mayor"),
        (isolated, "Productos sin relaciones"),
    ])

    cards = "".join(_group_card(index, component) for index, component in enumerate(components, start=1))
    ui.render(f'<div class="cc-groups">{cards}</div>')


def _group_card(number, component):
    size = len(component)
    if size == 1:
        status = ui.tag("Aislado")
        note = "Sin relaciones: registre una para que pueda recibir propuestas."
    elif number == 1:
        status = ui.tag("Grupo principal", "solid")
        note = f"{size} productos conectados."
    else:
        status = ui.tag("Grupo separado", "outline")
        note = f"{size} productos conectados."

    chips = "".join(
        f'<span class="cc-chip">{escape(product["product_name"])}{ui.product_id(product["product_id"])}</span>'
        for product in component
    )
    return (
        f'<section class="cc-group"><div class="cc-group-head"><h3>Grupo {number}</h3>{status}</div>'
        f'<div class="cc-chips">{chips}</div><p class="cc-group-note">{escape(note)}</p></section>'
    )
