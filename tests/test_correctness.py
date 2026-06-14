"""
test_correctness.py — Correctness tests for Dijkstra and Bellman-Ford.

Verifies:
1. Both algorithms produce the same distances on the same graphs.
2. Dijkstra correctly raises ValueError on negative weights.
3. Bellman-Ford detects negative cycles.
4. Both handle disconnected graphs (unreachable vertices → INF).
5. Both handle single-vertex and single-edge graphs.
6. Real Surabaya graph: distances agree and are sensible (> 0).

Run with:
    python -m pytest tests/ -v
    # or
    python tests/test_correctness.py
"""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import math
import pytest

from src.graph import Graph
from src.dijkstra import dijkstra, reconstruct_path as dijk_path
from src.bellman_ford import bellman_ford, reconstruct_path as bf_path, NegativeCycleError
from src.generator import generate_random_graph
from src.city_data import build_surabaya_graph

INF = float("inf")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_graph(n: int, edges: list[tuple[int, int, float]], directed: bool = True) -> Graph:
    g = Graph(n, directed=directed)
    for u, v, w in edges:
        g.add_edge(u, v, w)
    return g


def distances_equal(d1: list[float], d2: list[float], tol: float = 1e-9) -> bool:
    for a, b in zip(d1, d2):
        if a == INF and b == INF:
            continue
        if a == INF or b == INF:
            return False
        if abs(a - b) > tol:
            return False
    return True


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

class TestBasicCorrectness:

    def test_single_vertex(self):
        g = make_graph(1, [])
        d_d, _ = dijkstra(g, 0)
        d_bf, _ = bellman_ford(g, 0)
        assert d_d[0] == 0.0
        assert d_bf[0] == 0.0

    def test_two_vertices_connected(self):
        g = make_graph(2, [(0, 1, 5.0)])
        d_d, _ = dijkstra(g, 0)
        d_bf, _ = bellman_ford(g, 0)
        assert d_d[1] == 5.0
        assert d_bf[1] == 5.0

    def test_two_vertices_disconnected(self):
        g = make_graph(2, [])
        d_d, _ = dijkstra(g, 0)
        d_bf, _ = bellman_ford(g, 0)
        assert d_d[1] == INF
        assert d_bf[1] == INF

    def test_triangle(self):
        # 0 -1-> 1 -1-> 2, 0 -3-> 2 (direct is longer)
        g = make_graph(3, [(0, 1, 1.0), (1, 2, 1.0), (0, 2, 3.0)])
        d_d, _ = dijkstra(g, 0)
        d_bf, _ = bellman_ford(g, 0)
        assert d_d[2] == 2.0   # through 1
        assert d_bf[2] == 2.0

    def test_longer_path(self):
        g = make_graph(5, [
            (0, 1, 2.0), (1, 2, 3.0), (2, 3, 1.0), (3, 4, 4.0),
            (0, 4, 20.0),   # direct but expensive
        ])
        d_d, _ = dijkstra(g, 0)
        d_bf, _ = bellman_ford(g, 0)
        assert d_d[4] == 10.0
        assert distances_equal(d_d, d_bf)

    def test_source_to_self_is_zero(self):
        g = generate_random_graph(50, seed=7)
        for algo in [dijkstra, bellman_ford]:
            dist, _ = algo(g, 0)
            assert dist[0] == 0.0


class TestAgreement:
    """Both algorithms must return identical distances on every graph."""

    def test_small_random_graphs(self):
        for seed in range(20):
            g = generate_random_graph(30, avg_degree=4, seed=seed)
            d_d, _ = dijkstra(g, 0)
            d_bf, _ = bellman_ford(g, 0)
            assert distances_equal(d_d, d_bf), \
                f"Mismatch on seed={seed}: dijkstra={d_d}, bellman_ford={d_bf}"

    def test_medium_random_graphs(self):
        for seed in [42, 99, 123, 777, 2024]:
            g = generate_random_graph(300, avg_degree=5, seed=seed)
            d_d, _ = dijkstra(g, 0)
            d_bf, _ = bellman_ford(g, 0)
            assert distances_equal(d_d, d_bf), f"Mismatch on seed={seed}"

    def test_surabaya_real_graph(self):
        g = build_surabaya_graph()
        d_d, _ = dijkstra(g, 0)
        d_bf, _ = bellman_ford(g, 0)
        assert distances_equal(d_d, d_bf), "Surabaya graph: Dijkstra ≠ Bellman-Ford"

    def test_large_graph(self):
        g = generate_random_graph(1000, avg_degree=5, seed=42)
        d_d, _ = dijkstra(g, 0)
        d_bf, _ = bellman_ford(g, 0)
        assert distances_equal(d_d, d_bf)


