# ComercioConecta - Feature 1: Red comercial inicial

## Descripción del proyecto

ComercioConecta es una aplicación que ayuda a tiendas de barrio a entender qué productos se compran juntos para proponer combinaciones comerciales razonables. Esta implementación corresponde a la **Feature 1: Red comercial inicial**, que permite crear y listar productos y relaciones, rechazando duplicados y datos inválidos, y mostrando la red mediante una API REST y una interfaz frontend.

## Características implementadas

### Backend (API REST)
- **Lenguaje**: Python 3.13
- **Framework**: Flask 3.1
- **Endpoints disponibles**:
  - `GET /products` - Listar todos los productos
  - `GET /products/<id>` - Obtener producto específico
  - `POST /products` - Agregar nuevo producto (ID auto-generado: P001, P002, ...)
  - `DELETE /products/<id>` - Eliminar producto
  - `GET /relationships` - Listar todas las relaciones
  - `POST /relationships` - Agregar nueva relación
  - `GET /graph/info` - Obtener información completa del grafo
  - `GET /explore/bfs/<id>?depth=N` - Exploración en amplitud (BFS)
  - `GET /explore/dfs/<id>?depth=N` - Exploración en profundidad (DFS)
  - `GET /components` - Obtener componentes conexos del grafo
- **Datos de prueba (seed data)**: 8 productos y 8 relaciones precargados al iniciar

### Frontend (Interfaz Streamlit)
- **Tecnología**: Streamlit 1.64
- **Pestañas**:
  - 📦 **Productos**: Catálogo con ID y nombre, agregar productos (solo nombre, ID auto)
  - 🔗 **Relaciones**: Tabla con "ID - Nombre" en ambas columnas, pesos como %, agregar con dropdowns
  - 🔍 **Exploración**: BFS/DFS con selector "ID - Nombre", peso acumulado como %
  - 📊 **Componentes**: Grupos de productos interconectados con detalle expandible
- **Carga automática**: Datos se cargan al abrir la app (sin botón de refresh)
- **Validaciones locales con detalle**:
  - Producto duplicado → muestra ID y nombre del existente
  - Relación duplicada → muestra ambos productos, peso actual vs intentado

### Algoritmos de grafo propios
- **Grafo no dirigido**: Las relaciones "se compran juntos" son simétricas
- **BFS (Breadth-First Search)**: Exploración por niveles con peso acumulado
- **DFS (Depth-First Search)**: Exploración en profundidad evitando ciclos
- **Componentes conexos**: Identifica grupos de productos aislados entre sí
- **Validaciones**:
  - Productos únicos por nombre (case-insensitive)
  - Relaciones no duplicadas (en ninguna dirección A-B = B-A)
  - Pesos en rango (0, 1]
  - Relaciones solo entre productos diferentes
  - Profundidad mínima de 1 en exploraciones

## Decisiones de diseño

### Modelo de grafo
- **Representación**: Lista de adyacencia usando diccionarios anidados
- **Dirección**: No dirigido (relaciones simétricas)
- **Peso**: Valor en (0, 1] representando fuerza/frecuencia de co-compra normalizada
- **Justificación**: Una relación "se compran juntos" es inherentemente simétrica - si el producto A se compra con el producto B, entonces el producto B se compra con el producto A

### Algoritmo de exploración
- **BFS seleccionado** para consultas de relaciones porque:
  - Encuentra el camino más corto primero
  - Es intuitivo para usuarios que quieren ver relaciones cercanas
  - Permite controlar el alcance con el parámetro de profundidad
- **Límite de profundidad 2** justificado por:
  - Profundidad 1: Relaciones directas (útiles para paquetes inmediatos)
  - Profundidad 2: Relaciones vía un intermediario (útiles para recomendaciones de combos)
  - Profundidad > 2: Tiende a generar recomendaciones poco relevantes o demasiado amplias
- **Peso acumulado multiplicativo**: Representa aproximación de probabilidad conjunta en cadena de compras

## Requisitos del sistema

- Python 3.12+
- Dependencias listadas en `requirements.txt`

## Instalación y ejecución

### Opción 1: Ejecutar todo con un solo comando (recomendado)
```bash
# Desde el directorio comercioconecta/
.\iniciar.bat
```
Este script abrirá automáticamente dos ventanas:
1. API Flask en http://127.0.0.1:5000
2. Frontend Streamlit en http://localhost:8501

### Opción 2: Ejecutar manualmente
```bash
# 1. Crear entorno virtual (si no existe)
python -m venv .venv

# 2. Activar entorno virtual
.\.venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Iniciar la API (en una terminal)
.\.venv\Scripts\python.exe api.py

# 5. Iniciar el frontend (en otra terminal)
.\.venv\Scripts\streamlit.exe run frontend/app.py
```

## Pruebas de aceptación

Ejecutar el script de pruebas contra la API local:
```bash
.\.venv\Scripts\python.exe acceptance_test.py --start
```
El script iniciará la API automáticamente, ejecutará las pruebas y guardará los resultados en `acceptance_output.txt`.

## Estructura del proyecto

```
comercioconecta/
├── api.py                 # API REST con Flask
├── graph.py               # Implementación del grafo y algoritmos
├── models.py              # Clases Product y Relationship
├── requirements.txt       # Dependencias del proyecto
├── acceptance_test.py     # Script de pruebas de aceptación
├── iniciar.bat            # Script para lanzamiento doble (API + Frontend)
├── frontend/
│   └── app.py             # Interfaz Streamlit
└── README.md              # Este archivo
```

## Endpoints de la API

### Productos
```
GET    /products
GET    /products/<id>
POST   /products     {"name": "<string>"}          # ID auto-generado (P001, P002, ...)
DELETE /products/<id>
```

### Relaciones
```
GET    /relationships
POST   /relationships {"product_a": "<string>", "product_b": "<string>", "weight": <float>}
```

### Información y exploración
```
GET    /graph/info
GET    /explore/bfs/<id>?depth=<int>
GET    /explore/dfs/<id>?depth=<int>
GET    /components
```

### Códigos de estado HTTP
- 200: Éxito
- 201: Recurso creado
- 400: Solicitud inválida (datos faltantes o inválidos)
- 404: Recurso no encontrado
- 409: Conflicto (duplicado)
- 500: Error interno del servidor

## Datos de prueba (Seed Data)

Al iniciar la API, se cargan automáticamente:

**Productos (8):**
| ID | Nombre |
|----|--------|
| P001 | Leche |
| P002 | Pan |
| P003 | Huevos |
| P004 | Mantequilla |
| P005 | Café |
| P006 | Azúcar |
| P007 | Aceite |
| P008 | Arroz |

**Relaciones (8):**
| Producto A | Producto B | Peso | % |
|------------|------------|------|---|
| Leche | Pan | 0.85 | 85% |
| Leche | Huevos | 0.70 | 70% |
| Pan | Mantequilla | 0.90 | 90% |
| Huevos | Mantequilla | 0.65 | 65% |
| Café | Azúcar | 0.80 | 80% |
| Aceite | Arroz | 0.75 | 75% |
| Leche | Café | 0.40 | 40% |
| Pan | Huevos | 0.55 | 55% |

**Componentes conexos (2):**
1. **Componente principal** (6 productos): Leche, Pan, Huevos, Café, Mantequilla, Azúcar
2. **Componente secundario** (2 productos): Aceite, Arroz