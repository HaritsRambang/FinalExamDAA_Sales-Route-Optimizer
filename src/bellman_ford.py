"""
bellman_ford.py — Bellman-Ford Single-Source Shortest Path algorithm.

Algorithm B (comparison baseline) for the Sales Route Optimizer.

Relaxes all edges V-1 times, then performs one additional pass to
detect negative-weight cycles.  Written entirely from scratch.

Time complexity  : O(V · E)
Space complexity : O(V)
"""

from __future__ import annotations
from typing import Optional
from src.graph import Graph

INF = float("inf")


class NegativeCycleError(Exception):
    """Raised when the graph contains a negative-weight cycle reachable from source."""
    pass


def bellman_ford(
    g: Graph,
    source: int,
) -> tuple[list[float], list[Optional[int]]]:
    """
    Run Bellman-Ford from 'source' on graph 'g'.

    Parameters
    ----------
    g      : weighted Graph (negative weights allowed; negative cycles are detected)
    source : starting vertex

    Returns
    -------
    dist   : dist[v] = shortest-path distance from source to v
             (INF if v is unreachable)
    prev   : prev[v] = predecessor of v on a shortest path

    Raises
    ------
    NegativeCycleError : if a negative-weight cycle is reachable from source
    """
    n = g.num_vertices()
    dist: list[float] = [INF] * n
    prev: list[Optional[int]] = [None] * n
    dist[source] = 0.0

    edges = g.edges  # flat list of Edge(src, dst, w)

    # --- Phase 1: V-1 relaxation passes -----------------------------------
    # After pass k, dist[v] holds the true shortest-path distance using
    # at most k edges.  After V-1 passes every simple path has been covered.
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

    # --- Phase 2: negative-cycle detection --------------------------------
    # If any distance can still be relaxed, a negative cycle exists.
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
            return []       # cycle guard (should not happen if no negative cycles)
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
