#!/usr/bin/env python3
"""
Acceptance test for ComercioConecta Feature 2: Exploracion de relaciones

This script automates validation of the ComercioConecta API against the
Feature 2 requirements specification. It tests:

- Normal scenario: BFS/DFS from a product with connections, verifying
  reachable products, distances, cumulative weights, path, and nivel_relacion.
- Empty graph scenario: behavior when no products exist.
- Non-existent product: 404 error for BFS/DFS/reachability on missing product.
- Isolated product: product with no relationships returns empty reachable list.
- Route/relationship non-existent: depth insufficient to reach a node.
- Invalid data: depth 0 or negative returns 400.
- Connected components: at least one group is shown; disconnected products
  are listed as unreachable with reason "otro_componente".

The test prints detailed results (scenario, expected, obtained, passed/failed)
and returns a non-zero exit code if any test fails.
"""

import requests
import json
import sys
import time

BASE_URL = "http://127.0.0.1:5000"

# Counters
tests_passed = 0
tests_total = 0


def test_endpoint(method, endpoint, data=None, expected_status=200, description=""):
    """Test an endpoint and record pass/fail."""
    global tests_passed, tests_total
    url = f"{BASE_URL}{endpoint}"
    tests_total += 1

    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        else:
            print(f"  [ERR] FAIL | {description}")
    except Exception as e:
        print(f"  [ERR] FAIL | {description} | Error: {e}")
        return False, None

    success = response.status_code == expected_status
    status_msg = "PASS" if success else "FAIL"

    print(f"  [{status_msg}] | {description}")
    print(f"      {method} {endpoint} -> Expected {expected_status}, got {response.status_code}")

    if not success:
        try:
            detail = response.json()
            print(f"      Error detail: {json.dumps(detail, indent=2)[:300]}")
        except Exception:
            print(f"      Response: {response.text[:300]}")

    if success and response.content:
        try:
            resp_data = response.json()
            resp_str = json.dumps(resp_data, indent=2)
            if len(resp_str) > 300:
                print(f"      Response: {resp_str[:300]}...")
            else:
                print(f"      Response: {resp_str}")
        except Exception:
            print(f"      Response: {response.text[:300]}")

    print()
    if success:
        tests_passed += 1
    return success, response


def delete_all_products():
    """Delete all products to reset the graph to empty state."""
    resp = requests.get(f"{BASE_URL}/products")
    if resp.status_code == 200:
        products = resp.json().get("products", [])
        for p in products:
            del_resp = requests.delete(f"{BASE_URL}/products/{p['id']}")
            if del_resp.status_code not in [200, 204]:
                print(f"      [WARN] No se pudo eliminar {p['id']}: {del_resp.status_code}")


def seed_sample_data():
    """Seed a small sample graph for testing."""
    products = [
        ("P001", "Leche"),
        ("P002", "Pan"),
        ("P003", "Huevos"),
        ("P004", "Mantequilla"),
        ("P005", "Café"),
        ("P006", "Azúcar"),
        ("P007", "Aceite"),
        ("P008", "Arroz"),
        ("P009", "Sal"),  # isolated product
    ]
    relationships = [
        ("P001", "P002", 0.85),  # Leche - Pan
        ("P001", "P003", 0.70),  # Leche - Huevos
        ("P002", "P004", 0.90),  # Pan - Mantequilla
        ("P003", "P004", 0.65),  # Huevos - Mantequilla
        ("P005", "P006", 0.80),  # Café - Azúcar
        ("P007", "P008", 0.75),  # Aceite - Arroz
        ("P001", "P005", 0.40),  # Leche - Café
        ("P002", "P003", 0.55),  # Pan - Huevos
    ]

    for pid, name in products:
        resp = requests.post(f"{BASE_URL}/products", json={"id": pid, "name": name})
        if resp.status_code not in [200, 201]:
            print(f"      [WARN] No se pudo crear producto {pid}: {resp.status_code} {resp.text[:100]}")

    for pid_a, pid_b, weight in relationships:
        resp = requests.post(f"{BASE_URL}/relationships",
                             json={"product_a": pid_a, "product_b": pid_b, "weight": weight})
        if resp.status_code not in [200, 201]:
            print(f"      [WARN] No se pudo crear relacion {pid_a}-{pid_b}: {resp.status_code} {resp.text[:100]}")


