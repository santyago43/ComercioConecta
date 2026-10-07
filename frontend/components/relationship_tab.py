"""
Componente de pestaña de relaciones para el frontend de ComercioConecta
"""
import streamlit as st
from collections import Counter


def render_relationship_tab():
    """Renderiza la pestaña de relaciones"""
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    st.header("🔗 Relaciones Registradas")

    if st.session_state.get('relationships', []):
        # Relationship stats
        strong_count = sum(1 for r in st.session_state.relationships if r['weight'] >= 0.7)
        medium_count = sum(1 for r in st.session_state.relationships if 0.4 <= r['weight'] < 0.7)
        weak_count = sum(1 for r in st.session_state.relationships if r['weight'] < 0.4)

        st.markdown(f"""
        <div class="welcome-box">
            <h4>📊 Estadísticas de relaciones</h4>
            <p>Tiene <strong>{len(st.session_state.relationships)}</strong> relaciones registradas:</p>
            <ul>
                <li>🟢 <strong>Fuertes (≥70%)</strong>: {strong_count}</li>
                <li>🟡 <strong>Medianas (40-69%)</strong>: {medium_count}</li>
                <li>🔴 <strong>Débiles (<40%)</strong>: {weak_count}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # Build product lookup for names
        product_lookup = {p['id']: f"{p['id']} - {p['name']}" for p in st.session_state.get('products', [])}

        # Display relationships in an enhanced table format with visual indicators
        relationship_data = []
        for rel in st.session_state.relationships:
            from frontend.utils.helpers import get_relationship_strength_color
            color = get_relationship_strength_color(rel['weight'])
            relationship_data.append({
                "Producto A": product_lookup.get(rel["product_a"], rel["product_a"]),
                "Producto B": product_lookup.get(rel["product_b"], rel["product_b"]),
                "Fuerza": f"<span style='color: {color}; font-weight: bold;'>{rel['weight'] * 100:.0f}%</span>",
                "Tipo": "🟢 Fuerte" if rel['weight'] >= 0.7 else "🟡 Media" if rel['weight'] >= 0.4 else "🔴 Débil"
            })

        st.write("### Tabla de relaciones")
        if relationship_data:
            html = '<table style="width:100%; border-collapse: collapse; margin: 1rem 0;">'
            html += '<thead><tr>'
            html += '<th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Producto A</th>'
            html += '<th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Producto B</th>'
            html += '<th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Fuerza</th>'
            html += '<th style="text-align: left; padding: 8px; border-bottom: 2px solid #ddd;">Tipo</th>'
            html += '</tr></thead><tbody>'
            for rel in relationship_data:
                html += '<tr>'
                html += f'<td style="padding: 8px; border-bottom: 1px solid #eee;">{rel["Producto A"]}</td>'
                html += f'<td style="padding: 8px; border-bottom: 1px solid #eee;">{rel["Producto B"]}</td>'
                html += f'<td style="padding: 8px; border-bottom: 1px solid #eee;">{rel["Fuerza"]}</td>'
                html += f'<td style="padding: 8px; border-bottom: 1px solid #eee;">{rel["Tipo"]}</td>'
                html += '</tr>'
            html += '</tbody></table>'
            st.markdown(html, unsafe_allow_html=True)

        # Show strongest relationships highlighted
        if st.session_state.relationships:
            strongest = max(st.session_state.relationships, key=lambda x: x['weight'])
            prod_a = next((p for p in st.session_state.get('products', []) if p['id'] == strongest['product_a']), None)
            prod_b = next((p for p in st.session_state.get('products', []) if p['id'] == strongest['product_b']), None)
            name_a = f"{prod_a['id']} - {prod_a['name']}" if prod_a else strongest['product_a']
            name_b = f"{prod_b['id']} - {prod_b['name']}" if prod_b else strongest['product_b']

            st.info(f"🔥 **Relación más fuerte:** {name_a} ↔ {name_b} ({strongest['weight'] * 100:.0f}%)")
    else:
        st.markdown("""
        <div class="welcome-box">
            <h4>🔗 Comience a conectar productos</h4>
            <p>No hay relaciones registradas aún. Primero necesita al menos 2 productos, luego use el panel lateral para crear relaciones entre ellos.</p>
            <p><strong>Ejemplo de relaciones útiles:</strong></p>
            <ul>
                <li>Leche ↔ Pan (desayuno)</li>
                <li>Café ↔ Azúcar (endulzante)</li>
                <li>Huevos ↔ Mantequilla (cocina)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)