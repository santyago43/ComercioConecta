#!/usr/bin/env python3
"""
Acceptance test for ComercioConecta Feature 4: Panel comercial demostrable (Core Scenarios)

Validates integration of Features 1-3:
- Product/relationship management (F1)
- Graph exploration BFS/DFS/reachability/components (F2)
- Explainable recommendations (F3)

Core scenarios: normal, isolated product, non-existent, empty graph, invalid data
"""

import requests
import json
import sys
import time

BASE_URL = "http://127.0.0.1:5000"


def test_endpoint(method, endpoint, data=None, expected_status=200, description=""):
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        else:
            return False, f"Unsupported method: {method}", None

        success = response.status_code == expected_status
        status_msg = "✓ PASS" if success else "✗ FAIL"
        print(f"{status_msg} {description}")
        print(f"    {method} {endpoint} - Expected {expected_status}, got {response.status_code}")

        if not success:
            try:
                print(f"    Error: {json.dumps(response.json(), indent=2)}")
            except:
                print(f"    Response: {response.text[:200]}")
        elif response.content:
            try:
                r = json.dumps(response.json(), indent=2)
                print(f"    Response: {r[:300]}..." if len(r) > 300 else f"    Response: {r}")
            except:
                print(f"    Response: {response.text[:300]}")
        print()
        return success, response.status_code, response.json() if success and response.content else None
    except requests.exceptions.ConnectionError:
        print(f"✗ FAIL {description}\n    Connection error. Is API running?\n")
        return False, None, None
    except Exception as e:
        print(f"✗ FAIL {description}\n    Error: {e}\n")
        return False, None, None


def clear_data():
    try:
        r = requests.get(f"{BASE_URL}/products")
        if r.status_code == 200:
            for p in r.json().get("products", []):
                requests.delete(f"{BASE_URL}/products/{p['id']}")
    except:
        pass


def setup_normal():
    clear_data()
    for pid, name in [("P001","Leche"),("P002","Pan"),("P003","Huevos"),("P004","Mantequilla"),
                      ("P005","Café"),("P006","Azúcar"),("P007","Aceite"),("P008","Arroz"),("P009","Sal")]:
        test_endpoint("POST","/products",{"id":pid,"name":name},201,f"Crear {name}")
    for a,b,w in [("P001","P002",0.85),("P001","P003",0.70),("P002","P004",0.90),("P003","P004",0.65),
                   ("P005","P006",0.80),("P007","P008",0.75),("P001","P005",0.40)]:
        test_endpoint("POST","/relationships",{"product_a":a,"product_b":b,"weight":w},201,f"Rel {a}-{b}")


def setup_isolated():
    clear_data()
    test_endpoint("POST","/products",{"id":"ISO001","name":"Aislado"},201,"Crear aislado")


def main():
    print("Feature 4 Acceptance - CORE Scenarios")
    print("=" * 60)
    print("API must be running at http://127.0.0.1:5000\n")
    passed = total = 0
    time.sleep(1)

    # 1. NORMAL
    print("1. NORMAL: Full workflow")
    setup_normal()
    for ep, desc in [("/products","List products"),("/relationships","List rels"),("/graph/info","Graph info")]:
        total+=1; s,_,d=test_endpoint("GET",ep,None,200,desc)
        if s: passed+=1
    for ep, desc in [("/explore/bfs/P001?depth=2","BFS Leche"),("/explore/dfs/P001?depth=2","DFS Leche"),
                     ("/explore/reachability/P001?depth=2","Reach Leche"),("/components","Components")]:
        total+=1; s,_,d=test_endpoint("GET",ep,None,200,desc)
        if s: passed+=1
    for pid, desc in [("P001","Recs Leche"),("P002","Recs Pan")]:
        total+=1; s,_,d=test_endpoint("GET",f"/recommendations/{pid}",None,200,desc)
        if s and all(k in d for k in ("proposals","direct_connections","excluded","rule","message")): passed+=1

    # 2. ISOLATED
    print("2. ISOLATED PRODUCT")
    setup_isolated()
    for ep, desc in [("/explore/bfs/ISO001?depth=2","BFS isolated"),("/explore/dfs/ISO001?depth=2","DFS isolated"),
                     ("/explore/reachability/ISO001?depth=2","Reach isolated"),("/recommendations/ISO001","Recs isolated"),
                     ("/components","Components isolated")]:
        total+=1; s,_,d=test_endpoint("GET",ep,None,200,desc)
        if s: passed+=1

    # 3. NON-EXISTENT
    print("3. NON-EXISTENT PRODUCT")
    setup_normal()
    for ep, desc in [("/products/P999","Get missing"),("/explore/bfs/P999?depth=2","BFS missing"),
                     ("/explore/dfs/P999?depth=2","DFS missing"),("/explore/reachability/P999?depth=2","Reach missing"),
                     ("/recommendations/P999","Recs missing"),("/relationships","Rel with missing (POST)")]:
        exp = 404 if "POST" not in desc else 404
        total+=1; s,_=test_endpoint("POST" if "POST" in desc else "GET",ep,
            {"product_a":"P001","product_b":"P999","weight":0.5} if "POST" in desc else None,exp,desc)[:2]
        if s: passed+=1

    # 4. EMPTY GRAPH
    print("4. EMPTY GRAPH")
    clear_data()
    for ep, desc in [("/products","List empty"),("/relationships","Rels empty"),("/graph/info","Graph empty"),
                     ("/components","Comps empty"),("/recommendations/P001","Recs empty (404)")]:
        total+=1; s,_,d=test_endpoint("GET",ep,None,200 if "404" not in desc else 404,desc)
        if s: passed+=1
    total+=1; s,_=test_endpoint("POST","/products",{"id":"P001","name":"Solo"},201,"Create solo")[:2]
    if s: passed+=1
    total+=1; s,_,d=test_endpoint("GET","/recommendations/P001",None,200,"Recs solo")
    if s and d["proposals_count"]==0: passed+=1

    # 5. INVALID DATA
    print("5. INVALID DATA")
    setup_normal()
    invalid_cases = [
        ("POST","/products",{"id":"P001","name":"Dup"},409,"Duplicate ID"),
        ("POST","/relationships",{"product_a":"P001","product_b":"P002","weight":0.9},400,"Duplicate rel"),
        ("POST","/relationships",{"product_a":"P001","product_b":"P001","weight":0.5},400,"Self-rel"),
        ("POST","/relationships",{"product_a":"P001","product_b":"P003","weight":0},400,"Weight 0"),
        ("POST","/relationships",{"product_a":"P001","product_b":"P003","weight":1.5},400,"Weight >1"),
        ("POST","/relationships",{"product_a":"P001","product_b":"P003","weight":-0.1},400,"Weight neg"),
        ("POST","/relationships",{"product_a":"P001","product_b":"P003","weight":"x"},400,"Weight text"),
        ("POST","/products",{"id":"P999"},400,"Missing name"),
        ("POST","/products",{"name":"Solo Nombre"},400,"Missing ID"),
        ("POST","/relationships",{"product_a":"P001"},400,"Missing fields"),
        ("GET","/explore/bfs/P001?depth=0",None,400,"Depth 0"),
        ("GET","/explore/bfs/P001?depth=-1",None,400,"Depth neg"),
    ]
    for m,ep,d,exp,desc in invalid_cases:
        total+=1; s,_=test_endpoint(m,ep,d,exp,desc)[:2]
        if s: passed+=1

    print("=" * 60)
    print(f"CORE: {passed}/{total} passed")
    return 0 if passed==total else 1


if __name__ == "__main__":
    sys.exit(main())