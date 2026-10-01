from models import Product, Relationship


class CommercialGraph:
    def __init__(self):
        # Adjacency list: dict[Product, dict[Product, float]]
        self.graph = {}
        # Products dictionary for O(1) lookup by ID
        self.products = {}

    def add_product(self, product):
        """Add a product to the graph"""
        if product.product_id in self.products:
            raise ValueError(f"Product with ID {product.product_id} already exists")

        self.products[product.product_id] = product
        self.graph[product] = {}

    def add_relationship(self, relationship):
        """Add a symmetric relationship between two products"""
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

    def __repr__(self):
        return f"CommercialGraph(products={len(self.products)}, relationships={len(self.get_relationships())})"