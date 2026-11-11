"""
Propuesta comercial justificable (Feature 3).

Regla:
1. Solo se consideran productos a un máximo de 2 pasos del origen.
2. Primero las relaciones directas (co-compra registrada) y luego las
   indirectas (inferidas por un intermediario), cada grupo por fuerza.
3. Fuerza mínima distinta por tipo: lo inferido debe ser más fuerte.
4. Nunca se propone el origen ni productos sin camino demostrable.
5. Cada producto propuesto o descartado lleva su razón.
"""
from dataclasses import asdict, dataclass

from graph import CommercialGraph
from models import Product

MAX_STEPS = 2
DIRECT = "directa"
INDIRECT = "indirecta"

REACHABILITY_REASONS = {
    "fuera_del_alcance": f"Está en el mismo grupo, pero a más de {MAX_STEPS} pasos.",
    "otro_componente": "Pertenece a otro grupo: no hay relación demostrable.",
}


@dataclass(frozen=True)
class RecommendationRule:
    min_direct: float = 0.30
    min_indirect: float = 0.50
    limit: int = 5


@dataclass(frozen=True)
class Candidate:
    product: Product
    kind: str
    strength: float
    path: tuple[Product, ...]
    path_weights: tuple[float, ...]
    reason: str


def _pct(value: float) -> str:
    """Formatea 0.765 como 76.5% y 0.85 como 85%."""
    return f"{value * 100:.1f}".rstrip("0").rstrip(".") + "%"


def _direct_candidates(graph: CommercialGraph, origin: Product) -> list[Candidate]:
    candidates = [
        Candidate(
            product=neighbor,
            kind=DIRECT,
            strength=weight,
            path=(origin, neighbor),
            path_weights=(weight,),
            reason=f"Relación directa: se compra junto con {origin.name} (fuerza {_pct(weight)}).",
        )
        for neighbor, weight in graph.graph[origin].items()
    ]
    return sorted(candidates, key=lambda c: (-c.strength, c.product.product_id))


def _indirect_candidates(graph: CommercialGraph, origin: Product) -> list[Candidate]:
    """Revisa todos los caminos de 2 pasos para que el resultado no dependa del orden de carga."""
    direct = graph.graph[origin]
    routes: dict[Product, list[tuple[float, Product]]] = {}

    for via, first_weight in direct.items():
        for target, second_weight in graph.graph[via].items():
            # Si ya hay relación directa, esa evidencia prevalece sobre la inferida
            if target != origin and target not in direct:
                routes.setdefault(target, []).append((round(first_weight * second_weight, 4), via))

    candidates = []
    for target, options in routes.items():
        options.sort(key=lambda option: (-option[0], option[1].product_id))
        strength, via = options[0]
        reason = (
            f"Relación indirecta vía {via.name}: "
            f"{origin.name}–{via.name} {_pct(direct[via])} × "
            f"{via.name}–{target.name} {_pct(graph.graph[via][target])} = {_pct(strength)}."
        )
        if len(options) > 1:
            others = ", ".join(f"{v.name} ({_pct(s)})" for s, v in options[1:])
            reason += f" También conecta vía {others}."
        weights = (direct[via], graph.graph[via][target])
        candidates.append(Candidate(target, INDIRECT, strength, (origin, via, target), weights, reason))

    return sorted(candidates, key=lambda c: (-c.strength, c.product.product_id))


def _excluded(product: Product, code: str, reason: str) -> dict:
    return {
        "product_id": product.product_id,
        "product_name": product.name,
        "reason_code": code,
        "reason": reason,
    }


def _weak_reason(candidate: Candidate, minimum: float) -> str:
    return f"{candidate.reason} No alcanza el mínimo de {_pct(minimum)} para relación {candidate.kind}."


