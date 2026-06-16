from __future__ import annotations
import math
import random
from src.graph import Graph


def euclidean(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def generate_random_graph(
    n: int,
    avg_degree: float = 5.0,
    seed: int = 42,
    directed: bool = False,
    coord_scale: float = 1000.0,
) -> Graph:

    rng = random.Random(seed)

    g = Graph(n, directed=directed)

    # Step 1: place vertices in 2-D space
    coords = [(rng.uniform(0, coord_scale), rng.uniform(0, coord_scale)) for _ in range(n)]
    for i, (x, y) in enumerate(coords):
        g.set_coord(i, x, y)

    # Step 2: random spanning tree (shuffle and connect sequentially)
    perm = list(range(n))
    rng.shuffle(perm)
    for i in range(1, n):
        u = perm[i - 1]
        v = perm[i]
        w = round(euclidean(*coords[u], *coords[v]), 4)
        g.add_edge(u, v, w)

    # Step 3: add extra random edges
    target_edges = int(n * avg_degree / 2)
    added = n - 1  # already added from spanning tree
    attempts = 0
    max_attempts = target_edges * 10

    edge_set: set[tuple[int, int]] = set()
    for edge in g.edges:
        edge_set.add((edge.src, edge.dst))

    while added < target_edges and attempts < max_attempts:
        u = rng.randint(0, n - 1)
        v = rng.randint(0, n - 1)
        if u == v:
            attempts += 1
            continue
        key = (min(u, v), max(u, v)) if not directed else (u, v)
        if key in edge_set:
            attempts += 1
            continue
        w = round(euclidean(*coords[u], *coords[v]), 4)
        g.add_edge(u, v, w)
        edge_set.add(key)
        added += 1
        attempts += 1

    return g


def generate_graphs_for_benchmark(
    sizes: list[int],
    avg_degree: float = 5.0,
    base_seed: int = 42,
) -> list[tuple[int, Graph]]:

    result = []
    for i, n in enumerate(sizes):
        g = generate_random_graph(n, avg_degree=avg_degree, seed=base_seed + i)
        result.append((n, g))
    return result
