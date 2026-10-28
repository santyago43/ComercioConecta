# ComercioConecta - Feature 2: Exploración de Relaciones

## Resumen

Feature 2 extiende la red comercial inicial con capacidades avanzadas de **análisis y visualización de relaciones** entre productos. Permite a los encargados de tienda descubrir qué productos se compran juntos, identificar grupos aislados y tomar decisiones de *placement* y combos basadas en datos.

---

## Nuevas Capacidades

| Capacidad | Descripción | Valor de Negocio |
|-----------|-------------|------------------|
| **Exploración BFS/DFS** | Recorrido de grafo con límite de profundidad desde cualquier producto | Encontrar combos inmediatos (BFS) o cadenas de influencia (DFS) |
| **Nivel de Relación** | Clasificación semántica: *directo* (dist 1), *indirecto* (dist 2), *lejano* (>2) | Entender fuerza comercial sin interpretar números |
| **Path Completo** | Camino exacto entre producto origen y destino | Explicar *por qué* se recomienda cada producto |
| **Reachability** | Resumen alcanzables vs no alcanzables con motivo | Distinguir "no relacionado" de "relacionado pero lejos" |
| **Componentes Conexos** | Grupos de productos interconectados | Identificar categorías aisladas que necesitan cruce |
| **Visualización 2D** | Layout circular concéntrico interactivo | Ver de un vistazo relaciones y aislamientos |

---

## Endpoints API (Feature 2)

### `GET /explore/bfs/<product_id>?depth=<int>`
Exploración en amplitud (BFS) - **Algoritmo primario para combos**.

**Parámetros:**
- `product_id` (path): ID del producto origen
- `depth` (query, default=2, max=4): Profundidad máxima

**Respuesta:**
```json
{
  "start_product": "P001",
  "max_depth": 2,
  "algorithm": "bfs",
  "results_count": 4,
  "results": [
    {
      "product_id": "P002",
      "product_name": "Pan",
      "distance": 1,
      "cumulative_weight": 0.85,
      "path": ["P001", "P002"],
      "nivel_relacion": "directo",
      "alcanzable": true
    }
  ]
}
```

### `GET /explore/dfs/<product_id>?depth=<int>`
Exploración en profundidad (DFS) - Para *placement* y cadenas largas.

**Respuesta:** Estructura idéntica a BFS, `algorithm: "dfs"`.

### `GET /explore/reachability/<product_id>?depth=<int>`
**Nuevo en Feature 2** - Resumen completo de alcanzabilidad.

**Respuesta:**
```json
{
  "start_product_id": "P001",
  "start_product_name": "Leche",
  "max_depth": 2,
  "total_products": 9,
  "reachable_count": 4,
  "unreachable_count": 4,
  "component_ids": ["P001","P002","P003","P004","P005","P006"],
  "reachable": [...],
  "unreachable": [
    {
      "product_id": "P007",
      "product_name": "Aceite",
      "in_same_component": false,
      "reason": "otro_componente"
    },
    {
      "product_id": "P009",
      "product_name": "Sal",
      "in_same_component": false,
      "reason": "otro_componente"
    }
  ]
}
```

**Motivos de no alcanzabilidad:**
- `fuera_del_alcance`: Mismo componente, pero más allá de `max_depth`
- `otro_componente`: Producto en componente conexo diferente (sin camino posible)

### `GET /components`
Lista todos los componentes conexos (existente, mejorado en Feature 2).

---

## Frontend - Pestaña Exploración 🔍

### Controles
- **Selector de producto**: Dropdown con "ID - Nombre", default al más conectado
- **Slider profundidad**: 1-4 (default 2), con explicación contextual:
  - 1: Solo relaciones directas (amigos inmediatos)
  - 2: Hasta 2 pasos (amigos de amigos) ⭐ *recomendado*
  - 3: Hasta 3 pasos
  - 4: Cadenas largas
- **Botones**: Explorar BFS / Explorar DFS

