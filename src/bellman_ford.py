from __future__ import annotations
from typing import Optional
from src.graph import Graph

INF = float("inf")


class NegativeCycleError(Exception):

    pass


def bellman_ford(
    g: Graph,
    source: int,
) -> tuple[list[float], list[Optional[int]]]:

    n = g.num_vertices()
    dist: list[float] = [INF] * n
    prev: list[Optional[int]] = [None] * n
    dist[source] = 0.0

    edges = g.edges  # flat list of Edge(src, dst, w)

    for _ in range(n - 1):
        updated = False
        for edge in edges:
            u, v, w = edge.src, edge.dst, edge.w
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                prev[v] = u
                updated = True
        # Early termination: if no update occurred, we are done
        if not updated:
            break

    for edge in edges:
        u, v, w = edge.src, edge.dst, edge.w
        if dist[u] != INF and dist[u] + w < dist[v]:
            raise NegativeCycleError(
                f"Negative-weight cycle detected reachable from source {source}."
            )

    return dist, prev


def reconstruct_path(prev: list[Optional[int]], source: int, target: int) -> list[int]:
    """
    Reconstruct shortest path from source to target via predecessor array.

    Returns list of vertices source→…→target, or [] if unreachable.
    """
    path: list[int] = []
    node: Optional[int] = target
    visited = set()
    while node is not None:
        if node in visited:
            return []       
        visited.add(node)
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
