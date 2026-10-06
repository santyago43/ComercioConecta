from models import Product, Relationship


class CommercialGraph:
    def __init__(self):
        # Adjacency list: dict[Product, dict[Product, float]]
        self.graph = {}
        # Products dictionary for O(1) lookup by ID
        self.products = {}

    def add_product(self, product):
        """Add a product to the graph"""
        if not isinstance(product, Product):
            raise TypeError("Only Product instances can be added")

        if product.product_id in self.products:
            raise ValueError(f"Product with ID {product.product_id} already exists")

        self.products[product.product_id] = product
        self.graph[product] = {}

    def add_relationship(self, relationship):
        """Add a symmetric relationship between two products"""
        if not isinstance(relationship, Relationship):
            raise TypeError("Only Relationship instances can be added")

        prod_a = relationship.product_a
        prod_b = relationship.product_b
        weight = relationship.weight

        # Validate products exist
        if prod_a.product_id not in self.products:
            raise ValueError(f"Product {prod_a.product_id} does not exist")
        if prod_b.product_id not in self.products:
            raise ValueError(f"Product {prod_b.product_id} does not exist")

        # Get product objects
        product_a_obj = self.products[prod_a.product_id]
        product_b_obj = self.products[prod_b.product_id]

        # Check if relationship already exists (undirected graph)
        if product_b_obj in self.graph[product_a_obj]:
            raise ValueError(f"Relationship between {prod_a.product_id} and {prod_b.product_id} already exists")

        # Add symmetric relationship (undirected graph)
        self.graph[product_a_obj][product_b_obj] = weight
        self.graph[product_b_obj][product_a_obj] = weight

    def get_product(self, product_id):
        """Get product by ID (O(1) lookup)"""
        return self.products.get(product_id)

    def get_products(self):
        """Get all products"""
        return list(self.products.values())

    def get_relationships(self):
        """Get all unique relationships"""
        relationships = []
        seen = set()

        for product, neighbors in self.graph.items():
            for neighbor, weight in neighbors.items():
                # Create a unique identifier for the relationship
                rel_id = tuple(sorted([product.product_id, neighbor.product_id]))
                if rel_id not in seen:
                    seen.add(rel_id)
                    relationships.append((product, neighbor, weight))

        return relationships

    def remove_product(self, product_id):
        """Remove a product and its relationships"""
        product = self.get_product(product_id)
        if product is None:
            raise ValueError(f"Product {product_id} does not exist")

        # Remove all relationships involving this product
        if product in self.graph:
            # Create a copy of neighbors to avoid modifying dict during iteration
            neighbors = list(self.graph[product].keys())
            for neighbor in neighbors:
                # Remove the relationship from neighbor's adjacency list
                if neighbor in self.graph:
                    self.graph[neighbor].pop(product, None)
                # Remove from product's adjacency list
                self.graph[product].pop(neighbor, None)
            # Remove the product from graph
            del self.graph[product]

        # Remove from products dictionary
        del self.products[product_id]

    def remove_relationship(self, product_id_a, product_id_b):
        """Remove a relationship between two products"""
        product_a = self.get_product(product_id_a)
        product_b = self.get_product(product_id_b)

        if product_a is None:
            raise ValueError(f"Product {product_id_a} does not exist")
        if product_b is None:
            raise ValueError(f"Product {product_id_b} does not exist")

        # Check if relationship exists
        if product_b not in self.graph[product_a]:
            raise ValueError(f"Relationship between {product_id_a} and {product_id_b} does not exist")

        # Remove the relationship (undirected graph)
        del self.graph[product_a][product_b]
        del self.graph[product_b][product_a]

    def to_dict(self):
        """Convert graph to dictionary for JSON serialization"""
        return {
            "products": [{"id": p.product_id, "name": p.name} for p in self.get_products()],
            "relationships": [
                {
                    "product_a": p_a.product_id,
                    "product_b": p_b.product_id,
                    "weight": weight
                }
                for p_a, p_b, weight in self.get_relationships()
            ]
        }

    def __repr__(self):
        return f"CommercialGraph(products={len(self.products)}, relationships={len(self.get_relationships())})"