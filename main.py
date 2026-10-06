from models import Product, Relationship
from graph import CommercialGraph


def display_menu():
    print("\n=== ComercioConecta - Gestión de Red Comercial ===")
    print("1. Agregar producto")
    print("2. Listar productos")
    print("3. Agregar relación")
    print("4. Listar relaciones")
    print("5. Información del grafo")
    print("6. Eliminar producto")
    print("7. Eliminar relación")
    print("0. Salir")
    print("=" * 50)


def main():
    graph = CommercialGraph()

    while True:
        display_menu()
        try:
            choice = input("Seleccione una opción: ").strip()

            if choice == "0":
                print("¡Hasta luego!")
                break

            elif choice == "1":
                product_id = input("ID del producto: ").strip()
                name = input("Nombre del producto: ").strip()

                if not product_id or not name:
                    print("Error: ID y nombre son requeridos")
                    continue

                try:
                    product = Product(product_id, name)
                    graph.add_product(product)
                    print(f"Producto '{name}' agregado exitosamente")
                except ValueError as e:
                    print(f"Error: {e}")
                except TypeError as e:
                    print(f"Error: {e}")

            elif choice == "2":
                products = graph.get_products()
                if not products:
                    print("No hay productos registrados")
                else:
                    print("\nProductos registrados:")
                    for product in products:
                        print(f"  ID: {product.product_id}, Nombre: {product.name}")

            elif choice == "3":
                product_id_a = input("ID del primer producto: ").strip()
                product_id_b = input("ID del segundo producto: ").strip()
                weight_str = input("Peso de la relación (0-1): ").strip()

                if not product_id_a or not product_id_b or not weight_str:
                    print("Error: Todos los campos son requeridos")
                    continue

                try:
                    weight = float(weight_str)
                    product_a = graph.get_product(product_id_a)
                    product_b = graph.get_product(product_id_b)

                    if product_a is None:
                        print(f"Error: Producto {product_id_a} no existe")
                        continue
                    if product_b is None:
                        print(f"Error: Producto {product_id_b} no existe")
                        continue

                    relationship = Relationship(product_a, product_b, weight)
                    graph.add_relationship(relationship)
                    print(f"Relación entre {product_id_a} y {product_id_b} agregada exitosamente")
                except ValueError as e:
                    print(f"Error: {e}")
                except TypeError as e:
                    print(f"Error: {e}")

            elif choice == "4":
                relationships = graph.get_relationships()
                if not relationships:
                    print("No hay relaciones registradas")
                else:
                    print("\nRelaciones registradas:")
                    for product_a, product_b, weight in relationships:
                        print(f"  {product_a.name} <-> {product_b.name}: peso = {weight}")

            elif choice == "5":
                print(f"\n{graph}")
                products = graph.get_products()
                relationships = graph.get_relationships()
                print(f"Detalle:")
                print(f"  - Productos: {len(products)}")
                print(f"  - Relaciones: {len(relationships)}")

            elif choice == "6":
                product_id = input("ID del producto a eliminar: ").strip()
                if not product_id:
                    print("Error: ID es requerido")
                    continue

                try:
                    graph.remove_product(product_id)
                    print(f"Producto {product_id} eliminado exitosamente")
                except ValueError as e:
                    print(f"Error: {e}")

            elif choice == "7":
                product_id_a = input("ID del primer producto: ").strip()
                product_id_b = input("ID del segundo producto: ").strip()

                if not product_id_a or not product_id_b:
                    print("Error: Ambos IDs son requeridos")
                    continue

                try:
                    graph.remove_relationship(product_id_a, product_id_b)
                    print(f"Relación entre {product_id_a} y {product_id_b} eliminada exitosamente")
                except ValueError as e:
                    print(f"Error: {e}")

            else:
                print("Opción no válida. Intente nuevamente.")

        except KeyboardInterrupt:
            print("\n\n¡Hasta luego!")
            break
        except Exception as e:
            print(f"Error inesperado: {e}")


if __name__ == "__main__":
    main()