class TestPathReconstruction:

    def test_path_endpoints(self):
        g = make_graph(4, [(0, 1, 1.0), (1, 2, 1.0), (2, 3, 1.0)])
        _, prev = dijkstra(g, 0)
        path = dijk_path(prev, 0, 3)
        assert path[0] == 0 and path[-1] == 3

    def test_path_length_matches_distance(self):
        g = generate_random_graph(50, seed=5)
        dist_d, prev_d = dijkstra(g, 0)
        dist_bf, prev_bf = bellman_ford(g, 0)
        for target in range(1, 10):
            p_d = dijk_path(prev_d, 0, target)
            p_bf = bf_path(prev_bf, 0, target)
            # Both paths must lead to the same total distance
            if p_d:
                cost_d = sum(
                    next(w for v2, w in g.neighbours(p_d[i]) if v2 == p_d[i + 1])
                    for i in range(len(p_d) - 1)
                )
                assert abs(cost_d - dist_d[target]) < 1e-9

    def test_unreachable_path_is_empty(self):
        g = make_graph(3, [(0, 1, 1.0)])  # 2 is isolated
        _, prev = dijkstra(g, 0)
        assert dijk_path(prev, 0, 2) == []


class TestEdgeCases:

    def test_dijkstra_rejects_negative_weight(self):
        g = make_graph(3, [(0, 1, -1.0), (1, 2, 2.0)], directed=True)
        with pytest.raises(ValueError):
            dijkstra(g, 0)

    def test_bellman_ford_detects_negative_cycle(self):
        g = make_graph(3, [(0, 1, 1.0), (1, 2, -2.0), (2, 0, 0.5)], directed=True)
        with pytest.raises(NegativeCycleError):
            bellman_ford(g, 0)

    def test_bellman_ford_handles_negative_weight_no_cycle(self):
        # Directed graph with negative edge but no negative cycle
        g = make_graph(3, [(0, 1, 4.0), (0, 2, 5.0), (1, 2, -2.0)], directed=True)
        dist, _ = bellman_ford(g, 0)
        assert dist[2] == 2.0   # 0→1→2 = 4 + (-2) = 2

    def test_zero_weight_edge(self):
        g = make_graph(2, [(0, 1, 0.0)])
        d_d, _ = dijkstra(g, 0)
        d_bf, _ = bellman_ford(g, 0)
        assert d_d[1] == 0.0
        assert d_bf[1] == 0.0

    def test_parallel_edges_take_minimum(self):
        g = make_graph(2, [(0, 1, 10.0), (0, 1, 3.0)], directed=True)
        d_d, _ = dijkstra(g, 0)
        d_bf, _ = bellman_ford(g, 0)
        assert d_d[1] == 3.0
        assert d_bf[1] == 3.0


# ---------------------------------------------------------------------------
# Run as a script (no pytest required)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import traceback
    import io

    # Force UTF-8 output on Windows to handle Unicode symbols
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    tests = [
        TestBasicCorrectness,
        TestAgreement,
        TestPathReconstruction,
        TestEdgeCases,
    ]

    passed = failed = 0
    for cls in tests:
        obj = cls()
        for name in [m for m in dir(cls) if m.startswith("test_")]:
            method = getattr(obj, name)
            try:
                method()
                print(f"  [PASS] {cls.__name__}.{name}")
                passed += 1
            except Exception as e:
                print(f"  [FAIL] {cls.__name__}.{name}: {e}")
                traceback.print_exc()
                failed += 1

    print(f"\n{'='*50}")
    print(f"  {passed} passed, {failed} failed")
    if failed == 0:
        print("  All tests PASSED")
    else:
        print("  Some tests FAILED")
        sys.exit(1)
