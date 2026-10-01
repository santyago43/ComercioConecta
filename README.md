Setup inicial

Este commit establece la base del proyecto ComercioConecta con:

## Implementado
- Clase `Product` con ID y nombre
- Clase `Relationship` con validaciones (productos distintos, peso en (0,1])
- Clase `CommercialGraph` con:
  - Grafo no dirigido (relaciones simétricas)
  - Lista de adyacencia para almacenar relaciones
  - Diccionario de productos para búsqueda O(1) por ID
  - Métodos para agregar productos y relaciones
  - Métodos para obtener productos y relaciones

## Características técnicas
- Uso de tipado implícito siguiendo buenas prácticas de Python
- Validaciones en el constructor de Relationship
- Búsqueda O(1) de productos por ID mediante diccionario
- Evitación de relaciones duplicadas mediante conjunto de seguimiento
- Representación clara de objetos mediante `__repr__`

## Cómo ejecutar
```bash
python main.py
```