### Resultados (Tabla Enriquecida)
| Columna | Descripción |
|---------|-------------|
| Distancia | "1 paso", "2 pasos", etc. |
| Producto | "Nombre (ID)" |
| Peso Acumulado | Porcentaje (ej: 76.5%) |
| Fuerza | 🟢 Fuerte (≥70%) / 🟡 Moderada (40-69%) / 🔴 Débil (<40%) |
| Relevancia | ★★★★★ visual basado en peso |

### Visualización 2D (Layout Circular Concéntrico)
```
                    ┌─────────────────┐
                    │   DESCONECTADOS │  ← Gris, área aparte
                    │  (otro componente│
                    │   o aislados)   │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │   ANILLO EXTERIOR  │                    │
        │   (distancia 2+)   │                    │
        │  ● ● ● ● ● ● ● ●   │                    │
        └────────┬───────────┘                    │
                 │                               │
        ┌────────▼────────┐                       │
        │  ANILLO INTERIOR│                       │
        │  (distancia 1)  │                       │
        │   ● ● ● ● ● ●   │                       │
        └────────┬────────┘                       │
                 │                               │
        ┌────────▼────────┐                       │
        │    CENTRO       │                       │
        │  PRODUCTO ORIGEN│                       │
        │      ● ●        │                       │
        └─────────────────┘                       │
```

**Codificación visual:**
- **Nodos**: Tamaño fijo, label con nombre + ID
- **Aristas**: Grosor ∝ peso, Color: 🟢 Verde (alto) → 🟡 Amarillo → 🔴 Rojo (bajo)
- **Leyenda**: Incluida en la visualización

---

## Algoritmos (Implementación Propia)

### BFS - Breadth-First Search
```python
def bfs(self, start_product_id, max_depth=2):
    # Queue: (product, distance, cumulative_weight, path)
    # Retorna: List[Dict] con product, distance, cumulative_weight, path, nivel_relacion, alcanzable
```
- Encuentra camino más corto primero
- Complejidad: O(V + E) acotado por `max_depth`
- **Uso recomendado**: Combos inmediatos, recomendaciones de "comprados juntos"

### DFS - Depth-First Search
```python
def dfs(self, start_product_id, max_depth=2):
    # Stack con path tracking, visitados por camino (no global)
    # Retorna: List[Dict] misma estructura que BFS
```
- Explora una rama hasta el final antes de retroceder
- Evita ciclos con visitados *por camino actual*
- **Uso recomendado**: Estrategias de *placement*, cadenas de influencia larga

### Reachability Summary
```python
def get_reachability_summary(self, start_product_id, max_depth=2):
    # 1. BFS para alcanzables
    # 2. get_component_of_product para componente del origen
    # 3. Diferencia: todos los demás = no alcanzables
    # 4. Clasifica reason: "fuera_del_alcance" vs "otro_componente"
```
- Unifica análisis de conectividad y profundidad
- Base para visualización 2D y decisiones de negocio

### Nivel de Relación
```python
def _nivel_relacion(self, distance):
    if distance == 1: return "directo"
    elif distance == 2: return "indirecto"
    else: return "lejano"
```
- Semántica de negocio sobre distancia numérica
- "directo" = se compran juntos en misma transacción
- "indirecto" = vía un intermediario (ej: Leche → Pan → Mantequilla)
- "lejano" = relación débil, poca acción comercial

---

## Datos de Prueba (Seed Data)

Al iniciar la API se cargan 8 productos y 8 relaciones formando **2 componentes conexos**:

```
COMPONENTE 1 (6 productos - núcleo principal)
  Leche (P001) ──── 0.85 ──── Pan (P002)
       │ 0.70              │ 0.90
       ▼                   ▼
  Huevos (P003) ──── 0.65 ──── Mantequilla (P004)
       │
       │ 0.40
       ▼
  Café (P005) ──── 0.80 ──── Azúcar (P006)

COMPONENTE 2 (2 productos - categoría separada)
  Aceite (P007) ──── 0.75 ──── Arroz (P008)

AISLADO (1 producto - sin relaciones)
  Sal (P009)
```

