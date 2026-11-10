"""
Pruebas del selector de producto: agrupación, búsqueda y conteo (no requieren la API).
Ejecutar: python -m unittest test_product_picker -v
"""
import unittest

from frontend.components.product_picker import group_products, relation_counts, relation_note


def member(product_id, name):
    return {"product_id": product_id, "product_name": name}


COMPONENTS = [
    [member("P007", "Aceite"), member("P008", "Arroz")],
    [member("P009", "Sal")],
    [member("P001", "Leche"), member("P002", "Pan"), member("P003", "Huevos")],
]
RELATIONSHIPS = [
    {"product_a": "P001", "product_b": "P002"},
    {"product_a": "P001", "product_b": "P003"},
    {"product_a": "P007", "product_b": "P008"},
]


class ProductPickerTest(unittest.TestCase):
    def test_cuenta_relaciones_por_producto(self):
        counts = relation_counts(RELATIONSHIPS)
        self.assertEqual(counts["P001"], 2)
        self.assertEqual(counts["P002"], 1)
        self.assertNotIn("P009", counts)

    def test_textos_de_relaciones(self):
        self.assertEqual(relation_note(0), "sin relaciones")
        self.assertEqual(relation_note(1), "1 relación")
        self.assertEqual(relation_note(3), "3 relaciones")

    def test_grupos_se_numeran_de_mayor_a_menor_como_en_la_pantalla_de_grupos(self):
        titles = [title for title, _ in group_products(COMPONENTS, {})]
        self.assertEqual(titles, ["Grupo 1 · 3 productos", "Grupo 2 · 2 productos", "Grupo 3 · aislado"])

    def test_cada_producto_trae_sus_relaciones(self):
        groups = dict(group_products(COMPONENTS, relation_counts(RELATIONSHIPS)))
        leche = next(item for item in groups["Grupo 1 · 3 productos"] if item["name"] == "Leche")
        sal = groups["Grupo 3 · aislado"][0]
        self.assertEqual(leche["relations"], 2)
        self.assertEqual(sal["relations"], 0)

    def test_busqueda_filtra_sin_distinguir_mayusculas_y_oculta_grupos_vacios(self):
        groups = group_products(COMPONENTS, {}, query="  PA")
        self.assertEqual([title for title, _ in groups], ["Grupo 1 · 3 productos"])
        self.assertEqual([item["name"] for item in groups[0][1]], ["Pan"])

    def test_busqueda_sin_coincidencias_devuelve_lista_vacia(self):
        self.assertEqual(group_products(COMPONENTS, {}, query="zzz"), [])

    def test_sin_grupos_devuelve_lista_vacia(self):
        self.assertEqual(group_products([], {}), [])


if __name__ == "__main__":
    unittest.main()
