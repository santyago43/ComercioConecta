#!/usr/bin/env python3
"""
Acceptance test for ComercioConecta Feature 2: Exploracion de relaciones.
Valida: BFS/DFS con path y nivel_relacion, reachability, componentes, edge cases.
"""
import requests, json, sys, time

BASE_URL = "http://127.0.0.1:5000"
tests_passed = tests_total = 0

def test_endpoint(method, endpoint, data=None, expected_status=200, desc=""):
    global tests_passed, tests_total
    tests_total += 1
    try:
        response = requests.request(method, f"{BASE_URL}{endpoint}", json=data)
    except Exception as e:
        print(f"  [ERR] FAIL | {desc} | Error: {e}")
        return False, None

    ok = response.status_code == expected_status
    print(f"  [{'PASS' if ok else 'FAIL'}] | {desc}")
    print(f"      {method} {endpoint} -> Expected {expected_status}, got {response.status_code}")

    if not ok:
        try: print(f"      Error: {json.dumps(response.json(), indent=2)[:300]}")
        except: print(f"      Response: {response.text[:300]}")
    elif response.content:
        try:
            s = json.dumps(response.json(), indent=2)
            print(f"      Response: {s[:300]}{'...' if len(s)>300 else ''}")
        except: print(f"      Response: {response.text[:300]}")
    print()
    if ok: tests_passed += 1
    return ok, response

def delete_all():
    for p in requests.get(f"{BASE_URL}/products").json().get("products", []):
        requests.delete(f"{BASE_URL}/products/{p['id']}")

def seed():
    products = [("P001","Leche"),("P002","Pan"),("P003","Huevos"),("P004","Mantequilla"),
                ("P005","Café"),("P006","Azúcar"),("P007","Aceite"),("P008","Arroz"),
                ("P009","Sal")]
    rels = [("P001","P002",.85),("P001","P003",.70),("P002","P004",.90),("P003","P004",.65),
            ("P005","P006",.80),("P007","P008",.75),("P001","P005",.40),("P002","P003",.55)]
    for pid,name in products: requests.post(f"{BASE_URL}/products", json={"id":pid,"name":name})
    for a,b,w in rels: requests.post(f"{BASE_URL}/relationships", json={"product_a":a,"product_b":b,"weight":w})

def check(cond, msg_ok, msg_err):
    global tests_passed, tests_total
    tests_total += 1
    if cond: print(f"      [OK] {msg_ok}"); tests_passed += 1
    else: print(f"      [ERR] {msg_err}")

def run_scenario(num, title, fn):
    print(f"{num}. {title}"); print("-"*70)
    fn(); print()

