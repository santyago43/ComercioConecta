#!/usr/bin/env python3
"""
Acceptance test for ComercioConecta Feature 4: Panel comercial demostrable (Edge Cases)

This script validates edge cases and Feature 4 specific integration:
6. Disconnected components: Multiple separate groups
7. Recommendation edge cases: Weak relationships, limit exceeded, different components
8. Graph visualization integration (Feature 4): Data structure verification
"""

import requests
import json
import sys
import time

BASE_URL = "http://127.0.0.1:5000"


def test_endpoint(method, endpoint, data=None, expected_status=200, description=""):
    """Test an endpoint and return success/failure with response"""
    url = f"{BASE_URL}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        else:
            print(f"Unsupported method: {method}")
            return False, f"Unsupported method: {method}", None

        success = response.status_code == expected_status
        status_msg = "✓ PASS" if success else "✗ FAIL"

        print(f"{status_msg} {description}")
        print(f"    {method} {endpoint} - Expected {expected_status}, got {response.status_code}")

        if not success:
            try:
                error_detail = response.json()
                print(f"    Error: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"    Response: {response.text[:200]}")

        if success and response.content:
            try:
                response_data = response.json()
                response_str = json.dumps(response_data, indent=2)
                if len(response_str) > 300:
                    print(f"    Response: {response_str[:300]}...")
                else:
                    print(f"    Response: {response_str}")
            except:
                print(f"    Response: {response.text[:300]}")

        print()
        return success, response.status_code, response.json() if success and response.content else None

    except requests.exceptions.ConnectionError:
        print(f"✗ FAIL {description}")
        print(f"    {method} {endpoint} - Connection error. Is the API running?")
        print()
        return False, None, None
    except Exception as e:
        print(f"✗ FAIL {description}")
        print(f"    {method} {endpoint} - Error: {e}")
        print()
        return False, None, None


def clear_test_data():
    """Helper to clean up test data by deleting all products"""
    try:
        resp = requests.get(f"{BASE_URL}/products")
        if resp.status_code == 200:
            products = resp.json().get("products", [])
            for p in products:
                requests.delete(f"{BASE_URL}/products/{p['id']}")
    except:
        pass


def main():
    print("Ejecutando pruebas de aceptación Feature 4 - ESCENARIOS EDGE")
    print("=" * 70)
    print("Asegúrese de que la API esté ejecutándose en http://127.0.0.1:5000")
    print()

    tests_passed = 0
    tests_total = 0

    time.sleep(1)

    # ============================================================
    # SCENARIO 6: COMPONENTES DESCONECTADOS
    # ============================================================
    print("6. ESCENARIO: COMPONENTES DESCONECTADOS (grupos separados)")
    clear_test_data()

    products = [
        ("A001", "Producto A1"), ("A002", "Producto A2"), ("A003", "Producto A3"),
        ("B001", "Producto B1"), ("B002", "Producto B2"),
    ]
    for pid, name in products:
        test_endpoint("POST", "/products", {"id": pid, "name": name}, 201, f"Crear {name}")

    relationships = [
        ("A001", "A002", 0.8), ("A002", "A003", 0.7),
        ("B001", "B002", 0.9),
    ]
    for a, b, w in relationships:
        test_endpoint("POST", "/relationships", {"product_a": a, "product_b": b, "weight": w}, 201,
                      f"Crear relación {a}-{b}")

    tests_total += 1
    success, _, data = test_endpoint("GET", "/components", None, 200,
                                     "Componentes con grupos separados")
    if success:
        tests_passed += 1
        assert data["components_count"] == 2, f"Expected 2 components, got {data['components_count']}"

    tests_total += 1
    success, _, data = test_endpoint("GET", "/recommendations/A001", None, 200,
                                     "Recomendaciones desde componente A")
    if success:
        tests_passed += 1
        proposal_ids = [p["product_id"] for p in data["proposals"]]
        assert "B001" not in proposal_ids and "B002" not in proposal_ids, \
            "Proposals should not include products from other component"
        excluded_ids = [e["product_id"] for e in data["excluded"] if e["reason_code"] == "otro_componente"]
        assert "B001" in excluded_ids and "B002" in excluded_ids, \
            "B products should be excluded with 'otro_componente' reason"

    # ============================================================
    # SCENARIO 7: CASOS EDGE DE RECOMENDACIONES
    # ============================================================
    print("7. ESCENARIO: CASOS EDGE DE RECOMENDACIONES")
    clear_test_data()

    products = [
        ("E001", "Centro"), ("E002", "Fuerte"), ("E003", "Media"),
        ("E004", "Debil"), ("E005", "Indirecta_Fuerte"), ("E006", "Indirecta_Debil"),
    ]
    for pid, name in products:
        test_endpoint("POST", "/products", {"id": pid, "name": name}, 201, f"Crear {name}")

    test_endpoint("POST", "/relationships", {"product_a": "E001", "product_b": "E002", "weight": 0.9}, 201, "Fuerte")
    test_endpoint("POST", "/relationships", {"product_a": "E001", "product_b": "E003", "weight": 0.5}, 201, "Media")
    test_endpoint("POST", "/relationships", {"product_a": "E001", "product_b": "E004", "weight": 0.2}, 201, "Débil")
    test_endpoint("POST", "/relationships", {"product_a": "E002", "product_b": "E005", "weight": 0.8}, 201, "Indirecta fuerte")
    test_endpoint("POST", "/relationships", {"product_a": "E003", "product_b": "E006", "weight": 0.3}, 201, "Indirecta débil")

    tests_total += 1
    success, _, data = test_endpoint("GET", "/recommendations/E001", None, 200,
                                     "Recomendaciones con fuerzas variadas")
    if success:
        tests_passed += 1
        if data["proposals"]:
            assert data["proposals"][0]["product_id"] == "E002", "Strongest direct should be first"
            assert data["proposals"][0]["type"] == "directa"

        excluded_codes = [e["reason_code"] for e in data["excluded"]]
        assert "directa_debil" in excluded_codes, "Weak direct should be excluded (min_direct=0.3)"
        assert "indirecta_debil" in excluded_codes, "Weak indirect should be excluded (min_indirect=0.5)"

        indirect_included = any(p["product_id"] == "E005" for p in data["proposals"])
        assert indirect_included, "Strong indirect (0.72) should be included"

    # Test limit enforcement (max 5 proposals)
    clear_test_data()
    for i in range(1, 8):
        test_endpoint("POST", "/products", {"id": f"L{i:03d}", "name": f"Producto {i}"}, 201, f"Crear L{i:03d}")
    for i in range(1, 7):
        test_endpoint("POST", "/relationships", {"product_a": "L001", "product_b": f"L{i+1:03d}", "weight": 0.8}, 201, f"L001-L{i+1}")

    tests_total += 1
    success, _, data = test_endpoint("GET", "/recommendations/L001", None, 200,
                                     "Límite de 5 productos en propuestas")
    if success:
        tests_passed += 1
        assert data["proposals_count"] <= 5, f"Proposals should be limited to 5, got {data['proposals_count']}"
        over_limit = [e for e in data["excluded"] if e["reason_code"] == "fuera_del_limite"]
        assert len(over_limit) >= 1, "Should have over-limit exclusions"

    # ============================================================
    # SCENARIO 8: VISUALIZACIÓN DE GRAFO (Feature 4)
    # ============================================================
    print("8. ESCENARIO: VISUALIZACIÓN DE GRAFO (integración Feature 4)")
    clear_test_data()

    products = [
        ("V001", "Centro"), ("V002", "Vecino1"), ("V003", "Vecino2"),
        ("V004", "Lejano"), ("V005", "Aislado"),
    ]
    for pid, name in products:
        test_endpoint("POST", "/products", {"id": pid, "name": name}, 201, f"Crear {name}")

    test_endpoint("POST", "/relationships", {"product_a": "V001", "product_b": "V002", "weight": 0.8}, 201, "V001-V002")
    test_endpoint("POST", "/relationships", {"product_a": "V001", "product_b": "V003", "weight": 0.6}, 201, "V001-V003")
    test_endpoint("POST", "/relationships", {"product_a": "V002", "product_b": "V004", "weight": 0.7}, 201, "V002-V004")

    tests_total += 1
    success, _, data = test_endpoint("GET", "/graph/info", None, 200,
                                     "Obtener datos del grafo para visualización")
    if success:
        tests_passed += 1
        assert "products" in data and "relationships" in data
        assert len(data["products"]) == 5
        assert len(data["relationships"]) == 3
        # Verify structure for visualization
        for p in data["products"]:
            assert "id" in p and "name" in p
        for r in data["relationships"]:
            assert "product_a" in r and "product_b" in r and "weight" in r

    tests_total += 1
    success, _, data = test_endpoint("GET", "/explore/reachability/V001?depth=2", None, 200,
                                     "Datos de alcanzabilidad para resaltar nodos")
    if success:
        tests_passed += 1
        assert "reachable" in data
        reachable_ids = [r["product_id"] for r in data["reachable"]]
        assert "V002" in reachable_ids and "V003" in reachable_ids, "Direct neighbors should be reachable"
        assert "V004" in reachable_ids, "2-step neighbor should be reachable at depth 2"
        assert "V005" not in reachable_ids, "Isolated product should not be reachable"

        unreachable_ids = [u["product_id"] for u in data["unreachable"]]
        assert "V005" in unreachable_ids, "Isolated product should be unreachable"
        v005_reason = next(u["reason"] for u in data["unreachable"] if u["product_id"] == "V005")
        assert v005_reason == "otro_componente", "Isolated product should be 'otro_componente'"

    tests_total += 1
    success, _, data = test_endpoint("GET", "/explore/reachability/V001?depth=1", None, 200,
                                     "Alcanzabilidad con profundidad 1")
    if success:
        tests_passed += 1
        reachable_ids = [r["product_id"] for r in data["reachable"]]
        assert "V002" in reachable_ids and "V003" in reachable_ids
        assert "V004" not in reachable_ids, "V004 should not be reachable at depth 1"
        v004_reason = next(u["reason"] for u in data["unreachable"] if u["product_id"] == "V004")
        assert v004_reason == "fuera_del_alcance", "V004 should be 'fuera_del_alcance' at depth 1"

    # Test components endpoint structure for group visualization
    tests_total += 1
    success, _, data = test_endpoint("GET", "/components", None, 200,
                                     "Estructura de componentes para visualización de grupos")
    if success:
        tests_passed += 1
        assert "components" in data
        assert len(data["components"]) == 2  # One component with 4 products, one isolated
        for comp in data["components"]:
            for p in comp:
                assert "product_id" in p and "product_name" in p

    # ============================================================
    # SCENARIO 9: CAMBIO DE REQUISITO DOCENTE - Adaptación demostrada
    # ============================================================
    print("9. ESCENARIO: CAMBIO DE REQUISITO DOCENTE - Visualización integrada")
    clear_test_data()

    # The requirement change after F2 was to add graph visualization to explain queries
    # This test verifies the API provides all data needed for visualization

    products = [
        ("R001", "Producto A"), ("R002", "Producto B"), ("R003", "Producto C"),
        ("R004", "Producto D"),
    ]
    for pid, name in products:
        test_endpoint("POST", "/products", {"id": pid, "name": name}, 201, f"Crear {name}")

    test_endpoint("POST", "/relationships", {"product_a": "R001", "product_b": "R002", "weight": 0.9}, 201, "R001-R002")
    test_endpoint("POST", "/relationships", {"product_a": "R002", "product_b": "R003", "weight": 0.8}, 201, "R002-R003")

    # Verify all endpoints needed for visualization return correct data
    tests_total += 1
    success, _, graph_data = test_endpoint("GET", "/graph/info", None, 200,
                                           "Graph info para visualización completa")
    if success:
        tests_passed += 1
        assert len(graph_data["products"]) == 4
        assert len(graph_data["relationships"]) == 2

    tests_total += 1
    success, _, reach_data = test_endpoint("GET", "/explore/reachability/R001?depth=2", None, 200,
                                           "Reachability para resaltar nodos alcanzables")
    if success:
        tests_passed += 1
        assert reach_data["start_product_id"] == "R001"
        assert reach_data["reachable_count"] == 2  # R002, R003

    tests_total += 1
    success, _, comp_data = test_endpoint("GET", "/components", None, 200,
                                          "Componentes para visualización de grupos")
    if success:
        tests_passed += 1
        assert comp_data["components_count"] == 2
        # Verify one component has 3 products, one has 1
        sizes = sorted([len(c) for c in comp_data["components"]])
        assert sizes == [1, 3]

    # Verify recommendations include visualization-relevant data
    tests_total += 1
    success, _, rec_data = test_endpoint("GET", "/recommendations/R001", None, 200,
                                         "Recomendaciones con datos para visualización")
    if success:
        tests_passed += 1
        assert "proposals" in rec_data
        assert "direct_connections" in rec_data
        assert "excluded" in rec_data
        # Each proposal has path info for visualization
        for p in rec_data["proposals"]:
            assert "path" in p and "path_names" in p and "path_weights" in p

    # ============================================================
    # RESUMEN
    # ============================================================
    print("=" * 70)
    print(f"RESUMEN EDGE: {tests_passed}/{tests_total} pruebas pasaron")

    if tests_passed == tests_total:
        print("🎉 Todas las pruebas EDGE de Feature 4 pasaron!")
        return 0
    else:
        print(f"❌ {tests_total - tests_passed} pruebas fallaron")
        return 1


if __name__ == "__main__":
    sys.exit(main())