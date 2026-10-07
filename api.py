"""
ComercioConecta API
===================

This Flask application provides a RESTful API for managing a commercial graph of products and their relationships.
It supports CRUD operations on products and relationships, as well as graph traversal (BFS/DFS) and connected component analysis.

Endpoints:
- GET /products -> list all products
- GET /products/<product_id> -> get a specific product
- POST /products -> add a new product (requires JSON with 'id' and 'name')
- DELETE /products/<product_id> -> delete a product
- GET /relationships -> list all relationships
- POST /relationships -> add a relationship (requires JSON with 'product_a', 'product_b', 'weight')
- GET /graph/info -> general info about the graph (node/edge counts)
- GET /explore/bfs/<product_id>?depth=<int> -> BFS traversal from product_id up to given depth
- GET /explore/dfs/<product_id>?depth=<int> -> DFS traversal from product_id up to given depth
- GET /components -> list connected components in the graph

Error handling returns appropriate HTTP status codes and JSON error messages.
"""
from flask import Flask, request, jsonify
from models import Product, Relationship
from graph import CommercialGraph

app = Flask(__name__)
graph = CommercialGraph()

# Datos de prueba iniciales (se cargan al arrancar la API)
_initial_products = [
    ("P001", "Leche"),
    ("P002", "Pan"),
    ("P003", "Huevos"),
    ("P004", "Mantequilla"),
    ("P005", "Café"),
    ("P006", "Azúcar"),
    ("P007", "Aceite"),
    ("P008", "Arroz"),
]

_initial_relationships = [
    ("P001", "P002", 0.85),  # Leche - Pan
    ("P001", "P003", 0.70),  # Leche - Huevos
    ("P002", "P004", 0.90),  # Pan - Mantequilla
    ("P003", "P004", 0.65),  # Huevos - Mantequilla
    ("P005", "P006", 0.80),  # Café - Azúcar
    ("P007", "P008", 0.75),  # Aceite - Arroz
    ("P001", "P005", 0.40),  # Leche - Café
    ("P002", "P003", 0.55),  # Pan - Huevos
]

for pid, name in _initial_products:
    try:
        graph.add_product(Product(pid, name))
    except ValueError:
        pass  # Ya existe

for pid_a, pid_b, weight in _initial_relationships:
    try:
        prod_a = graph.get_product(pid_a)
        prod_b = graph.get_product(pid_b)
        if prod_a and prod_b:
            graph.add_relationship(Relationship(prod_a, prod_b, weight))
    except ValueError:
        pass  # Ya existe o error de validación


@app.route('/products', methods=['GET'])
def get_products():
    """Get all products"""
    products = graph.get_products()
    return jsonify({
        "count": len(products),
        "products": [{"id": p.product_id, "name": p.name} for p in products]
    }), 200


@app.route('/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product"""
    product = graph.get_product(product_id)
    if product is None:
        return jsonify({"error": f"Product {product_id} not found"}), 404

    return jsonify({"id": product.product_id, "name": product.name}), 200


@app.route('/products', methods=['POST'])
def add_product():
    """Add a new product - auto-generates ID if not provided"""
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    product_id = data.get('id')
    name = data.get('name')

    if not name:
        return jsonify({"error": "Missing 'name' field"}), 400

    # Auto-generate ID if not provided (format: P001, P002, ...)
    if not product_id:
        existing_products = graph.get_products()
        max_num = 0
        for p in existing_products:
            if p.product_id.startswith('P'):
                try:
                    num = int(p.product_id[1:])
                    if num > max_num:
                        max_num = num
                except ValueError:
                    pass
        product_id = f"P{max_num + 1:03d}"

    try:
        product = Product(product_id, name)
        graph.add_product(product)
        return jsonify({
            "message": f"Product {product_id} added successfully",
            "product": {"id": product_id, "name": name}
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 409  # Conflict - duplicate
    except TypeError as e:
        return jsonify({"error": str(e)}), 400


@app.route('/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product"""
    try:
        graph.remove_product(product_id)
        return jsonify({"message": f"Product {product_id} deleted successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@app.route('/relationships', methods=['GET'])
def get_relationships():
    """Get all relationships"""
    relationships = graph.get_relationships()
    return jsonify({
        "count": len(relationships),
        "relationships": [
            {
                "product_a": p_a.product_id,
                "product_b": p_b.product_id,
                "weight": weight
            }
            for p_a, p_b, weight in relationships
        ]
    }), 200


@app.route('/relationships', methods=['POST'])
def add_relationship():
    """Add a new relationship"""
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    product_id_a = data.get('product_a')
    product_id_b = data.get('product_b')
    weight = data.get('weight')

    if not product_id_a or not product_id_b or weight is None:
        return jsonify({"error": "Missing 'product_a', 'product_b', or 'weight' field"}), 400

    try:
        weight = float(weight)
        product_a = graph.get_product(product_id_a)
        product_b = graph.get_product(product_id_b)

        if product_a is None:
            return jsonify({"error": f"Product {product_id_a} not found"}), 404
        if product_b is None:
            return jsonify({"error": f"Product {product_id_b} not found"}), 404

        relationship = Relationship(product_a, product_b, weight)
        graph.add_relationship(relationship)
        return jsonify({"message": f"Relationship between {product_id_a} and {product_id_b} added successfully"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400  # Bad request - invalid weight or duplicate
    except TypeError as e:
        return jsonify({"error": str(e)}), 400


@app.route('/graph/info', methods=['GET'])
def get_graph_info():
    """Get general information about the graph"""
    return jsonify(graph.to_dict()), 200


@app.route('/explore/bfs/<product_id>', methods=['GET'])
def explore_bfs(product_id):
    """Explore products using BFS from a starting product"""
    try:
        depth = request.args.get('depth', 2, type=int)
        if depth < 1:
            return jsonify({"error": "Depth must be at least 1"}), 400

        results = graph.bfs(product_id, depth)

        return jsonify({
            "start_product": product_id,
            "max_depth": depth,
            "results_count": len(results),
            "results": [
                {
                    "product_id": p.product_id,
                    "product_name": p.name,
                    "distance": distance,
                    "cumulative_weight": weight
                }
                for p, distance, weight in results
            ]
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/explore/dfs/<product_id>', methods=['GET'])
def explore_dfs(product_id):
    """Explore products using DFS from a starting product"""
    try:
        depth = request.args.get('depth', 2, type=int)
        if depth < 1:
            return jsonify({"error": "Depth must be at least 1"}), 400

        results = graph.dfs(product_id, depth)

        return jsonify({
            "start_product": product_id,
            "max_depth": depth,
            "results_count": len(results),
            "results": [
                {
                    "product_id": p.product_id,
                    "product_name": p.name,
                    "distance": distance,
                    "cumulative_weight": weight
                }
                for p, distance, weight in results
            ]
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/components', methods=['GET'])
def get_components():
    """Get all connected components in the graph"""
    components = graph.get_connected_components()

    return jsonify({
        "components_count": len(components),
        "components": [
            [
                {
                    "product_id": p.product_id,
                    "product_name": p.name
                }
                for p in component
            ]
            for component in components
        ]
    }), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)