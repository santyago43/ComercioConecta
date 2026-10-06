#!/usr/bin/env python3
"""
Simple test script for the ComercioConecta API
Run the API first: python api.py
Then run this script: python test_api.py
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
                print(f"  Response: {json.dumps(response.json(), indent=2)}")
            except:
                print(f"  Response: {response.text}")
            return True
        else:
            print(f"✗ {method} {endpoint} - Expected {expected_status}, got {response.status_code}")
            try:
                print(f"  Response: {json.dumps(response.json(), indent=2)}")
            except:
                print(f"  Response: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"✗ {method} {endpoint} - Connection error. Is the API running?")
        return False
    except Exception as e:
        print(f"✗ {method} {endpoint} - Error: {e}")
        return False

def main():
    print("Testing ComercioConecta API")
    print("=" * 40)

    # Test 1: Get products (should be empty initially)
    print("\n1. Testing products endpoint...")
    test_endpoint("GET", "/products")

    # Test 2: Add a product
    print("\n2. Adding products...")
    test_endpoint("POST", "/products", {"id": "P001", "name": "Aceite"}, 201)
    test_endpoint("POST", "/products", {"id": "P002", "name": "Arroz"}, 201)
    test_endpoint("POST", "/products", {"id": "P003", "name": "Fideos"}, 201)

    # Test 3: Try to add duplicate product (should fail)
    print("\n3. Testing duplicate product...")
    test_endpoint("POST", "/products", {"id": "P001", "name": "Aceite duplicado"}, 409)

    # Test 4: Get specific product
    print("\n4. Getting specific product...")
    test_endpoint("GET", "/products/P001")
    test_endpoint("GET", "/products/P002")
    test_endpoint("GET", "/products/P999", 404)  # Non-existent

    # Test 5: Add relationships
    print("\n5. Adding relationships...")
    test_endpoint("POST", "/relationships", {"product_a": "P001", "product_b": "P002", "weight": 0.8}, 201)
    test_endpoint("POST", "/relationships", {"product_a": "P002", "product_b": "P003", "weight": 0.6}, 201)
    test_endpoint("POST", "/relationships", {"product_a": "P001", "product_b": "P003", "weight": 0.3}, 201)

    # Test 6: Try to add duplicate relationship (should fail)
    print("\n6. Testing duplicate relationship...")
    test_endpoint("POST", "/relationships", {"product_a": "P001", "product_b": "P002", "weight": 0.9}, 400)

    # Test 7: Get relationships
    print("\n7. Getting relationships...")
    test_endpoint("GET", "/relationships")

    # Test 8: Get graph info
    print("\n8. Getting graph info...")
    test_endpoint("GET", "/graph/info")

    # Test 9: Invalid relationship data
    print("\n9. Testing invalid relationship data...")
    test_endpoint("POST", "/relationships", {"product_a": "P001", "product_b": "P001", "weight": 0.5}, 400)  # Same product
    test_endpoint("POST", "/relationships", {"product_a": "P001", "product_b": "P004", "weight": 1.5}, 400)  # Weight > 1
    test_endpoint("POST", "/relationships", {"product_a": "P001", "product_b": "P004", "weight": -0.1}, 400)  # Weight < 0
    test_endpoint("POST", "/relationships", {"product_a": "P001", "product_b": "P004"}, 400)  # Missing weight

    # Test 10: Delete product
    print("\n10. Deleting product...")
    test_endpoint("DELETE", "/products/P003")
    test_endpoint("GET", "/products/P003", 404)  # Should be gone

    print("\n" + "=" * 40)
    print("Testing completed!")

if __name__ == "__main__":
    main()