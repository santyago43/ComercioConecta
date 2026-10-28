# PR 2: API Endpoint Updates

## Resumen
Actualización de endpoints REST en `api.py` para exponer la funcionalidad mejorada de Feature 2. Incluye formato de respuesta enriquecido para BFS/DFS y nuevo endpoint de reachability.

## Archivos Modificados
- `ComercioConecta/api.py` (~50 líneas agregadas/modificadas)

## Cambios Detallados

### 1. Endpoint BFS Actualizado (`GET /explore/bfs/<product_id>?depth=<int>`)

**Nueva respuesta (antes era tuplas simples):**
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
    },
    {
      "product_id": "P004",
      "product_name": "Mantequilla",
      "distance": 2,
      "cumulative_weight": 0.765,
      "path": ["P001", "P002", "P004"],
      "nivel_relacion": "indirecto",
      "alcanzable": true
    }
  ]
}
```

**Cambios en código:**
- Agregado campo `"algorithm": "bfs"` para identificación
- Cada resultado incluye `path`, `nivel_relacion`, `alcanzable`
- Docstring expandido explicando por qué BFS es primario

### 2. Endpoint DFS Actualizado (`GET /explore/dfs/<product_id>?depth=<int>`)

**Nueva respuesta (ahora consistente con BFS):**
```json
{
  "start_product": "P001",
  "max_depth": 2,
  "algorithm": "dfs",
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
    // ... mismos campos que BFS
  ]
}
```

**Cambios en código:**
- Agregado campo `"algorithm": "dfs"`
- Estructura idéntica a BFS para consistencia en frontend
- Docstring expandido explicando uso para cadenas largas de influencia

### 3. Nuevo Endpoint: Reachability (`GET /explore/reachability/<product_id>?depth=<int>`)

**Respuesta completa:**
```json
{
  "start_product_id": "P001",
  "start_product_name": "Leche",
  "max_depth": 2,
  "total_products": 9,
  "reachable_count": 4,
  "unreachable_count": 4,
  "component_ids": ["P001", "P002", "P003", "P004", "P005"],
  "reachable": [
    {
      "product_id": "P002",
      "product_name": "Pan",
      "distance": 1,
      "cumulative_weight": 0.85,
      "path": ["P001", "P002"],
      "nivel_relacion": "directo",
      "alcanzable": true
    }
    // ... todos los alcanzables con detalles completos
  ],
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
    // ... productos en otros componentes o fuera de depth
  ]
}
```

**Parámetros:**
- `product_id` (path): ID del producto origen
- `depth` (query, opcional, default=2): Profundidad máxima

**Códigos de respuesta:**
- `200`: Éxito con resumen completo
- `400`: Depth inválido (< 1)
- `404`: Producto no existe
- `400`: Error interno (excepción genérica)

### 4. Mejor Manejo de Errores

**BFS/DFS/Reachability:** Todos capturan `Exception` genérica y retornan 400 con mensaje de error.

## Impacto en Frontend

El frontend (`exploration_tab.py`) ya está preparado para consumir:
- `path` → Para visualización 2D (dibujar aristas entre nodos intermedios)
- `nivel_relacion` → Para mostrar badges semánticos (Directo/Indirecto/Lejano)
- `alcanzable` → Para lógica de visualización (siempre true en BFS/DFS resultados)
- Endpoint reachability → Para vista 2D completa con zona de desconectados

## Dependencias

**Requiere:** PR 1 (graph.py) - Los nuevos campos vienen de `graph.bfs()`, `graph.dfs()`, `graph.get_reachability_summary()`

## Validación

```bash
# Iniciar API
python api.py

# En otra terminal, probar endpoints
curl "http://127.0.0.1:5000/explore/bfs/P001?depth=2" | jq '.results[0] | keys'
# Debe mostrar: algorithm, results_count, results (con path, nivel_relacion, alcanzable)

curl "http://127.0.0.1:5000/explore/dfs/P001?depth=2" | jq '.results[0] | keys'
# Misma estructura que BFS

curl "http://127.0.0.1:5000/explore/reachability/P001?depth=2" | jq '. | keys'
# Debe mostrar: start_product_id, start_product_name, max_depth, total_products, reachable_count, unreachable_count, component_ids, reachable, unreachable

# Probar errores
curl "http://127.0.0.1:5000/explore/bfs/P001?depth=0"  # Debe retornar 400
curl "http://127.0.0.1:5000/explore/reachability/P999?depth=2"  # Debe retornar 404
```

## Notas de Implementación

- **Breaking change**: Formato de respuesta BFS/DFS cambió (era tuplas, ahora objetos)
- **Versionado**: Considerar versionar API si hay consumidores externos
- **Performance**: Endpoint reachability llama internamente a BFS + análisis de componentes, O(V+E)
- **Consistencia**: BFS y DFS ahora tienen estructura idéntica para facilitar frontend
