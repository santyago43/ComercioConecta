"""
Componente de pestaña de productos para el frontend de ComercioConecta
"""
import streamlit as st


def render_product_tab():
    """Renderiza la pestaña de productos"""
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    st.header("📦 Productos Registrados")

    if st.session_state.get('products', []):
        # Welcome message with stats
        st.markdown(f"""
        <div class="welcome-box">
            <h4>📊 Resumen del inventario</h4>
            <p>Tiene <strong>{len(st.session_state.products)}</strong> productos registrados en el sistema.</p>
            <p>Use el panel lateral para agregar más productos o crear relaciones entre ellos.</p>
        </div>
        """, unsafe_allow_html=True)

        # Display products in an enhanced table format
        product_data = []
        for i, product in enumerate(st.session_state.products, 1):
            product_data.append({
                "#": i,
                "ID": product["id"],
                "Nombre": product["name"],
                "Fecha agregado": "Reciente"  # We don't have timestamp, but could add later
            })

        if product_data:
            html = '<table style="width:100%; border-collapse: collapse; margin: 1rem 0;">'
            html += '<thead><tr>'
            html += '<th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">#</th>'
            html += '<th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">ID</th>'
            html += '<th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Nombre</th>'
            html += '<th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Fecha agregado</th>'
            html += '</tr></thead><tbody>'
            for product in product_data:
                html += '<tr>'
                html += f'<td style="padding: 8px; border-bottom: 1px solid #eee;">{product["#"]}</td>'
                html += f'<td style="padding: 8px; border-bottom: 1px solid #eee;">{product["ID"]}</td>'
                html += f'<td style="padding: 8px; border-bottom: 1px solid #eee;">{product["Nombre"]}</td>'
                html += f'<td style="padding: 8px; border-bottom: 1px solid #eee;">{product["Fecha agregado"]}</td>'
                html += '</tr>'
            html += '</tbody></table>'
            st.markdown(html, unsafe_allow_html=True)

        # Quick stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total productos", len(st.session_state.products))
        with col2:
            # Most common starting letter (just for fun)
            if st.session_state.products:
                first_letters = [p['name'][0].upper() for p in st.session_state.products if p['name']]
                if first_letters:
                    from collections import Counter
                    most_common = Counter(first_letters).most_common(1)[0]
                    st.metric("Letra inicial común", f"{most_common[0]} ({most_common[1]})")
        with col3:
            st.metric("Última actualización", st.session_state.get('last_update') or "N/A")
    else:
        st.markdown("""
        <div class="welcome-box">
            <h4>🚀 ¡Comencemos!</h4>
            <p>No hay productos registrados aún. Use el panel lateral <strong>➕ Agregar Producto</strong> para comenzar.</p>
            <p><strong>Sugerencias iniciales:</strong> Leche, Pan, Huevos, Mantequilla, Café, Azúcar</p>
        </div>
        """, unsafe_allow_html=True)

        # Show some example products as cards
        st.subheader("Productos sugeridos para comenzar")
        cols = st.columns(3)
        examples = ["Leche", "Pan", "Huevos", "Mantequilla", "Café", "Azúcar"]
        for i, example in enumerate(examples[:6]):
            with cols[i % 3]:
                st.markdown(f"""
                <div style="border: 1px solid #ddd; border-radius: 8px; padding: 10px; text-align: center; margin: 5px 0;">
                    <strong style="text-transform: capitalize;">{example}</strong>
                </div>
                """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)