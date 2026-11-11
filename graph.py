"""
ComercioConecta Graph Module
============================

This module defines the `CommercialGraph` class, which represents an undirected weighted graph
of products and their relationships. It provides methods for:

- Adding/removing products and relationships
- Retrieving products and relationships
- Performing graph traversals (BFS/DFS) with depth limits
- Finding connected components
- Serializing the graph to a dictionary for JSON API responses

The graph uses an adjacency list representation with a dictionary for O(1) product lookup by ID.
Relationships are stored symmetrically (undirected) with a numeric weight indicating strength.
"""

from collections import deque
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

    def _nivel_relacion(self, distance):
        """
        Clasifica el nivel de relacion comercial segun la distancia en el grafo.
        - distancia 1: directo (se compran juntos inmediatamente)
        - distancia 2: indirecto (se compran juntos vía un intermediario)
        - distancia > 2: lejano (relacion debil, poca relevancia comercial)
        """
        if distance == 1:
            return "directo"
        elif distance == 2:
            return "indirecto"
        else:
            return "lejano"

    def _require_product(self, product_id: str) -> Product:
        """Devuelve el producto o lanza ValueError si no existe"""
        product = self.get_product(product_id)
        if product is None:
            raise ValueError(f"Product {product_id} does not exist")
        return product

    def _traversal_result(self, product: Product, distance: int, cumulative_weight: float,
                          path: list[Product]) -> dict:
        """Una fila de resultado de BFS/DFS"""
        return {
            "product": product,
            "distance": distance,
            "cumulative_weight": cumulative_weight,
            "path": list(path),
            "nivel_relacion": self._nivel_relacion(distance),
            "alcanzable": True,
        }

    @staticmethod
    def _sort_results(results: list[dict]) -> list[dict]:
        """Ordena por distancia (ascendente) y luego por peso acumulado (descendente)"""
        results.sort(key=lambda x: (x["distance"], -x["cumulative_weight"]))
        return results

    def bfs(self, start_product_id, max_depth=2):
        """
        Breadth-First Search from a starting product.
        Returns list of dicts with: product, distance, cumulative_weight, path, nivel_relacion, alcanzable.
        BFS es el algoritmo primario porque encuentra el camino mas corto primero,
        ideal para identificar productos directamente relacionados (distancia 1)
        y relacionados via intermediario (distancia 2).
        """
        start_product = self._require_product(start_product_id)

        # Queue for BFS: (product, distance, cumulative_weight, path)
        queue = deque([(start_product, 0, 1.0, [start_product])])
        visited = {start_product}
        results = []

        while queue:
            current_product, distance, cumulative_weight, path = queue.popleft()

            # Don't include the starting product in results with distance 0
            if distance > 0:
                results.append(self._traversal_result(current_product, distance, cumulative_weight, path))

            # Stop if we've reached max depth
            if distance >= max_depth:
                continue

            # Explore neighbors
            for neighbor, weight in self.graph[current_product].items():
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, distance + 1, cumulative_weight * weight, path + [neighbor]))

        return self._sort_results(results)

    def dfs(self, start_product_id, max_depth=2):
        """
        Depth-First Search from a starting product.
        Returns list of dicts with: product, distance, cumulative_weight, path, nivel_relacion, alcanzable.
        DFS explora una cadena lo mas lejos posible antes de retroceder.
        Util para descubrir rutas largas de influencia (estrategia de placement),
        no es el algoritmo primario para recomendacion de combos inmediatos.
        """
        start_product = self._require_product(start_product_id)

        # Stack for DFS: (product, distance, cumulative_weight, path)
        stack = [(start_product, 0, 1.0, [start_product])]
        results = []

        while stack:
            current_product, distance, cumulative_weight, path = stack.pop()

            # Don't include the starting product in results with distance 0
            if distance > 0:
                results.append(self._traversal_result(current_product, distance, cumulative_weight, path))

            # Stop if we've reached max depth
            if distance >= max_depth:
                continue

            # Explore neighbors (in reverse order to maintain consistent ordering)
            for neighbor, weight in reversed(list(self.graph[current_product].items())):
                if neighbor not in path:  # Avoid cycles
                    stack.append((neighbor, distance + 1, cumulative_weight * weight, path + [neighbor]))

        return self._sort_results(results)

    def get_connected_components(self):
        """
        Find all connected components in the graph.
        Returns list of lists, where each inner list contains products in a component.
        """
        visited = set()
        components = []

        for product in self.products.values():
            if product not in visited:
                # Start BFS from this unvisited product
                component = []
                queue = deque([product])
                visited.add(product)

                while queue:
                    current_product = queue.popleft()
                    component.append(current_product)

                    # Add unvisited neighbors to queue
                    for neighbor in self.graph[current_product]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)

                components.append(component)

        return components

    def get_component_of_product(self, product_id):
        """
        Returns the connected component (list of products) that contains the given product.
        Returns None if the product does not exist.
        Useful to determine if two products are in the same group or are disconnected.
        """
        product = self.get_product(product_id)
        if product is None:
            return None

        components = self.get_connected_components()
        for component in components:
            if product in component:
                return component

        return None

    @staticmethod
    def _reachable_details(bfs_results: list[dict]) -> list[dict]:
        """Resultados de BFS con ids y nombres, ordenados por distancia y peso"""
        reachable = [
            {
                "product_id": r["product"].product_id,
                "product_name": r["product"].name,
                "distance": r["distance"],
                "cumulative_weight": r["cumulative_weight"],
                "path": [p.product_id for p in r["path"]],
                "nivel_relacion": r["nivel_relacion"],
                "alcanzable": r["alcanzable"],
            }
            for r in bfs_results
        ]
        reachable.sort(key=lambda x: (x["distance"], -x["cumulative_weight"]))
        return reachable

    def _unreachable_details(self, unreachable_ids: set[str], component_ids: set[str]) -> list[dict]:
        """No alcanzables con su motivo: mismo grupo primero, luego otros grupos"""
        unreachable = []
        for pid in unreachable_ids:
            in_same_component = pid in component_ids
            unreachable.append({
                "product_id": pid,
                "product_name": self.products[pid].name,
                "in_same_component": in_same_component,
                "reason": "fuera_del_alcance" if in_same_component else "otro_componente",
            })
        unreachable.sort(key=lambda x: (not x["in_same_component"], x["product_name"]))
        return unreachable

    def get_reachability_summary(self, start_product_id, max_depth=2):
        """
        Summary of reachability from a starting product: reachable (BFS within max_depth),
        unreachable (other components or beyond depth), component_ids, total and per-list counts.
        """
        start_product = self._require_product(start_product_id)

        # Get reachable products via BFS
        reachable_results = self.bfs(start_product_id, max_depth)
        reachable_ids = {r["product"].product_id for r in reachable_results}

        # Get the component of the start product
        component = self.get_component_of_product(start_product_id)
        component_ids = {p.product_id for p in component} if component else set()

        # Unreachable: other components AND same component but beyond max_depth
        unreachable_ids = {pid for pid in self.products if pid != start_product_id} - reachable_ids

        reachable = self._reachable_details(reachable_results)
        unreachable = self._unreachable_details(unreachable_ids, component_ids)

        return {
            "start_product_id": start_product_id,
            "start_product_name": start_product.name,
            "max_depth": max_depth,
            "reachable": reachable,
            "unreachable": unreachable,
            "reachable_count": len(reachable),
            "unreachable_count": len(unreachable),
            "total_products": len(self.products),
            "component_ids": list(component_ids) if component else [],
        }

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