from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Edge:

    src: int
    dst: int
    w: float


class Graph:

    def __init__(self, n: int, directed: bool = False):

        self.n = n
        self.directed = directed
        # adj[u] = list of (v, weight) neighbours
        self.adj: list[list[tuple[int, float]]] = [[] for _ in range(n)]
        self.edges: list[Edge] = []          # flat edge list (for Bellman-Ford)
        # optional: store node labels/coordinates for the real-world demo
        self.labels: dict[int, str] = {}
        self.coords: dict[int, tuple[float, float]] = {}  # (lat, lon)

    def add_edge(self, u: int, v: int, w: float) -> None:

        if w < 0 and not self.directed:
            raise ValueError("Undirected graphs require non-negative weights.")
        self.adj[u].append((v, w))
        self.edges.append(Edge(u, v, w))
        if not self.directed:
            self.adj[v].append((u, w))
            self.edges.append(Edge(v, u, w))

    def set_label(self, v: int, label: str) -> None:
        self.labels[v] = label

    def set_coord(self, v: int, lat: float, lon: float) -> None:
        self.coords[v] = (lat, lon)


    def neighbours(self, u: int) -> list[tuple[int, float]]:

        return self.adj[u]

    def num_vertices(self) -> int:
        return self.n

    def num_edges(self) -> int:

        return len(self.edges)

    def label(self, v: int) -> str:
        return self.labels.get(v, str(v))

    def __repr__(self) -> str:
        return f"Graph(n={self.n}, edges={self.num_edges()}, directed={self.directed})"
