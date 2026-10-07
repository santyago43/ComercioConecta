"""
Componente de pestaña de componentes para el frontend de ComercioConecta
"""
import streamlit as st


def render_component_tab():
    """Renderiza la pestaña de componentes"""
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    st.header("📊 Componentes Conexos")

    # Enhanced explanation
    with st.expander("📖 ¿Qué son los componentes conexos?", expanded=True):
        st.markdown("""
        ### 🧩 Componentes Conexos
        - **Definición**: Grupos de productos donde cada producto puede llegar a cualquier otro mediante relaciones (directas o indirectas)
        - **Analogía**: Como "islas" en un archipiélago - productos dentro de la misma isla están conectados, pero no hay puentes entre islas diferentes
        - **Valor para negocio**:
          - Identificar grupos de productos naturalmente asociados
          - Detectar oportunidades para conectar componentes separados
          - Ver qué tan fragmentado está su catálogo de productos
        """)

    if st.session_state.get('components', []):
        if len(st.session_state.components) > 0:
            # Component statistics
            total_products_in_components = sum(len(comp) for comp in st.session_state.components)
            largest_component = max(st.session_state.components, key=len) if st.session_state.components else []
            smallest_components = [comp for comp in st.session_state.components if len(comp) == 1]

            st.markdown(f"""
            <div class="welcome-box">
                <h4>📊 Estadísticas de componentes</h4>
                <p><strong>{len(st.session_state.components)}</strong> componentes encontrados que contienen <strong>{total_products_in_components}</strong> productos en total:</p>
                <ul>
                    <li>🏆 Componente más grande: <strong>{len(largest_component)}</strong> productos</li>
                    <li>🔹 Productos en componentes pequeños ({len(smallest_components)} aislados): {len(smallest_components)}</li>
                    <li>📈 Conectividad promedio: {total_products_in_components / len(st.session_state.components) if st.session_state.components else 0:.1f} productos por componente</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

            # Display components in enhanced table format
            component_data = []
            for i, component in enumerate(st.session_state.components):
                # Determine component importance
                if len(component) == len(largest_component) and len(largest_component) > 1:
                    importance = "🏆 Principal"
                    importance_color = "#4CAF50"
                elif len(component) == 1:
                    importance = "🔹 Isolado"
                    importance_color = "#9E9E9E"
                else:
                    importance = f"📦 Secundario ({len(component)} productos)"
                    importance_color = "#2196F3"

                component_data.append({
                    "Componente": f"C{i+1}",
                    "Tamaño": len(component),
                    "Importancia": f"<span style='color: {importance_color}; font-weight: bold;'>{importance}</span>",
                    "Productos": ", ".join([f"{p['product_name']} ({p['product_id']})" for p in component][:3]) +
                               ("..." if len(component) > 3 else ""),
                    "Detalle": f"Ver todos los {len(component)} productos"
                })

            # Render HTML table
            if component_data:
                html = '<table style="width:100%; border-collapse: collapse; margin: 1rem 0;">'
                html += '<thead><tr>'
                html += '<th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Componente</th>'
                html += '<th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Tamaño</th>'
                html += '<th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Importancia</th>'
                html += '<th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Productos</th>'
                html += '<th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Detalle</th>'
                html += '</tr></thead><tbody>'
                for row in component_data:
                    html += '<tr>'
                    html += f'<td style="padding: 8px; border-bottom: 1px solid #eee;">{row["Componente"]}</td>'
                    html += f'<td style="padding: 8px; border-bottom: 1px solid #eee;">{row["Tamaño"]}</td>'
                    html += f'<td style="padding: 8px; border-bottom: 1px solid #eee;">{row["Importancia"]}</td>'
                    html += f'<td style="padding: 8px; border-bottom: 1px solid #eee;">{row["Productos"]}</td>'
                    html += f'<td style="padding: 8px; border-bottom: 1px solid #eee;">{row["Detalle"]}</td>'
                    html += '</tr>'
                html += '</tbody></table>'
                st.markdown(html, unsafe_allow_html=True)

            st.caption(f"Total: {len(st.session_state.components)} componentes conexos")

            # Show detailed view of components with visual indicators
            st.subheader("🔍 Detalle de Componentes")

            # Create visual representation
            cols = st.columns(min(3, len(st.session_state.components)))
            for i, component in enumerate(st.session_state.components):
                with cols[i % 3]:
                    # Determine container style based on size
                    if len(component) == 1:
                        border_color = "#9E9E9E"
                        bg_color = "#f5f5f5"
                    elif len(component) >= len(st.session_state.components[0]) * 0.8 if st.session_state.components else False:
                        border_color = "#4CAF50"
                        bg_color = "#82c487"
                    else:
                        border_color = "#2196F3"
                        bg_color = "#7aa3c2"

                    st.markdown(f"""
                    <div style="border: 2px solid {border_color}; border-radius: 10px; padding: 15px; margin: 10px 0; background-color: {bg_color};">
                        <h4>Componente {i+1}</h4>
                        <p><strong>{len(component)} producto{'s' if len(component) > 1 else ''}</strong></p>
                    </div>
                    """, unsafe_allow_html=True)

                    # List products in component
                    for product in component:
                        st.markdown(f"• **{product['product_name']}** (`{product['product_id']}`)")

                    # Add action button for isolated products
                    if len(component) == 1:
                        if st.button(f"Conectar este producto", key=f"connect_{i}", help="Sugerencia: este producto está aislado, considere crear relaciones con otros"):
                            st.info("💡 Sugerencia: busque productos relacionados en la sección de Exploración y cree relaciones aquí")
        else:
            st.info("No hay componentes detectados.")
    else:
        st.info("📊 No hay datos de componentes disponibles. Los componentes se calculan automáticamente desde las relaciones.")

        # Show helpful message when no data
        if not st.session_state.get('relationships', []):
            st.markdown("""
            <div class="welcome-box">
                <h4>🔗 Primero cree algunas relaciones</h4>
                <p>Los componentes se basan en las relaciones entre productos. Para ver componentes interesantes:</p>
                <ol>
                    <li>Agregue varios productos (mínimo 3-4)</li>
                    <li>Cree relaciones entre ellos (algunas fuertes, algunas débiles)</li>
                    <li>Vuelva a esta sección para ver cómo se agrupan</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)