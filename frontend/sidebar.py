"""
Componente de barra lateral para el frontend de ComercioConecta
"""
import streamlit as st
from datetime import datetime


def render_sidebar():
    """Renderiza la barra lateral con controles y información"""
    st.header("🎯 Panel de Control")

    # Show current stats
    if st.session_state.get('last_update'):
        st.caption(f"Última actualización: {st.session_state.last_update}")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("📦 Productos", len(st.session_state.get('products', [])))
    with col2:
        st.metric("🔗 Relaciones", len(st.session_state.get('relationships', [])))

    # Getting started guide
    with st.expander("📖 Guía de inicio rápido", expanded=not st.session_state.get('products', [])):
        st.markdown("""
        **Para comenzar:**
        1. **Agregue productos** usando el formulario abajo
        2. **Conéctelos** creando relaciones entre ellos
        3. **Explore** descubriendo qué se compra con qué
        4. **Analice** los componentes para ver grupos de productos

        💡 *Tip: Empiece con productos comunes como Leche, Pan, Huevos*
        """)

    # Add product section
    st.subheader("➕ Agregar Producto")
    st.caption("El ID se genera automáticamente (P001, P002, ...)")
    with st.form("add_product_form"):
        product_name = st.text_input("Nombre del Producto", placeholder="Ej: Yogur, Queso, Mermelada")
        submitted = st.form_submit_button("Agregar Producto", use_container_width=True)

        if submitted:
            if product_name.strip():
                # Validación local: buscar duplicados por nombre (case-insensitive)
                existing = next((p for p in st.session_state.get('products', [])
                               if p['name'].lower() == product_name.strip().lower()), None)
                if existing:
                    st.error(f"❌ **Producto duplicado**")
                    with st.expander("Ver detalles del producto existente", expanded=True):
                        st.write(f"**ID:** {existing['id']}")
                        st.write(f"**Nombre:** {existing['name']}")
                        st.info("El producto ya existe en el sistema. Use el ID mostrado para crear relaciones.")
                else:
                    # Import here to avoid circular imports
                    from frontend.utils.helpers import api_request
                    data, error = api_request("POST", "/products", {"name": product_name.strip()})
                    if error:
                        st.error(f"Error: {error}")
                    else:
                        generated_id = data.get("product", {}).get("id", "desconocido")
                        st.success(f"✅ Producto '{product_name.strip()}' agregado con ID {generated_id}")
                        # Import here to avoid circular imports
                        from frontend.utils.helpers import load_data
                        load_data()
                        st.rerun()
            else:
                st.error("El nombre es requerido")

    st.divider()

    # Add relationship section
    st.subheader("🔗 Agregar Relación")
    st.caption("Peso = probabilidad de que se compren juntos (1% = rara vez, 100% = siempre)")

    # Build product options for dropdowns
    product_options = {f"{p['id']} - {p['name']}": p['id'] for p in st.session_state.get('products', [])}

    with st.form("add_relationship_form"):
        if len(product_options) >= 2:
            # Smart defaults: select first two different products
            default_a = list(product_options.keys())[0] if product_options else ""
            default_b = list(product_options.keys())[1] if len(product_options) > 1 else ""

            rel_product_a_label = st.selectbox("Producto A", options=list(product_options.keys()),
                                               index=0 if default_a else 0, key="rel_a")
            rel_product_b_label = st.selectbox("Producto B", options=list(product_options.keys()),
                                               index=1 if len(product_options) > 1 else 0, key="rel_b")

            # Ensure they're different
            if rel_product_a_label == rel_product_b_label and len(product_options) > 1:
                st.warning("Seleccione dos productos diferentes")
                rel_product_b_label = list(product_options.keys())[0] if rel_product_a_label != list(product_options.keys())[0] else list(product_options.keys())[1]

            rel_product_a = product_options[rel_product_a_label]
            rel_product_b = product_options[rel_product_b_label]
        else:
            st.info("⚠️ Primero agregue al menos 2 productos para crear relaciones")
            rel_product_a = rel_product_b = None
            rel_product_a_label = rel_product_b_label = None

        rel_weight_pct = st.slider("Co-compra (%)", min_value=1, max_value=100, value=50, step=5,
                                   help="¿Con qué frecuencia se compran estos productos juntos?")
        rel_weight = rel_weight_pct / 100.0

        # Visual indicator for relationship strength
        from frontend.utils.helpers import get_relationship_strength_color
        color = get_relationship_strength_color(rel_weight)
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin: 10px 0;">
            <div class="strength-indicator" style="background-color: {color};"></div>
            <small>Fuerza: {'Muy fuerte' if rel_weight >= 0.8 else 'Fuerte' if rel_weight >= 0.6 else 'Moderada' if rel_weight >= 0.4 else 'Débil'}</small>
        </div>
        """, unsafe_allow_html=True)

        submitted = st.form_submit_button("Agregar Relación", use_container_width=True)

        if submitted:
            if rel_product_a and rel_product_b and rel_product_a_label and rel_product_b_label:
                if rel_product_a == rel_product_b:
                    st.error("Los productos deben ser diferentes")
                else:
                    # Validación local: buscar relación duplicada (en cualquier dirección)
                    existing_rel = next((r for r in st.session_state.get('relationships', [])
                                       if (r['product_a'] == rel_product_a and r['product_b'] == rel_product_b)
                                       or (r['product_a'] == rel_product_b and r['product_b'] == rel_product_a)), None)
                    if existing_rel:
                        # Obtener nombres de productos
                        prod_a = next((p for p in st.session_state.get('products', []) if p['id'] == existing_rel['product_a']), None)
                        prod_b = next((p for p in st.session_state.get('products', []) if p['id'] == existing_rel['product_b']), None)
                        name_a = f"{prod_a['id']} - {prod_a['name']}" if prod_a else existing_rel['product_a']
                        name_b = f"{prod_b['id']} - {prod_b['name']}" if prod_b else existing_rel['product_b']

                        st.error(f"❌ **Relación duplicada**")
                        with st.expander("Ver detalles de la relación existente", expanded=True):
                            st.write(f"**Producto A:** {name_a}")
                            st.write(f"**Producto B:** {name_b}")
                            st.write(f"**Co-compra actual:** {existing_rel['weight'] * 100:.0f}%")
                            st.write(f"**Co-compra intentada:** {rel_weight * 100:.0f}%")
                            st.info("La relación ya existe (el orden no importa: A-B es igual a B-A). "
                                   "Modifique el peso desde la API directamente si necesita cambiarlo.")
                    else:
                        # Import here to avoid circular imports
                        from frontend.utils.helpers import api_request
                        data, error = api_request("POST", "/relationships", {
                            "product_a": rel_product_a,
                            "product_b": rel_product_b,
                            "weight": rel_weight
                        })
                        if error:
                            st.error(f"Error: {error}")
                        else:
                            # Obtener nombres para mensaje de éxito
                            prod_a = next((p for p in st.session_state.get('products', []) if p['id'] == rel_product_a), None)
                            prod_b = next((p for p in st.session_state.get('products', []) if p['id'] == rel_product_b), None)
                            name_a = f"{prod_a['id']} - {prod_a['name']}" if prod_a else rel_product_a
                            name_b = f"{prod_b['id']} - {prod_b['name']}" if prod_b else rel_product_b
                            st.success(f"✅ Relación agregada: {name_a} ↔ {name_b} ({rel_weight * 100:.0f}%)")
                            # Import here to avoid circular imports
                            from frontend.utils.helpers import load_data
                            load_data()
                            st.rerun()
            else:
                if len(st.session_state.get('products', [])) < 2:
                    st.error("Necesita al menos 2 productos para crear una relación")
                else:
                    st.error("Seleccione dos productos diferentes")