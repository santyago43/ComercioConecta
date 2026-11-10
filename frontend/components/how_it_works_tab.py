"""
Sección con la explicación de la regla comercial y de los algoritmos
"""
import streamlit as st

from frontend.utils import ui

# Los puntos que se explican en el pitch: modelado, estructura, algoritmo, complejidad, caso borde y evidencia
TECHNICAL_ANALYSIS = """
<div class="cc-tech-grid">
  <article class="cc-tech-card">
    <h3>1 · Modelado</h3>
    <ul>
      <li><strong>Nodos:</strong> productos.</li>
      <li><strong>Aristas:</strong> co-compra entre dos productos.</li>
      <li><strong>Dirección:</strong> ninguna. A–B vale igual que B–A.</li>
      <li><strong>Peso:</strong> índice de 0 a 1, sintético.</li>
    </ul>
  </article>
  <article class="cc-tech-card">
    <h3>2 · Estructura de datos</h3>
    <p>Lista de adyacencia propia: un diccionario donde cada producto guarda a sus vecinos con el peso. Cada relación se guarda por los dos lados. Otro diccionario busca productos por ID en O(1).</p>
    <div class="cc-code">Leche → {Pan: 0.85, Huevos: 0.70, Café: 0.40}<br>Pan → {Leche: 0.85, Mantequilla: 0.90, Huevos: 0.55}</div>
  </article>
  <article class="cc-tech-card">
    <h3>3 · Algoritmo y por qué</h3>
    <p>La propuesta mira los vecinos del producto y los vecinos de esos vecinos (2 pasos). Revisa todos los caminos de 2 pasos y no solo el primero, así el resultado no depende del orden de carga. La fuerza indirecta es el producto de los pesos del camino más fuerte.</p>
    <p>BFS explora por niveles y sirve para el análisis y la alcanzabilidad: encuentra primero lo más cercano. DFS no se usa para proponer porque repite productos por cada camino.</p>
  </article>
  <article class="cc-tech-card">
    <h3>4 · Complejidad</h3>
    <ul>
      <li><strong>BFS:</strong> O(V + E). Cada producto y relación se visita una vez.</li>
      <li><strong>Grupos:</strong> O(V + E). Un recorrido por grupo.</li>
      <li><strong>Propuesta:</strong> revisa vecinos y vecinos de vecinos, y calcula los grupos para explicar los descartes. En el peor caso, O(V + E).</li>
      <li><strong>DFS por caminos:</strong> puede repetir productos y crecer rápido en redes muy conectadas; por eso lleva límite de profundidad.</li>
    </ul>
  </article>
  <article class="cc-tech-card">
    <h3>5 · Caso borde</h3>
    <p>Un producto sin relaciones no genera propuesta, para no inventar recomendaciones. Un producto de otro grupo no se propone y aparece entre los descartados con su motivo.</p>
  </article>
  <article class="cc-tech-card">
    <h3>6 · Evidencia</h3>
    <p>El script de aceptación ejecuta 9 escenarios contra la API: caso normal, grupos separados, producto aislado, red escasa, fuera del alcance, orden de carga, producto inexistente, dato inválido y red vacía. La regla también tiene pruebas unitarias.</p>
    <div class="cc-code">acceptance_test_feature3.py<br>test_recommendation.py</div>
  </article>
  <article class="cc-tech-card">
    <h3>7 · Límites y sesgos</h3>
    <ul>
      <li>Una relación directa débil queda por encima de una indirecta más fuerte.</li>
      <li>Los mínimos de fuerza y el tope de productos son criterio de negocio, no están calibrados con datos reales. Pueden dejar fuera relaciones válidas.</li>
      <li>Multiplicar pesos hace que cada paso reste fuerza: las cadenas largas pierden.</li>
      <li>Los productos con más relaciones tienen más caminos para aparecer como indirectos.</li>
      <li>El peso no dice qué producto se compra primero.</li>
      <li>Los datos son sintéticos: no se concluye nada sobre clientes reales.</li>
    </ul>
  </article>
</div>
"""


def render_how_it_works_tab():
    """Renderiza la explicación de la propuesta y los algoritmos"""
    ui.page_header("Cómo funciona", "Qué hace el sistema para llegar a cada propuesta y qué límites tiene.")

    ui.render("""
    <div class="cc-prose">
      <h2>En pocas palabras</h2>
      <p>El sistema mira qué productos se compran juntos. Si el cliente lleva Leche y Leche se compra con Pan, recomienda Pan. Si Pan además se compra con Mantequilla y esa cadena es fuerte, también puede recomendar Mantequilla. Cuando no hay compras que relacionen los productos, no recomienda nada.</p>

      <h2>Cómo se arma la propuesta</h2>
      <ul>
        <li><strong>Alcance limitado.</strong> Solo se miran productos a máximo 2 pasos del producto de interés.</li>
        <li><strong>Primero lo observado.</strong> Van primero las relaciones directas y después las indirectas, cada grupo por fuerza.</li>
        <li><strong>Fuerza mínima.</strong> Una relación indirecta se infiere, por eso se le exige más que a una directa. Los valores aparecen en el detalle técnico de cada recomendación.</li>
        <li><strong>Sin inventar.</strong> Nunca se propone el mismo producto ni productos de otro grupo.</li>
        <li><strong>Con razón.</strong> Cada producto propuesto o descartado indica por qué.</li>
      </ul>
      <p>La fuerza de una relación indirecta es el producto de los pesos de su camino. Si hay varios caminos de 2 pasos, se usa el más fuerte.</p>

      <h2>Qué significa el peso</h2>
      <p>Es un <strong>índice simétrico de co-compra entre 0 y 1</strong>, con datos sintéticos. A–B vale lo mismo que B–A, por eso el grafo es no dirigido. No indica qué producto se compra primero.</p>

      <h2>Qué son los grupos</h2>
      <p>Son los componentes conexos del grafo: conjuntos de productos unidos por alguna cadena de relaciones. Dos productos en grupos distintos no tienen relación demostrable, así que nunca se recomiendan entre sí.</p>

    </div>
    """)

    with st.expander("Para el análisis técnico", icon=":material/engineering:", expanded=True):
        ui.render(TECHNICAL_ANALYSIS)

    ui.render('<div class="cc-prose"><h2>BFS y DFS</h2></div>')
    ui.render(ui.table(
        [("", False), ("BFS: búsqueda en amplitud", False), ("DFS: búsqueda en profundidad", False)],
        [
            ["<strong>Cómo explora</strong>", "Por niveles: primero los productos directos, luego los de 2 pasos.",
             "Sigue una cadena lo más lejos posible antes de retroceder."],
            ["<strong>Sirve para</strong>", "Encontrar productos relacionados cercanos.",
             "Descubrir rutas largas de influencia."],
            ["<strong>Ejemplo</strong>", "Desde Leche encuentra primero Pan y Huevos, luego Mantequilla.",
             "Desde Leche puede seguir Leche → Pan → Mantequilla."],
            ["<strong>En esta aplicación</strong>", "Análisis avanzado y cálculo de alcanzabilidad.",
             "Análisis avanzado. No se usa para proponer porque repite productos."],
        ],
    ))
