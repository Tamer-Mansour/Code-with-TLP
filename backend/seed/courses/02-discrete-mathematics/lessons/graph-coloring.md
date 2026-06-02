# Graph Coloring

**Graph coloring** assigns labels ("colors") to vertices (or edges) of a graph so that no two adjacent elements share the same color. Despite sounding like an art problem, it models resource-allocation conflicts — from register allocation in compilers to exam scheduling.

## Vertex Coloring

A **proper k-coloring** of graph G is a function `c: V → {1, 2, …, k}` such that `c(u) ≠ c(v)` whenever `(u, v) ∈ E`.

The **chromatic number χ(G)** is the minimum k for which a proper k-coloring exists.

| Graph | χ(G) | Reason |
|-------|------|--------|
| Empty graph (no edges) | 1 | One color suffices |
| Path Pₙ (n ≥ 2) | 2 | Alternate two colors |
| Even cycle C₂ₖ | 2 | Bipartite |
| Odd cycle C₂ₖ₊₁ | 3 | One vertex breaks bipartiteness |
| Complete graph Kₙ | n | Every pair adjacent |
| Petersen graph | 3 | Non-bipartite, triangle-free |

**Key theorem:** A graph G is **bipartite if and only if χ(G) ≤ 2** (equivalently, iff G has no odd-length cycle).

## Greedy Coloring

The greedy algorithm assigns to each vertex the smallest color not used by any already-colored neighbor.

```python
def greedy_color(adj, n):
    """adj: adjacency list (1-indexed, list of lists). Returns color list."""
    color = [0] * (n + 1)          # 0 = uncolored
    for v in range(1, n + 1):
        used = {color[u] for u in adj[v] if color[u] != 0}
        c = 1
        while c in used:
            c += 1
        color[v] = c
    return color
```

- **Guarantee:** Greedy uses at most `Δ(G) + 1` colors, where `Δ(G)` is the maximum degree.
- **Brook's theorem (1941):** χ(G) ≤ Δ(G) unless G is a complete graph or an odd cycle, in which case χ(G) = Δ(G) + 1.
- **Drawback:** The result depends on vertex ordering. On some graphs greedy uses far more colors than χ(G).

## Four Color Theorem

Every **planar graph** has χ(G) ≤ 4. This was conjectured in 1852 and proved (with computer assistance) in 1976 by Appel and Haken — the first major theorem proved with a computer. The proof reduced the problem to checking ~1,900 reducible configurations.

**Corollary:** Any map where regions sharing a border (not just a point) must have different colors needs at most 4 colors.

## Edge Coloring

An **edge coloring** assigns colors to edges so that no two edges sharing a vertex have the same color. The **chromatic index χ'(G)** is the minimum number of colors needed.

- **Vizing's theorem:** χ'(G) is either Δ(G) or Δ(G) + 1 for simple graphs.
  - **Class 1:** χ'(G) = Δ(G) (e.g., bipartite graphs, by König's theorem)
  - **Class 2:** χ'(G) = Δ(G) + 1 (e.g., odd cycles, K₃)

**Application:** Round-robin tournament scheduling. If n teams each play one match per round, the schedule corresponds to an edge coloring of Kₙ: each color = one round. Kₙ (n even) is Class 1 with Δ = n−1, so n−1 rounds suffice.

## CS Applications

| Application | Graph | Coloring meaning |
|-------------|-------|-----------------|
| Register allocation | Interference graph: variables as vertices, edge if live simultaneously | Colors = physical registers; χ = minimum registers needed |
| Exam scheduling | Conflict graph: courses as vertices, edge if a student takes both | Colors = time slots; χ = minimum slots with no conflicts |
| Map coloring | Planar graph of regions | Colors = distinct map colors; χ ≤ 4 by four-color theorem |
| Frequency assignment | Graph of base stations | Colors = radio frequencies; adjacent stations get different frequencies |
| Sudoku | 81-vertex graph (row/column/box constraints as edges) | 9-coloring = valid Sudoku solution |

## Chromatic Polynomial

For graph G, the **chromatic polynomial** P(G, k) counts the number of proper k-colorings.

- **Path Pₙ:** P(Pₙ, k) = k(k−1)^(n−1)
- **Cycle Cₙ:** P(Cₙ, k) = (k−1)^n + (−1)^n (k−1)
- **Tree on n vertices:** P(T, k) = k(k−1)^(n−1) (same as path)
- **Complete Kₙ:** P(Kₙ, k) = k(k−1)(k−2)···(k−n+1) = k! / (k−n)!

The smallest positive integer k where P(G, k) > 0 is exactly χ(G).

**Example — triangle K₃:**
```
P(K₃, k) = k(k−1)(k−2)
P(K₃, 2) = 2·1·0 = 0   → 2 colors are not enough
P(K₃, 3) = 3·2·1 = 6   → 6 proper 3-colorings exist
```

## Complexity

- Deciding χ(G) ≤ 2 (bipartiteness) is solvable in O(n + m) with BFS/DFS.
- Deciding χ(G) ≤ 3 is NP-complete.
- Approximating χ(G) within a factor of n^(1−ε) for any ε > 0 is also NP-hard (unless P = NP).

This gulf between 2-coloring (easy) and 3-coloring (NP-complete) is one of the cleanest illustrations of computational hardness in discrete mathematics.
