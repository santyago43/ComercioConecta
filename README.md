# Commit 4: Exploración completa (BFS, DFS, Componentes)

Este commit implementa los algoritmos de exploración del grafo:
- BFS (Breadth-First Search)
- DFS (Depth-First Search) 
- Componentes conexos
- Endpoints de API para todas las funcionalidades

## Nuevos endpoints implementados

### Exploración BFS
- `GET /explore/bfs/<product_id>?depth=N` - Exploración en amplitud
  - Parámetro opcional `depth` (default: 2)
  - Retorna productos alcanzables con distancia y peso acumulado
  - Ordenado por distancia (asc) y peso acumulado (desc)

### Exploración DFS
- `GET /explore/dfs/<product_id>?depth=N` - Exploración en profundidad
  - Parámetro opcional `depth` (default: 2)
  - Evita ciclos manteniendo registro del camino actual
  - Retorna productos alcanzables con distancia y peso acumulado
  - Ordenado por distancia (asc) y peso acumulado (desc)

### Componentes conexos
- `GET /components` - Obtiene todos los componentes conexos del grafo
  - Cada componente es un grupo de productos interconectados
  - Útil para identificar grupos de productos relacionados

## Características de los algoritmos

### BFS
- Usa cola (FIFO) para explorar por niveles
- Calcula peso acumulado como producto de los pesos de las aristas
- Profundidad máxima configurable para evitar explorar todo el catálogo
- Complejidad: O(V + E) donde V son vértices y E son aristas

### DFS
- Usa pila (LIFO) para explorar en profundidad
- Evita ciclos verificando que no se repita un producto en el camino actual
- También calcula peso acumulado
- Complejidad: O(V + E) en el peor caso

### Componentes conexos
- Aplica BFS desde cada nodo no visitado
- Identifica grupos de productos completamente aislados entre sí
- Complejidad: O(V + E)

## Justificación técnica

### Grafo no dirigido
Las relaciones "se compran juntos" son simétricas por naturaleza:
- Si el aceite se compra con arroz, entonces el arroz se compra con aceite
- Por lo tanto, el grafo es no dirigido y almacenamos las relaciones en ambas direcciones

### Peso acumulado multiplicativo
El peso representa la fuerza de asociación entre productos:
- Se interpreta como probabilidad condicional normalizada
- El peso acumulado en un camino representa la probabilidad conjunta aproximada
- Se usa multiplicación porque asumimos independencia aproximada entre compras sucesivas

### Límite de profundidad
Se justifica por razones de negocio:
- Profundidad 1: Relaciones directas (productos que se compran juntos)
- Profundidad 2: Relaciones vía un intermediario (útil para recomendaciones)
- Profundidad > 2: Puede generar recomendaciones poco relevantes ("todo el catálogo")
- Depth 2 proporciona equilibrio entre utilidad y especificidad

## Cómo ejecutar
```bash
# Instalar dependencias
pip install -r requirements.txt

# Iniciar el servidor
python api.py
```

La API estará disponible en http://127.0.0.1:5000

## Ejemplos de uso

### BFS desde producto P001 con profundidad 2
```
GET /explore/bfs/P001?depth=2
```

### DFS desde producto P001 con profundidad 1
```
GET /explore/dfs/P001?depth=1
```

### Obtener componentes conexos
```
GET /components
```

## Próximos pasos
- Implementar frontend mínimo con Streamlit
- Crear script de aceptación completo
- Actualizar documentación y bitácora de IA