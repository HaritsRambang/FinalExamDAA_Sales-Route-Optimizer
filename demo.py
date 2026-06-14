"""
demo.py — Interactive CLI demo for the Sales Route Optimizer.

Uses the real Surabaya road network.
Lets the user pick a depot and multiple customer locations,
then finds and displays the shortest route using both Dijkstra and Bellman-Ford.

Usage:
    python demo.py
    python demo.py --source 0 --targets 3 8 11
    python demo.py --list-nodes
"""

from __future__ import annotations
import argparse
import sys
import time

from src.city_data import build_surabaya_graph, SURABAYA_NODES
from src.dijkstra import dijkstra, reconstruct_path as dijk_path
from src.bellman_ford import bellman_ford, reconstruct_path as bf_path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def print_header() -> None:
    print("=" * 60)
    print("      SALES ROUTE OPTIMIZER — Surabaya Road Network")
    print("      Dijkstra vs Bellman-Ford Shortest Path Demo")
    print("=" * 60)


def list_nodes() -> None:
    print("\nAvailable nodes:")
    for i, (name, lat, lon) in enumerate(SURABAYA_NODES):
        print(f"  [{i:2d}] {name} ({lat:.6f}, {lon:.6f})")


def format_path(g, path: list[int]) -> str:
    if not path:
        return "(unreachable)"
    return " → ".join(g.label(v) for v in path)


def run_demo(source: int, targets: list[int]) -> None:
    g = build_surabaya_graph()
    print_header()
    print(f"\nDepot (source) : [{source}] {g.label(source)}")
    print(f"Customers      : {[f'[{t}] {g.label(t)}' for t in targets]}")
    print(f"Graph size     : {g.num_vertices()} nodes, {g.num_edges() // 2} undirected edges\n")

    # -----------------------------------------------------------------------
    # Run both algorithms
    # -----------------------------------------------------------------------
    t0 = time.perf_counter()
    dist_d, prev_d = dijkstra(g, source)
    time_d = (time.perf_counter() - t0) * 1000  # ms

    t0 = time.perf_counter()
    dist_bf, prev_bf = bellman_ford(g, source)
    time_bf = (time.perf_counter() - t0) * 1000  # ms

    # -----------------------------------------------------------------------
    # Display results per customer
    # -----------------------------------------------------------------------
    print(f"{'Destination':<35} {'Dijkstra':>12} {'Bellman-Ford':>14} {'Match':>7}")
    print("-" * 72)

    all_match = True
    for t in targets:
        d_dist = dist_d[t]
        b_dist = dist_bf[t]
        match = abs(d_dist - b_dist) < 1e-9 if d_dist != float("inf") else d_dist == b_dist
        if not match:
            all_match = False
        flag = "✓" if match else "✗ MISMATCH"
        label = g.label(t)[:33]
        dist_str_d = f"{d_dist:.1f} km" if d_dist != float("inf") else "∞"
        dist_str_b = f"{b_dist:.1f} km" if b_dist != float("inf") else "∞"
        print(f"[{t:2d}] {label:<31} {dist_str_d:>12} {dist_str_b:>14} {flag:>7}")

    print("-" * 72)
    print(f"\n⏱  Dijkstra     : {time_d:.4f} ms")
    print(f"⏱  Bellman-Ford : {time_bf:.4f} ms")
    print(f"\n✅ All distances match: {all_match}")

    # -----------------------------------------------------------------------
    # Print detailed paths
    # -----------------------------------------------------------------------
    print("\n--- Shortest Paths (Dijkstra) ---")
    for t in targets:
        path = dijk_path(prev_d, source, t)
        d = dist_d[t]
        dist_str = f"{d:.1f} km" if d != float("inf") else "∞"
        print(f"\n  To [{t}] {g.label(t)} ({dist_str}):")
        print(f"    {format_path(g, path)}")

    print("\n--- Shortest Paths (Bellman-Ford) ---")
    for t in targets:
        path = bf_path(prev_bf, source, t)
        d = dist_bf[t]
        dist_str = f"{d:.1f} km" if d != float("inf") else "∞"
        print(f"\n  To [{t}] {g.label(t)} ({dist_str}):")
        print(f"    {format_path(g, path)}")

    print("\n" + "=" * 60)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sales Route Optimizer — Surabaya shortest path demo."
    )
    parser.add_argument("--list-nodes", action="store_true",
                        help="List all available node indices and names, then exit.")
    parser.add_argument("--source", type=int, default=0,
                        help="Source (depot) node index (default: 0 = Tunjungan Plaza).")
    parser.add_argument("--targets", type=int, nargs="+",
                        default=[3, 8, 11, 13],
                        help="Target (customer) node indices (default: 3 8 11 13).")
    args = parser.parse_args()

    if args.list_nodes:
        list_nodes()
        sys.exit(0)

    # Validate indices
    n = len(SURABAYA_NODES)
    for idx in [args.source] + args.targets:
        if not (0 <= idx < n):
            print(f"Error: node index {idx} out of range (0..{n-1}).")
            sys.exit(1)

    run_demo(args.source, args.targets)


if __name__ == "__main__":
    main()