def _proposal(rank: int, candidate: Candidate) -> dict:
    return {
        "rank": rank,
        "product_id": candidate.product.product_id,
        "product_name": candidate.product.name,
        "type": candidate.kind,
        "strength": candidate.strength,
        "path": [p.product_id for p in candidate.path],
        "path_names": [p.name for p in candidate.path],
        "path_weights": list(candidate.path_weights),
        "reason": candidate.reason,
    }


def _message(origin: Product, direct: list[Candidate], proposals: list[dict]) -> str:
    if proposals:
        return f"{len(proposals)} producto(s) propuesto(s) para {origin.name}."
    if not direct:
        return f"{origin.name} no tiene relaciones registradas: no se genera propuesta para no inventar recomendaciones."
    return f"{origin.name} tiene relaciones, pero ninguna alcanza la fuerza mínima: no se genera propuesta."


def _rule_summary(rule: RecommendationRule) -> dict:
    return {
        **asdict(rule),
        "max_steps": MAX_STEPS,
        "description": (
            f"Hasta {MAX_STEPS} pasos. Primero directas (mínimo {_pct(rule.min_direct)}) y luego "
            f"indirectas (mínimo {_pct(rule.min_indirect)}), por fuerza. Máximo {rule.limit} productos."
        ),
    }


def _filter_by_strength(
    direct: list[Candidate], indirect: list[Candidate], rule: RecommendationRule
) -> tuple[list[Candidate], list[dict]]:
    """Separa los candidatos que alcanzan su fuerza mínima (directas primero) de los descartados."""
    accepted, excluded = [], []
    for candidates, minimum, code in (
        (direct, rule.min_direct, "directa_debil"),
        (indirect, rule.min_indirect, "indirecta_debil"),
    ):
        for candidate in candidates:
            if candidate.strength >= minimum:
                accepted.append(candidate)
            else:
                excluded.append(_excluded(candidate.product, code, _weak_reason(candidate, minimum)))
    return accepted, excluded


def _over_limit_exclusions(accepted: list[Candidate], rule: RecommendationRule) -> list[dict]:
    """Los aceptados que no caben en el máximo de productos."""
    return [
        _excluded(
            candidate.product,
            "fuera_del_limite",
            f"{candidate.reason} Quedó por fuera del máximo de {rule.limit} productos.",
        )
        for candidate in accepted[rule.limit:]
    ]


def _unreachable_exclusions(graph: CommercialGraph, product_id: str) -> list[dict]:
    """Reutiliza la alcanzabilidad de Feature 2 para explicar lo que no tiene camino corto."""
    return [
        {
            "product_id": item["product_id"],
            "product_name": item["product_name"],
            "reason_code": item["reason"],
            "reason": REACHABILITY_REASONS[item["reason"]],
        }
        for item in graph.get_reachability_summary(product_id, MAX_STEPS)["unreachable"]
    ]


def recommend(
    graph: CommercialGraph,
    product_id: str,
    rule: RecommendationRule = RecommendationRule(),
) -> dict:
    """Devuelve conexiones directas, propuesta y descartados de un producto."""
    origin = graph.get_product(product_id)
    if origin is None:
        raise ValueError(f"Product {product_id} does not exist")

    direct = _direct_candidates(graph, origin)
    indirect = _indirect_candidates(graph, origin)

    accepted, excluded = _filter_by_strength(direct, indirect, rule)
    excluded += _over_limit_exclusions(accepted, rule)
    excluded += _unreachable_exclusions(graph, product_id)

    proposals = [_proposal(rank, c) for rank, c in enumerate(accepted[:rule.limit], start=1)]

    return {
        "product_id": origin.product_id,
        "product_name": origin.name,
        "rule": _rule_summary(rule),
        "direct_connections": [
            {"product_id": c.product.product_id, "product_name": c.product.name, "weight": c.strength}
            for c in direct
        ],
        "proposals_count": len(proposals),
        "proposals": proposals,
        "excluded": excluded,
        "message": _message(origin, direct, proposals),
    }
