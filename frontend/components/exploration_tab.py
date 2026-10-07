"""
Componente de pestaña de exploración para el frontend de ComercioConecta
"""
import streamlit as st


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

        # Depth selection with better explanation
        st.markdown("### 📏 Profundidad de exploración")
        depth_col1, depth_col2 = st.columns([2, 1])

        with depth_col1:
            depth = st.slider("Número máximo de pasos:", min_value=1, max_value=4, value=2,
                             help="¿Hasta qué nivel de separación quiere explorar?")

        with depth_col2:
            # Visual explanation of depth
            depth_explanations = {
                1: "Solo relaciones directas\n(amigos inmediatos)",
                2: "Hasta 2 pasos\n(amigos de amigos)",
                3: "Hasta 3 pasos\n(amigos de amigos de amigos)",
                4: "Hasta 4 pasos\n(cadenas largas)"
            }
            st.info(f"**Profundidad {depth}**\n{depth_explanations.get(depth, '')}")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔍 Explorar con BFS", disabled=not selected_product_id, use_container_width=True):
                if selected_product_id:
                    with st.spinner("Explorando relaciones en amplitud..."):
                        # Import here to avoid circular imports
                        from frontend.utils.helpers import api_request
                        data, error = api_request("GET", f"/explore/bfs/{selected_product_id}?depth={depth}")
                        if error:
                            st.error(f"Error en BFS: {error}")
                        else:
                            st.session_state.exploration_results['bfs'] = data
                            st.rerun()

        with col2:
            if st.button("🔍 Explorar con DFS", disabled=not selected_product_id, use_container_width=True):
                if selected_product_id:
                    with st.spinner("Explorando relaciones en profundidad..."):
                        # Import here to avoid circular imports
                        from frontend.utils.helpers import api_request
                        data, error = api_request("GET", f"/explore/dfs/{selected_product_id}?depth={depth}")
                        if error:
                            st.error(f"Error en DFS: {error}")
                        else:
                            st.session_state.exploration_results['dfs'] = data
                            st.rerun()

        # Display BFS results with enhanced visualization
        if 'bfs' in st.session_state.exploration_results:
            st.subheader("📊 Resultados BFS (Exploración por niveles)")
            bfs_data = st.session_state.exploration_results['bfs']

            if bfs_data.get("results_count", 0) > 0:
                bfs_results = []
                for result in bfs_data["results"]:
                    # Add visual indicator based on weight
                    weight_pct = result['cumulative_weight'] * 100
                    if weight_pct >= 70:
                        strength_icon = "🟢"
                        strength_text = "Fuerte"
                    elif weight_pct >= 40:
                        strength_icon = "🟡"
                        strength_text = "Moderada"
                    else:
                        strength_icon = "🔴"
                        strength_text = "Débil"

                    bfs_results.append({
                        "Distancia": f"{result['distance']} paso{'s' if result['distance'] > 1 else ''}",
                        "Producto": f"{result['product_name']} ({result['product_id']})",
                        "Peso Acumulado": f"{weight_pct:.1f}%",
                        "Fuerza": f"{strength_icon} {strength_text}",
                        "Relevancia": "★" * min(5, int(weight_pct / 20))  # Visual relevance indicator
                    })

                if bfs_results:
                    html = '<table style="width:100%; border-collapse: collapse; margin: 1rem 0;">'
                    html += '<thead><tr>'
                    html += '<th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Distancia</th>'
                    html += '<th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Producto</th>'
                    html += '<th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Peso Acumulado</th>'
                    html += '<th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Fuerza</th>'
                    html += '<th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Relevancia</th>'
                    html += '</tr></thead><tbody>'
                    for result in bfs_results:
                        html += '<tr>'
                        html += f'<td style="padding: 8px; border-bottom: 1px solid #eee;">{result["Distancia"]}</td>'
                        html += f'<td style="padding: 8px; border-bottom: 1px solid #eee;">{result["Producto"]}</td>'
                        html += f'<td style="padding: 8px; border-bottom: 1px solid #eee;">{result["Peso Acumulado"]}</td>'
                        html += f'<td style="padding: 8px; border-bottom: 1px solid #eee;">{result["Fuerza"]}</td>'
                        html += f'<td style="padding: 8px; border-bottom: 1px solid #eee;">{result["Relevancia"]}</td>'
                        html += '</tr>'
                    html += '</tbody></table>'
                    st.markdown(html, unsafe_allow_html=True)

                # Highlight most relevant result
                if bfs_results:
                    best_result = max(bfs_results, key=lambda x: float(x['Peso Acumulado'].rstrip('%')))
                    st.success(f"🎯 **Resultado más relevante:** {best_result['Producto']} ({best_result['Peso Acumulado']})")

                st.caption(f"Mostrando {bfs_data['results_count']} resultados desde {bfs_data['start_product']} (profundidad máxima: {bfs_data['max_depth']})")
            else:
                st.info("🔍 No se encontraron productos relacionados con los criterios especificados.")
                st.suggestion = st.button("💡 Sugerencia: Intente aumentar la profundidad o seleccionar otro producto")

        # Display DFS results with enhanced visualization
        if 'dfs' in st.session_state.exploration_results:
            st.subheader("📊 Resultados DFS (Exploración en profundidad)")
            dfs_data = st.session_state.exploration_results['dfs']

            if dfs_data.get("results_count", 0) > 0:
                dfs_results = []
                for result in dfs_data["results"]:
                    # Add visual indicator based on weight
                    weight_pct = result['cumulative_weight'] * 100
                    if weight_pct >= 70:
                        strength_icon = "🟢"
                        strength_text = "Fuerte"
                    elif weight_pct >= 40:
                        strength_icon = "🟡"
                        strength_text = "Moderada"
                    else:
                        strength_icon = "🔴"
                        strength_text = "Débil"

                    dfs_results.append({
                        "Distancia": f"{result['distance']} paso{'s' if result['distance'] > 1 else ''}",
                        "Producto": f"{result['product_name']} ({result['product_id']})",
                        "Peso Acumulado": f"{weight_pct:.1f}%",
                        "Fuerza": f"{strength_icon} {strength_text}",
                        "Relevancia": "★" * min(5, int(weight_pct / 20))  # Visual relevance indicator
                    })

                if dfs_results:
                    html = '<table style="width:100%; border-collapse: collapse; margin: 1rem 0;">'
                    html += '<thead><tr>'
                    html += '<th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Distancia</th>'
                    html += '<th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Producto</th>'
                    html += '<th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Peso Acumulado</th>'
                    html += '<th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Fuerza</th>'
                    html += '<th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Relevancia</th>'
                    html += '</tr></thead><tbody>'
                    for result in dfs_results:
                        html += '<tr>'
                        html += f'<td style="padding: 8px; border-bottom: 1px solid #eee;">{result["Distancia"]}</td>'
                        html += f'<td style="padding: 8px; border-bottom: 1px solid #eee;">{result["Producto"]}</td>'
                        html += f'<td style="padding: 8px; border-bottom: 1px solid #eee;">{result["Peso Acumulado"]}</td>'
                        html += f'<td style="padding: 8px; border-bottom: 1px solid #eee;">{result["Fuerza"]}</td>'
                        html += f'<td style="padding: 8px; border-bottom: 1px solid #eee;">{result["Relevancia"]}</td>'
                        html += '</tr>'
                    html += '</tbody></table>'
                    st.markdown(html, unsafe_allow_html=True)

                # Highlight most relevant result
                if dfs_results:
                    best_result = max(dfs_results, key=lambda x: float(x['Peso Acumulado'].rstrip('%')))
                    st.success(f"🎯 **Resultado más relevante:** {best_result['Producto']} ({best_result['Peso Acumulado']})")

                st.caption(f"Mostrando {dfs_data['results_count']} resultados desde {dfs_data['start_product']} (profundidad máxima: {dfs_data['max_depth']})")
            else:
                st.info("🔍 No se encontraron productos relacionados con los criterios especificados.")
    else:
        st.info("📦 No hay productos disponibles para explorar. Agregue algunos productos primero.")
    st.markdown('</div>', unsafe_allow_html=True)