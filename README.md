# Commit 3: API REST

Este commit implementa una API REST usando Flask para exponer la funcionalidad del grafo comercial.

## Endpoints implementados

### Productos
- `GET /products` - Obtener todos los productos
- `GET /products/<id>` - Obtener un producto específico
- `POST /products` - Agregar un nuevo producto
- `DELETE /products/<id>` - Eliminar un producto

### Relaciones
- `GET /relationships` - Obtener todas las relaciones
- `POST /relationships` - Agregar una nueva relación

### Información del grafo
- `GET /graph/info` - Obtener información completa del grafo

## Formatos de datos

### Producto
```json
{
  "id": "P001",
  "name": "Aceite"
}
```

### Relación
```json
{
  "product_a": "P001",
  "product_b": "P002",
  "weight": 0.8
}
```

### Respuesta de error
```json
{
  "error": "Descripción del error"
}
```

## Códigos de estado HTTP
- 200: Éxito
- 201: Recurso creado
- 400: Solicitud inválida (datos faltantes o inválidos)
- 404: Recurso no encontrado
- 409: Conflicto (producto o relación duplicada)
- 500: Error interno del servidor

## Cómo ejecutar
```bash
# Instalar dependencias
pip install -r requirements.txt

# Iniciar el servidor
python api.py
```

La API estará disponible en http://127.0.0.1:5000

## Próximos pasos (commit4)
- Implementar algoritmos de exploración (BFS, DFS, componentes conexos)
- Agregar endpoints de exploración
- Mantener documentación actualizada