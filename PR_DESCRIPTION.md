# PR 3b: Feature 4 Acceptance Tests - Edge Cases & Visualization Integration

## Summary
Automated acceptance tests for edge cases and Feature 4 visualization integration requirements.

## Test File
- **acceptance_test_feature4_edge.py** (330 lines)

## Scenarios Tested

### 6. Disconnected Components (Separate Groups)
- Two completely separate components: A (3 products) and B (2 products)
- Verify `/components` returns 2 components
- Recommendations from Component A:
  - **Never** include products from Component B
  - Component B products appear in `excluded` with `reason_code: "otro_componente"`
  - Reason message: "Pertenece a otro grupo: no hay relación demostrable."

### 7. Recommendation Edge Cases
#### Strength Thresholds
- Direct: min 0.30 (weak direct = 0.2 → excluded as `directa_debil`)
- Indirect: min 0.50 (weak indirect = 0.15 → excluded as `indirecta_debil`)
- Strong indirect (0.9 × 0.8 = 0.72) → included
- Ordering: Direct first (by strength), then indirect (by strength)

#### Limit Enforcement (max 5 proposals)
- Create 6 direct relationships from one product
- Verify `proposals_count ≤ 5`
- Excess proposals appear in `excluded` with `reason_code: "fuera_del_limite"`

### 8. Graph Visualization Integration (Feature 4 Requirement)
Verifies API endpoints return visualization-ready data structures:

#### `GET /graph/info`
```json
{
  "products": [{"id": "...", "name": "..."}],
  "relationships": [{"product_a": "...", "product_b": "...", "weight": 0.8}]
}
```
- All products have `id` and `name`
- All relationships have `product_a`, `product_b`, `weight`

#### `GET /explore/reachability/<id>?depth=<n>`
```json
{
  "start_product_id": "...",
  "reachable": [{"product_id": "...", "product_name": "...", ...}],
  "unreachable": [{"product_id": "...", "reason": "otro_componente|fuera_del_alcance", ...}]
}
```
- Depth=2: Direct + 2-step neighbors reachable
- Depth=1: Only direct neighbors; 2-step marked `fuera_del_alcance`
- Isolated products marked `otro_componente`

#### `GET /components`
```json
{
  "components": [[{"product_id": "...", "product_name": "..."}, ...], ...]
}
```
- Each component is array of product objects
- Structure supports group visualization

### 9. Requirement Change Adaptation (Cambio de Requisito Docente)
The post-F2 requirement change: **"Add graph visualization to explain queries"**

This test demonstrates adaptation by verifying:
- All visualization data endpoints functional
- Reachability provides node highlighting data (reachable/unreachable classification)
- Components provides group visualization data
- Recommendations include `path`, `path_names`, `path_weights` for edge visualization
- Complete data pipeline: Graph → Reachability → Visualization → Frontend

## Running Tests
```bash
# Start API first
python api.py

# In another terminal
python acceptance_test_feature4_edge.py
```

## Expected Output
```
Feature 4 Acceptance - EDGE Scenarios
============================================================
6. DISCONNECTED COMPONENTS
✓ PASS Components with separate groups
✓ PASS Recommendations from component A exclude B
7. RECOMMENDATION EDGE CASES
✓ PASS Recommendations with varying strengths
✓ PASS Limit enforcement (max 5)
8. GRAPH VISUALIZATION INTEGRATION
✓ PASS Graph info for visualization
✓ PASS Reachability for node highlighting
✓ PASS Reachability depth=1 vs depth=2
✓ PASS Components structure for group viz
9. REQUIREMENT CHANGE ADAPTATION
✓ PASS Full visualization data pipeline
============================================================
EDGE: 12/12 passed
🎉 Todas las pruebas EDGE de Feature 4 pasaron!
```

## Test Count
- **Total**: ~12 test groups with multiple assertions each
- **Lines**: 330 (under 400 limit)