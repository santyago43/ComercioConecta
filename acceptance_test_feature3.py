#!/usr/bin/env python3
"""
Pruebas de aceptación de Feature 3: Propuesta comercial justificable.
La API debe estar corriendo; estas pruebas borran sus datos en memoria.
Reinicie la API después para recuperar los datos iniciales.
"""
import sys

import requests

BASE_URL = "http://127.0.0.1:5000"
passed = total = 0


def check(condition, description, detail=""):
    global passed, total
    total += 1
    if condition:
        passed += 1
        print(f"  [PASS] {description}")
    else:
        print(f"  [FAIL] {description} {detail}")


def scenario(title):
    print(f"\n{title}\n" + "-" * 70)


def clear():
    for product in requests.get(f"{BASE_URL}/products").json()["products"]:
        requests.delete(f"{BASE_URL}/products/{product['id']}")


def load(products, relationships):
    clear()
    for product_id, name in products:
        requests.post(f"{BASE_URL}/products", json={"id": product_id, "name": name})
    for id_a, id_b, weight in relationships:
        requests.post(f"{BASE_URL}/relationships", json={"product_a": id_a, "product_b": id_b, "weight": weight})


def get(product_id):
    response = requests.get(f"{BASE_URL}/recommendations/{product_id}")
    return response.status_code, response.json()


def ids(data):
    return [p["product_id"] for p in data["proposals"]]


def codes(data):
    return {e["product_id"]: e["reason_code"] for e in data["excluded"]}


PRODUCTS = [("P001", "Leche"), ("P002", "Pan"), ("P003", "Huevos"), ("P004", "Mantequilla"),
            ("P005", "Café"), ("P006", "Azúcar"), ("P007", "Aceite"), ("P008", "Arroz"), ("P009", "Sal")]
RELATIONSHIPS = [("P001", "P002", .85), ("P001", "P003", .70), ("P002", "P004", .90), ("P003", "P004", .65),
                 ("P005", "P006", .80), ("P007", "P008", .75), ("P001", "P005", .40), ("P002", "P003", .55)]


def normal_case():
    scenario("1. Caso normal: propuesta explicable desde Leche")
    load(PRODUCTS, RELATIONSHIPS)
    status, data = get("P001")
    check(status == 200, "Responde 200", status)
    check(ids(data) == ["P002", "P003", "P005", "P004"], "Directas primero y luego indirecta", ids(data))
    check("P001" not in ids(data), "No se recomienda a sí mismo")
    check(all(p["reason"] for p in data["proposals"]), "Cada propuesta trae razón")
    mantequilla = data["proposals"][-1]
    check(mantequilla["type"] == "indirecta" and mantequilla["path"] == ["P001", "P002", "P004"],
          "Mantequilla usa el camino más fuerte, vía Pan", mantequilla)
    check(mantequilla["strength"] == 0.765, "Fuerza verificable 0.85 × 0.90 = 0.765", mantequilla["strength"])
    check(codes(data).get("P006") == "indirecta_debil", "Azúcar se descarta por débil", codes(data))
    check(len(data["direct_connections"]) == 3, "Muestra las 3 conexiones directas")


def separate_groups():
    scenario("2. Grupos separados")
    status, data = get("P007")
    check(status == 200 and ids(data) == ["P008"], "Aceite solo propone Arroz", ids(data))
    check(codes(data).get("P001") == "otro_componente", "Leche queda como otro grupo", codes(data))
    check(codes(data).get("P009") == "otro_componente", "Sal queda como otro grupo", codes(data))


def isolated_product():
    scenario("3. Producto aislado")
    status, data = get("P009")
    check(status == 200, "Responde 200", status)
    check(data["proposals_count"] == 0, "Propuesta vacía")
    check("no tiene relaciones" in data["message"], "Lo comunica sin inventar", data["message"])


def sparse_network():
    scenario("4. Red escasa")
    load([("A", "Té"), ("B", "Galletas"), ("C", "Vela"), ("D", "Fósforos")],
         [("A", "B", .60), ("C", "D", .10)])
    _, data = get("A")
    check(ids(data) == ["B"], "Con una sola relación propone un solo producto", ids(data))
    _, data = get("C")
    check(data["proposals_count"] == 0, "Con relación débil no propone nada")
    check("ninguna alcanza" in data["message"], "Explica por qué no hay propuesta", data["message"])
    check(codes(data).get("D") == "directa_debil", "Descarta con razón", codes(data))


def beyond_reach():
    scenario("5. Producto fuera del alcance de 2 pasos")
    load([("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")],
         [("A", "B", .9), ("B", "C", .9), ("C", "D", .9)])
    _, data = get("A")
    check(ids(data) == ["B", "C"], "Propone solo hasta 2 pasos", ids(data))
    check(codes(data).get("D") == "fuera_del_alcance", "D queda fuera de alcance", codes(data))


def load_order():
    scenario("6. El resultado no depende del orden de carga")
    load(PRODUCTS, list(reversed(RELATIONSHIPS)))
    _, data = get("P001")
    check(ids(data) == ["P002", "P003", "P005", "P004"], "Mismo orden", ids(data))
    check(data["proposals"][-1]["strength"] == 0.765, "Misma fuerza", data["proposals"][-1])


def missing_product():
    scenario("7. Producto inexistente")
    status, data = get("P999")
    check(status == 404 and "error" in data, "Responde 404 con error", status)


def invalid_data():
    scenario("8. Dato inválido")
    for weight, description in ((1.5, "peso mayor a 1"), (0, "peso cero"), (-0.2, "peso negativo")):
        response = requests.post(f"{BASE_URL}/relationships",
                                 json={"product_a": "P001", "product_b": "P009", "weight": weight})
        check(response.status_code == 400, f"Rechaza {description}", response.status_code)
    _, data = get("P009")
    check(data["proposals_count"] == 0, "Los datos rechazados no generan propuesta")


def empty_network():
    scenario("9. Red vacía")
    clear()
    status, data = get("P001")
    check(status == 404 and "vacía" in data.get("error", ""), "Comunica que la red está vacía", data)


def main():
    print("=" * 70 + "\nPruebas de aceptación - ComercioConecta Feature 3\n" + "=" * 70)
    for run in (normal_case, separate_groups, isolated_product, sparse_network, beyond_reach,
                load_order, missing_product, invalid_data, empty_network):
        run()
    print("\n" + "=" * 70 + f"\nRESUMEN: {passed}/{total} pruebas pasaron")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
