"""
city_data.py — Real-world road network data for the demo.

Uses a hand-curated subset of Surabaya's major road intersections
and arterial roads, with distances approximated from coordinates.

This data is used for the interactive CLI demo only (not benchmarking).
Distances are haversine (great-circle) distances multiplied by a road
detour factor of 1.35 to approximate actual road travel distances.
"""

from __future__ import annotations
import math
from src.graph import Graph


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km between two (lat, lon) points."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


ROAD_DETOUR_FACTOR = 1.35

SURABAYA_NODES: list[tuple[str, float, float]] = [
    # idx  name                          lat        lon
    ("Tunjungan Plaza",              -7.263064, 112.740039),   # 0
    ("Balai Kota Surabaya",          -7.259111, 112.746947),   # 1
    ("Stasiun Gubeng",               -7.265642, 112.753219),   # 2
    ("ITS Sukolilo",                 -7.281376, 112.794280),   # 3
    ("Universitas Airlangga",        -7.268481, 112.784191),   # 4
    ("Pelabuhan Tanjung Perak",      -7.221922, 112.732111),   # 5
    ("Royal Plaza",                  -7.308805, 112.734652),   # 6
    ("Ciputra World",                -7.292622, 112.720115),   # 7
    ("Bandara Juanda",               -7.372037, 112.787858),   # 8
    ("Surabaya Zoo (KBS)",           -7.296036, 112.736748),   # 9
    ("Pasar Turi Station",           -7.248153, 112.731068),  # 10
    ("Pakuwon Mall",                 -7.289279, 112.675636),  # 11
    ("Grand City Mall",              -7.261372, 112.750991),  # 12
    ("Kenjeran Park",                -7.252517, 112.796938),  # 13
    ("Waru Interchange",             -7.347594, 112.710376),  # 14
    ("Bundaran Waru",                -7.347153, 112.728551),  # 15
    ("Jembatan Suramadu (Sby side)", -7.208151, 112.778615),  # 16
    ("RSUD Dr Soetomo",              -7.268083, 112.758046),  # 17
    ("Pasar Keputran",               -7.274674, 112.743203),  # 18
    ("Bungkul Park",                 -7.291310, 112.739817),  # 19
]



SURABAYA_EDGES: list[tuple[int, int]] = [

    (0, 1), (0, 2), (0, 17), (0, 18),
    (1, 5), (1, 10), (1, 12),
    (2, 3), (2, 4), (2, 17),
    (3, 4), (3, 13),
    (4, 17), (4, 12),

    (5, 10), (5, 16),

    (6, 7), (6, 9), (6, 11),
    (7, 9), (7, 19),

    (8, 14), (8, 15),
    (9, 19), (9, 7),
    (10, 12), (10, 1),

    (11, 6), (11, 15), (11, 9),
    (12, 1), (12, 17),
    (13, 16), (13, 3),
    (14, 15), (14, 8),

    (15, 6), (15, 14), (15, 9),
    (16, 5), (16, 13),
    (17, 18), (17, 0),
    (18, 0), (18, 17),
    (19, 7), (19, 9),

    (6, 0), (9, 0), (7, 2),
]


def build_surabaya_graph() -> Graph:

    n = len(SURABAYA_NODES)
    g = Graph(n, directed=False)


    for i, (name, lat, lon) in enumerate(SURABAYA_NODES):
        g.set_label(i, name)
        g.set_coord(i, lat, lon)


    added: set[tuple[int, int]] = set()
    for u, v in SURABAYA_EDGES:
        key = (min(u, v), max(u, v))
        if key in added:
            continue
        added.add(key)
        lat1, lon1 = SURABAYA_NODES[u][1], SURABAYA_NODES[u][2]
        lat2, lon2 = SURABAYA_NODES[v][1], SURABAYA_NODES[v][2]
        w = round(haversine(lat1, lon1, lat2, lon2) * ROAD_DETOUR_FACTOR, 1)
        g.add_edge(u, v, w)

    return g


def node_index(name: str) -> int:

    name_lower = name.lower()
    for i, (n, _, _) in enumerate(SURABAYA_NODES):
        if name_lower in n.lower():
            return i
    raise ValueError(f"Node '{name}' not found. Available: {[n for n, *_ in SURABAYA_NODES]}")
