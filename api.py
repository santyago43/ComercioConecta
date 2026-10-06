from flask import Flask, request, jsonify
from models import Product, Relationship
from graph import CommercialGraph

app = Flask(__name__)
graph = CommercialGraph()


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
    """Add a new product"""
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    product_id = data.get('id')
    name = data.get('name')

    if not product_id or not name:
        return jsonify({"error": "Missing 'id' or 'name' field"}), 400

    try:
        product = Product(product_id, name)
        graph.add_product(product)
        return jsonify({"message": f"Product {product_id} added successfully"}), 201
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
    app.run(debug=True, host='127.0.0.1', port=5000)