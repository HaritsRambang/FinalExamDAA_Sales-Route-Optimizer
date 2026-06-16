"""
dijkstra.py — Dijkstra's Single-Source Shortest Path algorithm.

Algorithm A (primary) for the Sales Route Optimizer.

Uses a binary min-heap (Python's heapq) as the priority queue.
The core logic is written from scratch; heapq is used only as a
supporting data structure (a library heap, not a library SSSP).

Time complexity  : O((V + E) log V)
Space complexity : O(V + E)
"""

from __future__ import annotations
import heapq
from typing import Optional
from src.graph import Graph

INF = float("inf")


def dijkstra(
    g: Graph,
    source: int,
) -> tuple[list[float], list[Optional[int]]]:

    n = g.num_vertices()

    for edge in g.edges:
        if edge.w < 0:
            raise ValueError(
                f"Dijkstra requires non-negative weights; "
                f"found w={edge.w} on edge ({edge.src}→{edge.dst})."
            )

    dist: list[float] = [INF] * n
    prev: list[Optional[int]] = [None] * n
    dist[source] = 0.0

    heap: list[tuple[float, int]] = [(0.0, source)]

    while heap:
        d_u, u = heapq.heappop(heap)

        # Stale entry: a shorter path to u was already finalised
        if d_u > dist[u]:
            continue

        for v, w in g.neighbours(u):
            alt = dist[u] + w
            if alt < dist[v]:
                dist[v] = alt
                prev[v] = u
                heapq.heappush(heap, (alt, v))

    return dist, prev


def reconstruct_path(prev: list[Optional[int]], source: int, target: int) -> list[int]:

    path: list[int] = []
    node: Optional[int] = target
    while node is not None:
        path.append(node)
        if node == source:
            break
        node = prev[node]
    else:
        return []      

    path.reverse()
    if path[0] != source:
        return []        
    return path