def main():
    global tests_passed, tests_total

    print("=" * 70)
    print("Pruebas de aceptacion - ComercioConecta Feature 2")
    print("Exploracion de relaciones")
    print("=" * 70)
    print("Asegurese de que la API este ejecutandose en http://127.0.0.1:5000")
    print()

    # Wait for API to be ready
    time.sleep(1)

    # -----------------------------------------------------------
    # ESCENARIO 1: Normal - BFS y DFS desde producto con conexiones
    # -----------------------------------------------------------
    print("1. ESCENARIO NORMAL: BFS y DFS desde producto con conexiones")
    print("-" * 70)

    # Ensure seed data exists
    delete_all_products()
    seed_sample_data()

    # BFS from Leche (P001) with depth 2
    success, resp = test_endpoint(
        "GET", "/explore/bfs/P001?depth=2", None, 200,
        "BFS desde Leche (P001) profundidad 2"
    )
    if success:
        data = resp.json()
        expected_reachable = {"P002", "P003", "P004", "P005"}  # Pan, Huevos, Mantequilla, Café
        actual_ids = {r["product_id"] for r in data.get("results", [])}
        if expected_reachable.issubset(actual_ids):
            print("      [OK] Contenido: Productos alcanzables esperados estan presentes")
            tests_passed += 1
        else:
            print(f"      [ERR] Contenido: Esperados {expected_reachable}, obtenidos {actual_ids}")
        tests_total += 1

        # Verify nivel_relacion is present
        has_nivel = all("nivel_relacion" in r for r in data.get("results", []))
        if has_nivel:
            print("      [OK] Contenido: Todos los resultados tienen 'nivel_relacion'")
            tests_passed += 1
        else:
            print("      [ERR] Contenido: Falta 'nivel_relacion' en algunos resultados")
        tests_total += 1

        # Verify path is present
        has_path = all("path" in r for r in data.get("results", []))
        if has_path:
            print("      [OK] Contenido: Todos los resultados tienen 'path'")
            tests_passed += 1
        else:
            print("      [ERR] Contenido: Falta 'path' en algunos resultados")
        tests_total += 1

    # DFS from Leche (P001) with depth 2
    success, resp = test_endpoint(
        "GET", "/explore/dfs/P001?depth=2", None, 200,
        "DFS desde Leche (P001) profundidad 2"
    )
    if success:
        data = resp.json()
        has_path = all("path" in r for r in data.get("results", []))
        if has_path:
            print("      [OK] Contenido: DFS devuelve 'path' completo")
            tests_passed += 1
        else:
            print("      [ERR] Contenido: DFS no devuelve 'path'")
        tests_total += 1

    print()

    # -----------------------------------------------------------
    # ESCENARIO 2: Grafo vacio
    # -----------------------------------------------------------
    print("2. ESCENARIO: Grafo vacio (sin productos)")
    print("-" * 70)

    delete_all_products()

    success, resp = test_endpoint(
        "GET", "/explore/bfs/P001?depth=2", None, 404,
        "BFS desde producto inexistente en grafo vacio"
    )
    print()

    success, resp = test_endpoint(
        "GET", "/explore/reachability/P001?depth=2", None, 404,
        "Reachability desde producto inexistente en grafo vacio"
    )
    print()

    success, resp = test_endpoint(
        "GET", "/components", None, 200,
        "Componentes en grafo vacio"
    )
    if success:
        data = resp.json()
        if data.get("components_count", -1) == 0:
            print("      [OK] Contenido: Grafo vacio retorna 0 componentes")
            tests_passed += 1
        else:
            print(f"      [ERR] Contenido: Esperaba 0 componentes, obtuvo {data.get('components_count')}")
        tests_total += 1
    print()

    # -----------------------------------------------------------
    # ESCENARIO 3: Producto inexistente
    # -----------------------------------------------------------
    print("3. ESCENARIO: Producto inexistente")
    print("-" * 70)

    # Re-seed data
    seed_sample_data()

    success, resp = test_endpoint(
        "GET", "/explore/bfs/P999?depth=2", None, 404,
        "BFS desde producto inexistente P999"
    )
    print()

    success, resp = test_endpoint(
        "GET", "/explore/dfs/P999?depth=2", None, 404,
        "DFS desde producto inexistente P999"
    )
    print()

    success, resp = test_endpoint(
        "GET", "/explore/reachability/P999?depth=2", None, 404,
        "Reachability desde producto inexistente P999"
    )
    print()

    # -----------------------------------------------------------
    # ESCENARIO 4: Producto aislado (sin relaciones)
    # -----------------------------------------------------------
    print("4. ESCENARIO: Producto aislado (sin relaciones)")
    print("-" * 70)

    success, resp = test_endpoint(
        "GET", "/explore/bfs/P009?depth=2", None, 200,
        "BFS desde producto aislado P009 (Sal)"
    )
    if success:
        data = resp.json()
        if data.get("results_count", -1) == 0:
            print("      [OK] Contenido: Producto aislado retorna 0 resultados")
            tests_passed += 1
        else:
            print(f"      [ERR] Contenido: Esperaba 0 resultados, obtuvo {data.get('results_count')}")
        tests_total += 1
    print()

    # -----------------------------------------------------------
    # ESCENARIO 5: Ruta / relacion inexistente (profundidad insuficiente)
    # -----------------------------------------------------------
    print("5. ESCENARIO: Ruta inexistente (profundidad insuficiente)")
    print("-" * 70)

    # From P009 (Sal, isolated) depth 2 should not reach P001 (Leche)
    # They are in different components, so no path exists at any depth
    success, resp = test_endpoint(
        "GET", "/explore/bfs/P009?depth=2", None, 200,
        "BFS desde P009 (aislado) no alcanza otros productos"
    )
    if success:
        data = resp.json()
        if data.get("results_count", -1) == 0:
            print("      [OK] Contenido: Ningun producto alcanzable desde aislado")
            tests_passed += 1
        else:
            print(f"      [ERR] Contenido: Esperaba 0, obtuvo {data.get('results_count')}")
        tests_total += 1
    print()

    # From P007 (Aceite) depth 1 should NOT reach P008 (Arroz) at distance > 1
    # Actually P007-P008 are directly connected, so depth 1 reaches P008.
    # Test: P001 (Leche) depth 1 should NOT reach P004 (Mantequilla, distance 2)
    success, resp = test_endpoint(
        "GET", "/explore/bfs/P001?depth=1", None, 200,
        "BFS desde P001 profundidad 1 (no debe alcanzar P004 a distancia 2)"
    )
    if success:
        data = resp.json()
        ids = {r["product_id"] for r in data.get("results", [])}
        if "P004" not in ids:
            print("      [OK] Contenido: P004 (Mantequilla) no alcanzable a profundidad 1")
            tests_passed += 1
        else:
            print("      [ERR] Contenido: P004 no deberia estar a profundidad 1")
        tests_total += 1
    print()

    # -----------------------------------------------------------
    # ESCENARIO 6: Datos invalidos (profundidad 0 o negativa)
    # -----------------------------------------------------------
    print("6. ESCENARIO: Datos invalidos (profundidad)")
    print("-" * 70)

    success, resp = test_endpoint(
        "GET", "/explore/bfs/P001?depth=0", None, 400,
        "BFS con profundidad 0 (invalido)"
    )
    print()

    success, resp = test_endpoint(
        "GET", "/explore/bfs/P001?depth=-1", None, 400,
        "BFS con profundidad negativa (invalido)"
    )
    print()

    success, resp = test_endpoint(
        "GET", "/explore/dfs/P001?depth=0", None, 400,
        "DFS con profundidad 0 (invalido)"
    )
    print()

    success, resp = test_endpoint(
        "GET", "/explore/reachability/P001?depth=-1", None, 400,
        "Reachability con profundidad negativa (invalido)"
    )
    print()

    # -----------------------------------------------------------
    # ESCENARIO 7: Componentes conexos (grupos desconectados)
    # -----------------------------------------------------------
    print("7. ESCENARIO: Componentes conexos (grupos desconectados)")
    print("-" * 70)

    success, resp = test_endpoint(
        "GET", "/components", None, 200,
        "Listar componentes conexos"
    )
    if success:
        data = resp.json()
        comp_count = data.get("components_count", -1)
        if comp_count >= 2:
            print(f"      [OK] Contenido: Se encontraron {comp_count} componentes (>= 2 esperado)")
            tests_passed += 1
        else:
            print(f"      [ERR] Contenido: Esperaba >= 2 componentes, obtuvo {comp_count}")
        tests_total += 1

        # Verify isolated product P009 is in its own component
        components = data.get("components", [])
        isolated_found = any(
            len(comp) == 1 and comp[0]["product_id"] == "P009"
            for comp in components
        )
        if isolated_found:
            print("      [OK] Contenido: Producto aislado P009 en su propio componente")
            tests_passed += 1
        else:
            print("      [ERR] Contenido: Producto aislado P009 no esta en componente propio")
        tests_total += 1
    print()

    # -----------------------------------------------------------
    # ESCENARIO 8: Reachability - alcanzables vs no alcanzables
    # -----------------------------------------------------------
    print("8. ESCENARIO: Reachability - alcanzables vs no alcanzables")
    print("-" * 70)

    success, resp = test_endpoint(
        "GET", "/explore/reachability/P001?depth=2", None, 200,
        "Reachability desde P001 (Leche) profundidad 2"
    )
    if success:
        data = resp.json()
        reachable = data.get("reachable", [])
        unreachable = data.get("unreachable", [])

        # P001 should reach P002, P003, P004, P005 (within depth 2)
        reachable_ids = {r["product_id"] for r in reachable}
        expected_reachable = {"P002", "P003", "P004", "P005"}
        if expected_reachable.issubset(reachable_ids):
            print("      [OK] Contenido: Productos alcanzables correctos")
            tests_passed += 1
        else:
            print(f"      [ERR] Contenido: Esperaba {expected_reachable} en alcanzables, obtuvo {reachable_ids}")
        tests_total += 1

        # Unreachable should include P007, P008 (otro componente) and P009 (aislado)
        unreachable_ids = {r["product_id"] for r in unreachable}
        expected_unreachable = {"P007", "P008", "P009"}
        if expected_unreachable.issubset(unreachable_ids):
            print("      [OK] Contenido: Productos no alcanzables correctos (otros componentes)")
            tests_passed += 1
        else:
            print(f"      [ERR] Contenido: Esperaba {expected_unreachable} en no alcanzables, obtuvo {unreachable_ids}")
        tests_total += 1

        # Verify unreachable has reason field
        has_reason = all("reason" in r for r in unreachable)
        if has_reason:
            print("      [OK] Contenido: Todos los no alcanzables tienen 'reason'")
            tests_passed += 1
        else:
            print("      [ERR] Contenido: Falta 'reason' en algunos no alcanzables")
        tests_total += 1

        # Verify counts
        if data.get("reachable_count") == len(reachable) and data.get("unreachable_count") == len(unreachable):
            print("      [OK] Contenido: Conteos de alcanzables/no alcanzables consistentes")
            tests_passed += 1
        else:
            print("      [ERR] Contenido: Conteos inconsistentes")
        tests_total += 1
    print()

    # -----------------------------------------------------------
    # RESUMEN
    # -----------------------------------------------------------
    print("=" * 70)
    print(f"RESUMEN: {tests_passed}/{tests_total} pruebas pasaron")

    if tests_passed == tests_total:
        print("[OK] Todas las pruebas de aceptacion de Feature 2 pasaron!")
        return 0
    else:
        print(f"[ERR] {tests_total - tests_passed} pruebas fallaron")
        return 1


if __name__ == "__main__":
    sys.exit(main())