def main():
    global tests_passed, tests_total
    print("="*70); print("Pruebas de aceptacion - ComercioConecta Feature 2"); print("="*70)
    print("API en http://127.0.0.1:5000\n"); time.sleep(1)

    # 1. Normal: BFS/DFS con conexiones
    def s1():
        delete_all(); seed()
        ok, r = test_endpoint("GET","/explore/bfs/P001?depth=2",None,200,"BFS Leche depth 2")
        if ok:
            d=r.json(); ids={x["product_id"] for x in d.get("results",[])}
            check({"P002","P003","P004","P005"}.issubset(ids), "Alcanzables esperados presentes",
                  f"Esperados P002-5, got {ids}")
            check(all("nivel_relacion" in x for x in d.get("results",[])), "Todos tienen nivel_relacion",
                  "Falta nivel_relacion")
            check(all("path" in x for x in d.get("results",[])), "Todos tienen path", "Falta path")
        ok, r = test_endpoint("GET","/explore/dfs/P001?depth=2",None,200,"DFS Leche depth 2")
        if ok: check(all("path" in x for x in r.json().get("results",[])), "DFS tiene path", "DFS sin path")
    run_scenario(1, "ESCENARIO NORMAL: BFS/DFS con conexiones", s1)

    # 2. Grafo vacío
    def s2():
        delete_all()
        test_endpoint("GET","/explore/bfs/P001?depth=2",None,404,"BFS inexistente en vacío")
        test_endpoint("GET","/explore/reachability/P001?depth=2",None,404,"Reach inexistente en vacío")
        ok,r = test_endpoint("GET","/components",None,200,"Componentes en vacío")
        if ok: check(r.json().get("components_count")==0, "0 componentes en vacío", f"Got {r.json().get('components_count')}")
    run_scenario(2, "ESCENARIO: Grafo vacío", s2)

    # 3. Producto inexistente
    def s3():
        seed()
        for ep in ["/explore/bfs/P999?depth=2","/explore/dfs/P999?depth=2","/explore/reachability/P999?depth=2"]:
            test_endpoint("GET",ep,None,404,f"{ep.split('/')[2]} P999 -> 404")
    run_scenario(3, "ESCENARIO: Producto inexistente", s3)

    # 4. Producto aislado
    def s4():
        ok,r = test_endpoint("GET","/explore/bfs/P009?depth=2",None,200,"BFS aislado P009")
        if ok: check(r.json().get("results_count")==0, "Aislado retorna 0", f"Got {r.json().get('results_count')}")
    run_scenario(4, "ESCENARIO: Producto aislado", s4)

    # 5. Profundidad insuficiente
    def s5():
        ok,r = test_endpoint("GET","/explore/bfs/P009?depth=2",None,200,"BFS aislado no alcanza otros")
        if ok: check(r.json().get("results_count")==0, "0 desde aislado", f"Got {r.json().get('results_count')}")
        ok,r = test_endpoint("GET","/explore/bfs/P001?depth=1",None,200,"BFS depth 1 no alcanza P004")
        if ok: check("P004" not in {x["product_id"] for x in r.json().get("results",[])}, "P004 no a depth 1", "P004 presente a depth 1")
    run_scenario(5, "ESCENARIO: Profundidad insuficiente", s5)

    # 6. Datos inválidos
    def s6():
        for ep,desc in [("/explore/bfs/P001?depth=0","BFS depth 0"),
                        ("/explore/bfs/P001?depth=-1","BFS depth -1"),
                        ("/explore/dfs/P001?depth=0","DFS depth 0"),
                        ("/explore/reachability/P001?depth=-1","Reach depth -1")]:
            test_endpoint("GET",ep,None,400,desc)
    run_scenario(6, "ESCENARIO: Datos inválidos (depth)", s6)

    # 7. Componentes conexos
    def s7():
        ok,r = test_endpoint("GET","/components",None,200,"Listar componentes")
        if ok:
            d=r.json(); c=d.get("components_count",-1)
            check(c>=2, f"{c} componentes (>=2)", f"Esperaba >=2, got {c}")
            comps=d.get("components",[])
            check(any(len(c)==1 and c[0]["product_id"]=="P009" for c in comps), "P009 en componente propio", "P009 no aislado")
    run_scenario(7, "ESCENARIO: Componentes conexos", s7)

    # 8. Reachability
    def s8():
        ok,r = test_endpoint("GET","/explore/reachability/P001?depth=2",None,200,"Reachability P001 depth 2")
        if ok:
            d=r.json(); reach=d.get("reachable",[]); unreach=d.get("unreachable",[])
            r_ids={x["product_id"] for x in reach}; u_ids={x["product_id"] for x in unreach}
            check({"P002","P003","P004","P005"}.issubset(r_ids), "Alcanzables correctos", f"Got {r_ids}")
            check({"P007","P008","P009"}.issubset(u_ids), "No alcanzables correctos", f"Got {u_ids}")
            check(all("reason" in x for x in unreach), "Todos no alcanzables tienen reason", "Falta reason")
            check(d.get("reachable_count")==len(reach) and d.get("unreachable_count")==len(unreach),
                  "Conteos consistentes", "Conteos inconsistentes")
    run_scenario(8, "ESCENARIO: Reachability", s8)

    # Resumen
    print("="*70); print(f"RESUMEN: {tests_passed}/{tests_total} pruebas pasaron")
    if tests_passed==tests_total: print("[OK] Todas las pruebas de Feature 2 pasaron!"); return 0
    print(f"[ERR] {tests_total-tests_passed} fallaron"); return 1

if __name__=="__main__": sys.exit(main())