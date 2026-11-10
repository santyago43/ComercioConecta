#!/usr/bin/env python3
"""
Pruebas unitarias de la regla de propuesta (no requieren la API).
Ejecutar: python -m unittest test_recommendation -v
"""
import unittest

from graph import CommercialGraph
from models import Product, Relationship
from recommendation import RecommendationRule, recommend


def build_graph(products, relationships):
    graph = CommercialGraph()
    for product_id in products:
        graph.add_product(Product(product_id, product_id))
    for id_a, id_b, weight in relationships:
        graph.add_relationship(Relationship(graph.get_product(id_a), graph.get_product(id_b), weight))
    return graph


def proposal_ids(result):
    return [p["product_id"] for p in result["proposals"]]


def excluded_codes(result):
    return {e["product_id"]: e["reason_code"] for e in result["excluded"]}


class RecommendationRuleTest(unittest.TestCase):
    def test_directas_van_antes_que_indirectas_mas_fuertes(self):
        graph = build_graph("ABC", [("A", "B", 0.40), ("B", "C", 1.0)])
        graph.add_product(Product("D", "D"))
        graph.add_relationship(Relationship(graph.get_product("A"), graph.get_product("D"), 0.90))
        graph.add_relationship(Relationship(graph.get_product("D"), graph.get_product("C"), 0.95))

        result = recommend(graph, "A")

        self.assertEqual(proposal_ids(result), ["D", "B", "C"])
        self.assertEqual(result["proposals"][2]["type"], "indirecta")

    def test_resultado_no_depende_del_orden_de_carga(self):
        relationships = [("L", "P", 0.85), ("L", "H", 0.70), ("P", "M", 0.90), ("H", "M", 0.65)]
        results = [
            recommend(build_graph("LPHM", order), "L")
            for order in (relationships, list(reversed(relationships)))
        ]

        self.assertEqual(results[0]["proposals"], results[1]["proposals"])
        indirect = results[0]["proposals"][-1]
        self.assertEqual(indirect["strength"], 0.765)
        self.assertEqual(indirect["path"], ["L", "P", "M"])
        self.assertIn("También conecta vía H", indirect["reason"])

    def test_umbrales_incluyen_el_valor_exacto(self):
        graph = build_graph("ABCD", [("A", "B", 0.30), ("A", "C", 0.29), ("C", "D", 1.0)])
        self.assertEqual(proposal_ids(recommend(graph, "A")), ["B"])

        graph = build_graph("ABC", [("A", "B", 0.5), ("B", "C", 1.0)])
        self.assertEqual(proposal_ids(recommend(graph, "A")), ["B", "C"])

    def test_directa_debil_no_reaparece_como_indirecta(self):
        graph = build_graph("ABC", [("A", "B", 0.90), ("B", "C", 0.90), ("A", "C", 0.10)])

        result = recommend(graph, "A")

        self.assertEqual(proposal_ids(result), ["B"])
        self.assertEqual(excluded_codes(result)["C"], "directa_debil")

    def test_nunca_propone_el_origen(self):
        graph = build_graph("ABC", [("A", "B", 0.9), ("B", "C", 0.9), ("A", "C", 0.9)])
        self.assertNotIn("A", proposal_ids(recommend(graph, "A")))

    def test_mas_de_dos_pasos_queda_fuera_de_alcance(self):
        graph = build_graph("ABCD", [("A", "B", 1.0), ("B", "C", 1.0), ("C", "D", 1.0)])

        result = recommend(graph, "A")

        self.assertEqual(proposal_ids(result), ["B", "C"])
        self.assertEqual(excluded_codes(result)["D"], "fuera_del_alcance")

    def test_otro_grupo_no_se_propone(self):
        graph = build_graph("ABCD", [("A", "B", 0.8), ("C", "D", 0.8)])

        result = recommend(graph, "A")

        self.assertEqual(proposal_ids(result), ["B"])
        self.assertEqual(excluded_codes(result)["C"], "otro_componente")

    def test_limite_descarta_con_razon(self):
        neighbors = "BCD"
        graph = build_graph("ABCD", [("A", n, 0.9) for n in neighbors])

        result = recommend(graph, "A", RecommendationRule(limit=2))

        self.assertEqual(result["proposals_count"], 2)
        self.assertEqual(excluded_codes(result)["D"], "fuera_del_limite")

    def test_aislado_no_inventa_recomendaciones(self):
        result = recommend(build_graph("AB", []), "A")

        self.assertEqual(result["proposals"], [])
        self.assertEqual(result["direct_connections"], [])
        self.assertIn("no tiene relaciones", result["message"])

    def test_inexistente_lanza_error(self):
        with self.assertRaises(ValueError):
            recommend(build_graph("A", []), "Z")

    def test_todas_las_propuestas_tienen_razon(self):
        graph = build_graph("ABC", [("A", "B", 0.9), ("B", "C", 0.9)])
        self.assertTrue(all(p["reason"] for p in recommend(graph, "A")["proposals"]))


if __name__ == "__main__":
    unittest.main()
