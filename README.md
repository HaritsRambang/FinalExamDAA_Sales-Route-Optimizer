# Sales Route Optimizer

**EF234405 Design & Analysis of Algorithms — Final Exam Capstone Project**

A real-world shortest-path solver for delivery/sales routing, implemented on
Surabaya's road network. Compares **Dijkstra** (Algorithm A) against
**Bellman-Ford** (Algorithm B) on the same problem instances.

---

## Problem

A sales representative starts from a depot and must find the shortest road
route to each of several customer locations. Modelled as a **weighted
undirected graph** where vertices are intersections/landmarks and edge
weights are road distances in km (Euclidean / Haversine approximations).

## Algorithms

| | Dijkstra | Bellman-Ford |
|---|---|---|
| **Complexity** | O((V + E) log V) | O(V · E) |
| **Weights** | Non-negative only | Negative weights OK |
| **Negative cycle** | N/A | Detected & raises error |
| **Data structure** | Binary min-heap | Edge list, V–1 passes |

---

## Project Structure

```
sales-route-optimizer/
├── src/
│   ├── graph.py          # Weighted graph (adjacency list)
│   ├── dijkstra.py       # Algorithm A — Dijkstra (binary heap)
│   ├── bellman_ford.py   # Algorithm B — Bellman-Ford
│   ├── generator.py      # Random connected graph generator
│   └── city_data.py      # Real Surabaya road network (20 nodes, 36 edges)
├── tests/
│   └── test_correctness.py  # 18 correctness + cross-check tests
├── results/
│   ├── benchmark_results.csv
│   └── runtime_plot.png
├── demo.py               # Interactive CLI demo (Surabaya network)
├── benchmark.py          # One-command benchmark harness
├── requirements.txt
└── README.md
```

---

## Quick Start

### 1. Clone & install dependencies

```bash
git clone https://github.com/<your-username>/sales-route-optimizer.git
cd sales-route-optimizer
pip install -r requirements.txt
```

### 2. Run the interactive demo (real Surabaya road network)

```bash
# Default: depot = Tunjungan Plaza, customers = ITS, Juanda, Pakuwon, Kenjeran
python demo.py

# List all available nodes
python demo.py --list-nodes

# Custom route: depot=Stasiun Gubeng [2], customers=[5, 8, 11, 14]
python demo.py --source 2 --targets 5 8 11 14
```

### 3. Run correctness tests

```bash
python tests/test_correctness.py
# or with pytest:
python -m pytest tests/ -v
```

### 4. Reproduce the benchmark (one command)

```bash
python benchmark.py
```

This generates:
- `results/benchmark_results.csv` — timing data for all 7 sizes
- `results/runtime_plot.png` — linear + log-log runtime plot

For a quick smoke test (fewer sizes):

```bash
python benchmark.py --quick
```

---

## Benchmark Results (reference run)

Machine: Intel Core i5, Python 3.11, E ≈ 5V sparse graphs, 5-run average.

| V | E | Dijkstra (ms) | Bellman-Ford (ms) | Ratio | Match |
|---|---|---|---|---|---|
| 100 | 500 | 0.099 | 0.216 | 2.2× | ✓ |
| 300 | 1500 | 0.302 | 1.056 | 3.5× | ✓ |
| 500 | 2500 | 0.604 | 1.554 | 2.6× | ✓ |
| 1,000 | 5,000 | 1.309 | 2.963 | 2.3× | ✓ |
| 2,000 | 10,000 | 2.828 | 7.460 | 2.6× | ✓ |
| 5,000 | 25,000 | 7.391 | 18.899 | 2.6× | ✓ |
| 10,000 | 50,000 | 17.880 | 50.688 | 2.8× | ✓ |

All distances agreed on every instance (correctness cross-check ✓).

---

## Language & Tools

- **Python 3.10+**
- `heapq` — Python standard library binary min-heap (supporting structure only; SSSP logic is written from scratch)
- `matplotlib`, `numpy` — plotting only
- `pytest` — test runner

---

## Attribution

- Surabaya node coordinates: manually curated from Google Maps / OpenStreetMap data.
- No external shortest-path or graph library is used. All algorithmic logic is the team's own work.
- `heapq` is used solely as a heap data structure (not a graph/SSSP library).

---

## Authors

| Name | Student ID | Contribution |
|---|---|---|
| Leyan Harits Rambang Wicaksana | 5025231288 | All components (graph, Dijkstra, Bellman-Ford, benchmark, tests, demo) |

