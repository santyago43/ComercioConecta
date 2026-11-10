"""
Componente de pestaña de exploración para el frontend de ComercioConecta
"""
from html import escape

import streamlit as st

from frontend.utils import ui
from frontend.utils.helpers import api_request, format_pct

DEPTH_LABELS = {
    1: "Solo relaciones directas",
    2: "Hasta 2 pasos (recomendado)",
    3: "Hasta 3 pasos",
    4: "Hasta 4 pasos: cadenas largas",
}
UNREACHABLE_TAGS = {
    "otro_componente": "Otro grupo: sin relación demostrable",
    "fuera_del_alcance": "Mismo grupo, más allá de la profundidad",
}


def render_exploration_tab():
    """Renderiza la pestaña de exploración"""
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    st.header("🔍 Exploración de Relaciones")

    # Enhanced explanation
    with st.expander("📖 ¿Qué es BFS y DFS? ¿Cuándo usar cada uno?", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            ### 🔍 **BFS (Búsqueda en Amplitud)**
            - **Explora por niveles**: primero productos directos, luego los de 2 pasos, etc.
            - **Mejor para**: encontrar productos relacionados cercanos
            - **Ejemplo**: Desde "Leche" encuentra primero "Pan", "Huevos", luego "Mantequilla" (vía Pan)
            - **Use cuando**: quiera ver qué productos están directamente relacionados o a poca distancia
            """)

        with col2:
            st.markdown("""
            ### 🔍 **DFS (Búsqueda en Profundidad)**
            - **Explora una cadena lo más lejos posible** antes de retroceder
            - **Mejor para**: descubrir rutas largas de influencia
            - **Ejemplo**: Desde "Leche" podría ir Leche→Pan→Mantequilla→Huevos (si esas relaciones existen)
            - **Use cuando**: quiera ver cadenas largas de dependencia o influencia
            """)

    # Product selection for exploration
    if st.session_state.get('products', []):
        # Show current stats
        st.caption(f"📊 Disponible para explorar: {len(st.session_state.products)} productos")

        product_options = {f"{p['id']} - {p['name']}": p['id'] for p in st.session_state.products}

        # Smart default: select product with most relationships if possible
        default_index = 0
        if st.session_state.products:
            # Count relationships per product
            rel_counts = {}
            for rel in st.session_state.relationships:
                rel_counts[rel['product_a']] = rel_counts.get(rel['product_a'], 0) + 1
                rel_counts[rel['product_b']] = rel_counts.get(rel['product_b'], 0) + 1

            if rel_counts:
                most_connected = max(rel_counts, key=rel_counts.get)
                try:
                    default_index = list(product_options.values()).index(most_connected)
                except ValueError:
                    default_index = 0

        selected_product_label = st.selectbox(
            "🎯 Seleccione producto de origen:",
            options=list(product_options.keys()),
            index=default_index,
            help="El producto desde el cual comenzará la exploración"
        )
        selected_product_id = product_options[selected_product_label] if selected_product_label else None

        # Show info about selected product
        if selected_product_id:
            selected_product = next((p for p in st.session_state.products if p['id'] == selected_product_id), None)
            if selected_product:
                # Count direct relationships
                direct_rels = sum(1 for r in st.session_state.relationships
                                if r['product_a'] == selected_product_id or r['product_b'] == selected_product_id)
                st.info(f"📦 **{selected_product['name']}** tiene {direct_rels} relaciones directas")

        _render_advanced_analysis(selected_product_id)
    else:
        st.info("📦 No hay productos disponibles para explorar. Agregue algunos productos primero.")
    st.markdown('</div>', unsafe_allow_html=True)


def _render_advanced_analysis(product_id):
    depth_col, help_col = st.columns([3, 2])
    with depth_col:
        depth = st.slider("Número máximo de pasos", min_value=1, max_value=4, value=2)
    with help_col:
        ui.render(f'<div class="cc-specs">{ui.tag(DEPTH_LABELS[depth])}</div>')

    results = st.session_state.exploration_results
    actions = (("bfs", "Explorar con BFS"), ("dfs", "Explorar con DFS"), ("reachability", "Ver alcanzabilidad"))
    for column, (name, label) in zip(st.columns(3), actions):
        with column:
            if st.button(label, key=f"run_{name}", width="stretch"):
                data, error = api_request("GET", f"/explore/{name}/{product_id}?depth={depth}")
                if error:
                    st.error(f"Error: {error}")
                else:
                    results[name] = data

    # Solo se muestran resultados del producto elegido, no los de una consulta anterior
    for name, title in (("bfs", "BFS: exploración por niveles"), ("dfs", "DFS: exploración en profundidad")):
        data = results.get(name)
        if data and data["start_product"] == product_id:
            _render_traversal(title, data)

    reachability = results.get("reachability")
    if reachability and reachability["start_product_id"] == product_id:
        _render_reachability(reachability)


def _path_label(path):
    names = {p['id']: p['name'] for p in st.session_state.get('products', [])}
    return escape(" → ".join(names.get(product_id, product_id) for product_id in path))


def _traversal_table(items):
    return ui.table(
        [("Pasos", True), ("Producto", False), ("Peso acumulado", True), ("", False),
         ("Fuerza", False), ("Nivel", False), ("Camino", False)],
        [
            [
                item["distance"],
                f"<strong>{escape(item['product_name'])}</strong> {ui.product_id(item['product_id'])}",
                format_pct(item["cumulative_weight"]),
                ui.meter(item["cumulative_weight"]),
                ui.strength(item["cumulative_weight"]),
                escape(item["nivel_relacion"].capitalize()),
                _path_label(item["path"]),
            ]
            for item in items
        ],
    )


def _render_traversal(title, data):
    note = f"{data['results_count']} resultados · profundidad máxima {data['max_depth']}"
    if data["algorithm"] == "dfs":
        note += " · DFS muestra un producto una vez por cada camino"
    ui.section(title, note)

    if data["results_count"] == 0:
        ui.empty_state("Sin resultados", "No se encontraron productos relacionados con esta profundidad.")
        return
    ui.render(_traversal_table(data["results"]))


def _render_reachability(data):
    ui.section("Alcanzabilidad", f"Desde {data['start_product_name']} · profundidad máxima {data['max_depth']}")
    unreachable = data["unreachable"]
    ui.stats([
        (data["reachable_count"], "Alcanzables"),
        (sum(u["reason"] == "otro_componente" for u in unreachable), "En otro grupo"),
        (sum(u["reason"] == "fuera_del_alcance" for u in unreachable), "Fuera de alcance"),
    ])

    if data["reachable"]:
        ui.render(_traversal_table(data["reachable"]))
    if unreachable:
        ui.render(ui.table(
            [("Producto", False), ("Motivo", False)],
            [
                [f"<strong>{escape(u['product_name'])}</strong> {ui.product_id(u['product_id'])}",
                 escape(UNREACHABLE_TAGS[u["reason"]])]
                for u in unreachable
            ],
        ))