**Casos de prueba naturales:**
- BFS Leche depth=2 → alcanza Pan, Huevos, Mantequilla, Café
- Reachability Leche depth=2 → 4 alcanzables, 4 no alcanzables (Aceite, Arroz, Sal)
- DFS Leche depth=2 → cadenas como Leche→Pan→Mantequilla
- Producto aislado (Sal) → 0 resultados en cualquier profundidad

---

## Ejecución

### Inicio Rápido
```bash
# Desde directorio comercioconecta/
.\iniciar.bat
# Abre: API en :5000 + Streamlit en :8501
```

### Manual
```bash
# Terminal 1: API
.\.venv\Scripts\python.exe api.py

# Terminal 2: Frontend
.\.venv\Scripts\streamlit.exe run frontend/app.py
```

### Tests de Aceptación Feature 2
```bash
# API debe estar corriendo en :5000
.\.venv\Scripts\python.exe acceptance_test_feature2.py
```

**Escenarios cubiertos (19 aserciones):**
1. Normal: BFS/DFS con path, nivel_relacion, alcanzables esperados
2. Grafo vacío: 404s correctos, 0 componentes
3. Producto inexistente: 404 en BFS/DFS/Reachability
4. Producto aislado: 0 resultados (no inventa)
5. Profundidad insuficiente: P004 no a depth 1 desde Leche
6. Datos inválidos: depth 0/-1 → 400
7. Componentes: ≥2 grupos, aislado en componente propio
8. Reachability: alcanzables/no alcanzables con reasons correctos

---

## Decisiones de Diseño Clave (BITACORA_IA.md)

| Decisión | Rationale |
|----------|-----------|
| **BFS primario** | Camino más corto = combos más relevantes para tienda de barrio |
| **Path en respuesta** | Necesario para visualización 2D y explicabilidad |
| **nivel_relacion semántico** | Usuario de negocio entiende "directo/indirecto" mejor que "dist=1/2" |
| **Endpoint reachability** | Distinguir "no relacionado" vs "relacionado pero lejos" evita falsas recomendaciones |
| **Layout 2D propio (sin NetworkX)** | Guía común prohíbe NetworkX para algoritmos; solo visualización de resultados |
| **Depth máx 4 en UI** | >2 genera ruido; default 2 balancea relevancia/cobertura |

---

## Archivos Principales Feature 2

```
comercioconecta/
├── graph.py                      # +120 líneas: _nivel_relacion, BFS/DFS con path, reachability
├── api.py                        # +50 líneas: endpoints enriquecidos + /reachability
├── acceptance_test_feature2.py   # 145 líneas: 8 escenarios, 19 aserciones
├── frontend/components/
│   └── exploration_tab.py        # UI BFS/DFS + visualización 2D
└── README_FEATURE2.md            # Este archivo
```

---

## Guía Rápida de Uso

| Objetivo | Endpoint / Acción | Profundidad |
|----------|-------------------|-------------|
| **Combos inmediatos** | BFS desde producto estrella | 1-2 |
| **Descubrir influencers** | DFS desde producto nuevo | 2-3 |
| **Ver categorías aisladas** | GET /components | - |
| **Análisis completo producto** | GET /reachability/<id> | 2 |
| **Visualizar en 2D** | Pestaña Exploración → botones | 2 |

---

## Códigos de Estado Comunes Feature 2

| Código | Endpoint | Causa |
|--------|----------|-------|
| 200 | Todos | Éxito |
| 400 | BFS/DFS/Reachability | `depth < 1` |
| 404 | BFS/DFS/Reachability | `product_id` no existe |
| 200 | Reachability | Siempre (incluso 0 alcanzables) |

---

## Referencias

- `BITACORA_IA.md` - Registro completo de decisiones con verificación
- `acceptance_test_feature2.py` - Especificación ejecutable de requisitos
- `graph.py` - Implementación de algoritmos (líneas 127-360)
- `api.py` - Endpoints (líneas 195-300)