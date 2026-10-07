#!/usr/bin/env python3
"""
Test script for BFS/DFS exploration features
Run the API first: python api.py
Then run this script: python test_exploration.py
"""

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:5000"

def test_endpoint(method, endpoint, data=None, expected_status=200):
    """Test an endpoint and return success/failure"""
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
            return False

        if response.status_code == expected_status:
            print(f"✓ {method} {endpoint} - Status {response.status_code}")
            try:
                print(f"  Response: {json.dumps(response.json(), indent=2)[:200]}...")
            except:
                print(f"  Response: {response.text[:200]}...")
            return True
        else:
            print(f"✗ {method} {endpoint} - Expected {expected_status}, got {response.status_code}")
            try:
                print(f"  Response: {json.dumps(response.json(), indent=2)[:200]}...")
            except:
                print(f"  Response: {response.text[:200]}...")
            return False

    except requests.exceptions.ConnectionError:
        print(f"✗ {method} {endpoint} - Connection error. Is the API running?")
        return False
    except Exception as e:
        print(f"✗ {method} {endpoint} - Error: {e}")
        return False

def main():
    print("Testing ComercioConecta Exploration Features")
    print("=" * 50)

    # Clear any existing data by adding and removing (fresh start)
    print("\n1. Setting up test data...")

    # Add products
    test_endpoint("POST", "/products", {"id": "P001", "name": "Aceite"}, 201)
    test_endpoint("POST", "/products", {"id": "P002", "name": "Arroz"}, 201)
    test_endpoint("POST", "/products", {"id": "P003", "name": "Fideos"}, 201)
    test_endpoint("POST", "/products", {"id": "P004", "name": "Leche"}, 201)
    test_endpoint("POST", "/products", {"id": "P005", "name": "Huevos"}, 201)
    test_endpoint("POST", "/products", {"id": "P006", "name": "Pan"}, 201)

    # Add relationships
    test_endpoint("POST", "/relationships", {"product_a": "P001", "product_b": "P002", "weight": 0.8}, 201)  # Aceite-Arroz
    test_endpoint("POST", "/relationships", {"product_a": "P002", "product_b": "P003", "weight": 0.6}, 201)  # Arroz-Fideos
    test_endpoint("POST", "/relationships", {"product_a": "P001", "product_b": "P004", "weight": 0.3}, 201)  # Aceite-Leche
    test_endpoint("POST", "/relationships", {"product_a": "P004", "product_b": "P005", "weight": 0.7}, 201)  # Leche-Huevos
    test_endpoint("POST", "/relationships", {"product_a": "P005", "product_b": "P006", "weight": 0.5}, 201)  # Huevos-Pan
    # P006 (Pan) is isolated from the main group except through Huevos

    # Test 2: Get graph info
    print("\n2. Getting graph info...")
    test_endpoint("GET", "/graph/info")

    # Test 3: BFS exploration from P001 (Aceite) with default depth (2)
    print("\n3. BFS from P001 (Aceite) - depth 2...")
    test_endpoint("GET", "/explore/bfs/P001")

    # Test 4: BFS exploration from P001 with depth 1
    print("\n4. BFS from P001 (Aceite) - depth 1...")
    test_endpoint("GET", "/explore/bfs/P001?depth=1")

    # Test 5: BFS exploration from P001 with depth 3
    print("\n5. BFS from P001 (Aceite) - depth 3...")
    test_endpoint("GET", "/explore/bfs/P001?depth=3")

    # Test 6: DFS exploration from P001 (Aceite) with default depth (2)
    print("\n6. DFS from P001 (Aceite) - depth 2...")
    test_endpoint("GET", "/explore/dfs/P001")

    # Test 7: DFS exploration from P001 with depth 1
    print("\n7. DFS from P001 (Aceite) - depth 1...")
    test_endpoint("GET", "/explore/dfs/P001?depth=1")

    # Test 8: BFS from isolated product P006 (Pan)
    print("\n8. BFS from P006 (Pan) - should only reach Huevos...")
    test_endpoint("GET", "/explore/bfs/P006?depth=2")

    # Test 9: BFS from non-existent product
    print("\n9. BFS from non-existent product...")
    test_endpoint("GET", "/explore/bfs/P999", 404)

    # Test 10: Invalid depth
    print("\n10. Testing invalid depth...")
    test_endpoint("GET", "/explore/bfs/P001?depth=0", 400)
    test_endpoint("GET", "/explore/bfs/P001?depth=-1", 400)

    # Test 11: Connected components
    print("\n11. Getting connected components...")
    test_endpoint("GET", "/components")

    # Test 12: Add an isolated product and check components
    print("\n12. Adding isolated product and checking components...")
    test_endpoint("POST", "/products", {"id": "P007", "name": "Azúcar"}, 201)
    test_endpoint("GET", "/components")

    print("\n" + "=" * 50)
    print("Testing completed!")

if __name__ == "__main__":
    main()