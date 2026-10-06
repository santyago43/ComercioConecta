# Commit 2: Core con validaciones y CLI

Este commit mejora la base del proyecto agregando:

## Mejoras respecto al commit1
- Validaciones mejoradas en `Relationship` (verificación de tipo numérico para peso)
- Manejo de errores comprehensivo en todas las operaciones
- Prevención de relaciones duplicadas (evita sobrescritura silenciosa)
- Métodos de eliminación de productos y relaciones
- Interfaz de línea de comandos (CLI) interactiva

## Características técnicas
- Validaciones de tipo y rango en Relationship constructor
- Manejo de excepciones específicas (ValueError, TypeError) con mensajes claros
- CLI intuitiva con menú numerado
- Prevención de relaciones duplicadas mediante verificación previa
- Limpieza completa al eliminar productos (elimina todas las relaciones asociadas)
- Persistencia en memoria (los datos se mantienen durante la ejecución)

## Cómo ejecutar
```bash
python main.py
```

Luego use el menú interactivo para:
1. Agregar productos con ID y nombre
2. Listar todos los productos
3. Agregar relaciones especificando IDs de productos y peso (0-1)
4. Listar todas las relaciones
5. Ver información detallada del grafo
6. Eliminar productos y relaciones
7. Salir del programa
