class Product:
    def __init__(self, product_id, name):
        self.product_id = product_id
        self.name = name

    def __eq__(self, other):
        if isinstance(other, Product):
            return self.product_id == other.product_id
        return False

    def __hash__(self):
        return hash(self.product_id)

    def __repr__(self):
        return f"Product(id={self.product_id}, name='{self.name}')"


class Relationship:
    def __init__(self, product_a, product_b, weight):
        # Validate products are different
        if product_a.product_id == product_b.product_id:
            raise ValueError("Cannot create relationship with same product")

        # Validate weight is in (0, 1]
        if not isinstance(weight, (int, float)) or not (0 < weight <= 1):
            raise ValueError("Weight must be a numeric value in range (0, 1]")

        self.product_a = product_a
        self.product_b = product_b
        self.weight = float(weight)  # Ensure it's stored as float

    def __repr__(self):
        return f"Relationship({self.product_a.product_id} <-> {self.product_b.product_id}, weight={self.weight})"