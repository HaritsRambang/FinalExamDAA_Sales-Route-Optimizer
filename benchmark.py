"""
benchmark.py — One-command benchmark harness for the Sales Route Optimizer.

Measures wall-clock runtime of Dijkstra and Bellman-Ford across
5+ input sizes spanning two orders of magnitude (100 → 10,000 vertices).

Usage:
    python benchmark.py                   # run full benchmark, save CSV + plot
    python benchmark.py --quick           # fewer sizes, for a fast smoke test
    python benchmark.py --no-plot         # skip matplotlib (headless servers)

Output:
    results/benchmark_results.csv         — raw timing data
    results/runtime_plot.png              — runtime-vs-size plot (log-log + linear)
"""

from __future__ import annotations
import argparse
import csv
import os
import sys
import time
from pathlib import Path

# Ensure project root is on path when run directly
sys.path.insert(0, str(Path(__file__).parent))

from src.generator import generate_random_graph
from src.dijkstra import dijkstra
from src.bellman_ford import bellman_ford

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

FULL_SIZES   = [100, 300, 500, 1_000, 2_000, 5_000, 10_000]
QUICK_SIZES  = [100, 500, 1_000, 3_000, 5_000]
AVG_DEGREE   = 5.0          # edges ≈ 5·V  (sparse, road-network-like)
BASE_SEED    = 42
RUNS_PER_SIZE = 5            # average over this many runs for stable timing
RESULTS_DIR  = Path("results")
CSV_PATH     = RESULTS_DIR / "benchmark_results.csv"
PLOT_PATH    = RESULTS_DIR / "runtime_plot.png"

# ---------------------------------------------------------------------------
# Core benchmark
# ---------------------------------------------------------------------------

def time_algorithm(fn, *args, runs: int = RUNS_PER_SIZE) -> float:
    """Return average wall-clock time (seconds) over 'runs' executions."""
    total = 0.0
    for _ in range(runs):
        t0 = time.perf_counter()
        fn(*args)
        total += time.perf_counter() - t0
    return total / runs


def run_benchmark(sizes: list[int]) -> list[dict]:
    """
    Run Dijkstra and Bellman-Ford on graphs of each size in 'sizes'.

    Returns a list of result dicts (one per size).
    """
    results = []
    print(f"\n{'V':>8}  {'E':>8}  {'Dijkstra (ms)':>15}  {'Bellman-Ford (ms)':>18}  {'BF/Dijk':>8}  {'Same?':>6}")
    print("-" * 72)

    for i, n in enumerate(sizes):
        seed = BASE_SEED + i
        g = generate_random_graph(n, avg_degree=AVG_DEGREE, seed=seed)
        source = 0  # always route from vertex 0

        # Warm up (not timed)
        dijkstra(g, source)

        t_dijk = time_algorithm(dijkstra, g, source) * 1000   # → ms
        t_bf   = time_algorithm(bellman_ford, g, source) * 1000

        # Correctness cross-check: distances must be identical
        dist_d, _ = dijkstra(g, source)
        dist_bf, _ = bellman_ford(g, source)
        same = all(
            abs(dist_d[v] - dist_bf[v]) < 1e-9
            for v in range(n)
            if dist_d[v] != float("inf")
        )

        ratio = t_bf / t_dijk if t_dijk > 0 else float("inf")
        e = g.num_edges()
        print(f"{n:>8}  {e:>8}  {t_dijk:>15.3f}  {t_bf:>18.3f}  {ratio:>8.1f}x  {'✓' if same else '✗':>6}")

        results.append({
            "n_vertices": n,
            "n_edges": e,
            "avg_degree": AVG_DEGREE,
            "seed": seed,
            "dijkstra_ms": round(t_dijk, 4),
            "bellman_ford_ms": round(t_bf, 4),
            "bf_dijk_ratio": round(ratio, 2),
            "distances_match": same,
        })

    return results


# ---------------------------------------------------------------------------
# CSV export
# ---------------------------------------------------------------------------

def save_csv(results: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"\n📄 CSV saved → {path}")


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def save_plot(results: list[dict], path: Path) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("⚠  matplotlib not installed — skipping plot.")
        return

    ns    = [r["n_vertices"]     for r in results]
    t_d   = [r["dijkstra_ms"]    for r in results]
    t_bf  = [r["bellman_ford_ms"] for r in results]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Sales Route Optimizer — Runtime Benchmark\n"
                 "Dijkstra vs Bellman-Ford (sparse graph, E ≈ 5V)",
                 fontsize=13)

    # --- (a) Linear scale ---
    ax = axes[0]
    ax.plot(ns, t_d,  "o-", color="#2196F3", linewidth=2, markersize=6, label="Dijkstra")
    ax.plot(ns, t_bf, "s-", color="#F44336", linewidth=2, markersize=6, label="Bellman-Ford")
    ax.set_xlabel("Number of vertices (V)", fontsize=11)
    ax.set_ylabel("Average runtime (ms)", fontsize=11)
    ax.set_title("(a) Linear scale")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)

    # --- (b) Log-log scale + empirical exponent ---
    ax = axes[1]
    log_ns = np.log10(ns)
    log_d  = np.log10(np.maximum(t_d, 1e-9))
    log_bf = np.log10(np.maximum(t_bf, 1e-9))

    # Fit a line (log-log) to estimate empirical growth exponent
    exp_d  = np.polyfit(log_ns, log_d, 1)[0]
    exp_bf = np.polyfit(log_ns, log_bf, 1)[0]

    ax.plot(ns, t_d,  "o-", color="#2196F3", linewidth=2, markersize=6,
            label=f"Dijkstra (slope ≈ {exp_d:.2f})")
    ax.plot(ns, t_bf, "s-", color="#F44336", linewidth=2, markersize=6,
            label=f"Bellman-Ford (slope ≈ {exp_bf:.2f})")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Number of vertices V (log scale)", fontsize=11)
    ax.set_ylabel("Average runtime ms (log scale)", fontsize=11)
    ax.set_title("(b) Log-log scale (slope = empirical exponent)")
    ax.legend()
    ax.grid(True, which="both", alpha=0.3)

    plt.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"📊 Plot saved  → {path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark Dijkstra vs Bellman-Ford.")
    parser.add_argument("--quick",   action="store_true", help="Use fewer/smaller sizes.")
    parser.add_argument("--no-plot", action="store_true", help="Skip matplotlib plot.")
    args = parser.parse_args()

    sizes = QUICK_SIZES if args.quick else FULL_SIZES

    print("=" * 72)
    print("  BENCHMARK: Dijkstra vs Bellman-Ford — Sales Route Optimizer")
    print(f"  Sizes: {sizes}")
    print(f"  Runs per size: {RUNS_PER_SIZE}  |  Avg degree: {AVG_DEGREE}  |  Base seed: {BASE_SEED}")
    print("=" * 72)

    results = run_benchmark(sizes)
    save_csv(results, CSV_PATH)

    if not args.no_plot:
        save_plot(results, PLOT_PATH)

    # Summary
    all_match = all(r["distances_match"] for r in results)
    print(f"\n✅ Correctness cross-check (all sizes): {'PASSED ✓' if all_match else 'FAILED ✗'}")
    print("\nDone.")


if __name__ == "__main__":
    main()
