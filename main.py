from models import Product, Relationship
from graph import CommercialGraph


def main():
    # Create graph
    graph = CommercialGraph()

    # Create some products
    product1 = Product("P001", "Aceite")
    product2 = Product("P002", "Arroz")
    product3 = Product("P003", "Fideos")
    product4 = Product("P004", "Leche")

    # Add products to graph
    graph.add_product(product1)
    graph.add_product(product2)
    graph.add_product(product3)
    graph.add_product(product4)

    print("Productos agregados:")
    for product in graph.get_products():
        print(f"  {product}")

    # Create relationships
    rel1 = Relationship(product1, product2, 0.8)  # Aceite y Arroz
    rel2 = Relationship(product2, product3, 0.6)  # Arroz y Fideos
    rel3 = Relationship(product1, product4, 0.3)  # Aceite y Leche

    # Add relationships to graph
    graph.add_relationship(rel1)
    graph.add_relationship(rel2)
    graph.add_relationship(rel3)

    print("\nRelaciones agregadas:")
    for product_a, product_b, weight in graph.get_relationships():
        print(f"  {product_a.name} <-> {product_b.name}: peso = {weight}")

    # Show graph info
    print(f"\n{graph}")


if __name__ == "__main__":
    main()