# Algorithm & Data-Structure Visualizers — Implementation Plan

**App:** Code with TLP · **Source of scope:** [VisuAlgo](https://visualgo.net/en) · **Drafted:** 2026-05-27

A VisuAlgo-style interactive visualization section for Code with TLP. This plan covers
**every module on VisuAlgo**, the architecture to build them, how they plug into the
existing app, and a phased roadmap.

---

## 1. Goal

Let learners **watch and control** animations of data structures and algorithms, with the
same frame/player model proven in the standalone demo (`ds-animations-demo.html`):

> **algorithm → list of frames → a player applies one frame at a time → CSS/SVG transitions animate.**

Each module supports multiple operations, step/play controls, a synced pseudocode panel, and
custom input.

---

## 2. How it fits the app

Lessons render through `ngx-markdown`, so interactive widgets cannot live in the markdown body.
Two integration points:

1. **Standalone catalog** at `/visualize` — a grid of modules grouped by category (mirrors the
   VisuAlgo home). **This is the MVP.**
2. **Lesson embedding (later)** — a new `visualizer` lesson type (or a markdown placeholder the
   reader swaps for a component) so a lesson can show its matching visualizer inline; exercises in
   the relevant topics get a "Visualize this" link.

No backend changes are required for the MVP — visualizers are deterministic from input.

---

## 3. Architecture

```
frontend/src/app/features/visualizers/
  core/
    viz-frame.ts          # Frame model (see §3.1)
    viz-player.service.ts # play / pause / step / step-back / seek / speed (signals)
    visualizer.base.ts    # interface every module implements
    registry.ts           # slug -> { title, category, operations, loadComponent }
  shared/
    player-bar/           # play/pause/step/back/speed/progress — reused everywhere
    pseudocode-panel/     # highlights the running line for the current frame
    viz-controls/         # operation buttons + custom-input + random/example
    viz-legend/
  catalog/                # /visualize  (grid by category)
  viz-page/               # /visualize/:slug  (controls + canvas + pseudocode)
  modules/                # one component per visualizer (array, bst, graph, ...)
```

### 3.1 Frame & player contract (shared by all modules)

```ts
interface VizFrame {
  note: string;                 // human explanation shown under the canvas
  pseudoLine?: number;          // line to highlight in the pseudocode panel
  states?: Record<string, string>; // elementId -> visual state (compare/swap/active/visited/...)
  // module-specific payload (array order, graph edge states, tree reveal set, ...)
  data?: unknown;
}

interface Visualizer {
  meta: VizMeta;                          // title, category, operations, complexity
  buildFrames(op: string, input: VizInput): VizFrame[];
  renderFrame(frame: VizFrame): void;     // pure view update; transitions do the motion
}
```

The `VizPlayer` service is module-agnostic: it owns `frames`, `index`, `playing`, `speed`, and
calls `renderFrame`. Built once, reused by every module.

### 3.2 Rendering strategy

| Layer | Used for | Notes |
|---|---|---|
| **DOM + CSS** | arrays/bars, stacks, queues, hash buckets | `transform` slides, color = state class |
| **SVG + CSS** | trees, heaps, linked lists, graphs, geometry, segment/Fenwick trees | edges as `<line>`/`<path>`, nodes positioned by transform |
| **Canvas** (only if needed) | very large graphs, geometry sweeps | Phase 4 |
| **Layout helpers** | free-form graphs | consider `d3-force` or `elkjs`; fixed layouts otherwise |

No animation library for Phases 1–3; revisit GSAP/anime.js for Phase 4 sequencing.

---

## 4. Cross-cutting features (ported from VisuAlgo)

- **Synced pseudocode panel** — highlights the current line per frame (VisuAlgo's signature).
- **Custom input** — "enter your own array / values / edges / graph".
- **Random / example generators** per module.
- **Full transport** — play, pause, **step back**, step forward, **seek to any step**, speed.
- **Multiple operations** per structure (insert / search / delete / traverse / update / …).
- **Complexity badge** (time & space) per operation.
- **Two modes (later):** guided "e-Lecture" vs free "Exploration".
- Dark/light theme, responsive, matches the app's purple→blue gradient styling.

---

## 5. Full VisuAlgo module catalog → app mapping

Status legend: **P1** = MVP, **P2/P3** = follow-on, **P4** = advanced.

### 5.1 Data Structures

| Module | What it visualizes | Operations to implement | Render | Phase |
|---|---|---|---|---|
| **Array (1D)** | indexed cells; substrate for sorting/search | create, access, search, update | DOM | **P1** |
| **Linked List** | SLL, DLL, **Stack**, **Queue**, **Deque** | insert head/tail/pos, remove, search, peek, push/pop, enqueue/dequeue | SVG | **P1** |
| **Binary Heap / Priority Queue** | array-backed binary heap as a tree | insert, extractMax/Min, build O(n) vs O(n log n), heapsort, update key | SVG | P2 |
| **Hash Table** | separate chaining, linear/quadratic probing, double hashing | insert, search, remove, show load factor & collisions | DOM/SVG | P2 |
| **Binary Search Tree / AVL** | BST + AVL self-balancing | insert, search, remove, pred/succ, in/pre/post/level traversal, rank/select, rotations | SVG | **P1** (BST), P2 (AVL) |
| **Graph Structures** | adjacency matrix/list/edge list; tree, complete, bipartite, DAG examples | build, switch representation, example library | SVG | P2 |
| **Union-Find (Disjoint Sets)** | forest with path compression & union by rank | find, isSameSet, unionSet | SVG | P3 |
| **Fenwick Tree (BIT)** | binary indexed tree for range queries | build, point update + prefix/range sum, RuPQ/RsQ | SVG | P3 |
| **Segment Tree** | range query tree | build, range min/max/sum query, point update, range update + lazy propagation | SVG | P3 |

### 5.2 Sorting & Basic Algorithms

| Module | What it visualizes | Operations / variants | Render | Phase |
|---|---|---|---|---|
| **Sorting** | comparison & non-comparison sorts on a bar array | Bubble, Selection, Insertion, Merge, Quick, Random Quick, Counting, Radix | DOM | **P1** (first 5), P2 (counting/radix) |
| **Searching** | linear & binary search on an array | Linear, Binary (auto-sort) | DOM | **P1** |
| **Bitmask** | set operations via bits | set/clear/toggle/check bit, subset enumeration | DOM | P4 |
| **Recursion Tree / DAG** | call tree of any recursive fn; DP memoization | factorial, fib (naive vs memo), generic recursion | SVG | P2 |

### 5.3 Graph Algorithms

| Module | What it visualizes | Operations / variants | Render | Phase |
|---|---|---|---|---|
| **Graph Traversal** | DFS & BFS frontier expansion | DFS, BFS, topological sort, connected components, **SCC** (Tarjan/Kosaraju), bipartite check, **bridges & articulation points**, cycle detection | SVG | P2 (DFS/BFS), P3 (rest) |
| **Min Spanning Tree** | edges chosen to form the MST | **Kruskal**, **Prim** | SVG | P3 |
| **Single-Source Shortest Paths** | relaxation & distance updates | BFS (unweighted), **Dijkstra**, **Bellman-Ford**, DAG DP, 0/1-BFS | SVG | P3 |
| **Cycle Finding** | finding a cycle in a functional graph | Floyd tortoise–hare, Brent | SVG | P3 |
| **Network Flow (Max Flow)** | residual graph & augmenting paths | Ford-Fulkerson, Edmonds-Karp, Dinic; min cut | SVG | P4 |
| **Graph Matching** | augmenting paths for matching | Max Cardinality Bipartite Matching (Kuhn / Hopcroft-Karp) | SVG | P4 |

### 5.4 Advanced Topics

| Module | What it visualizes | Operations / variants | Render | Phase |
|---|---|---|---|---|
| **Suffix Tree** | suffix tree construction & queries | build (Ukkonen), substring search, longest repeated substring | SVG | P4 |
| **Suffix Array** | sorted suffixes + LCP | build, LCP, string matching, LRS, LCS | DOM/SVG | P4 |
| **Geometry (Polygon)** | polygon properties | area, perimeter, point-in-polygon, convex/concave, cut polygon | SVG | P4 |
| **Convex Hull** | hull construction sweep | Graham Scan, Andrew's Monotone Chain, Jarvis March | SVG | P4 |
| **Min Vertex Cover** | MVC on trees & bipartite graphs | tree DP, König's theorem (via matching) | SVG | P4 |
| **Steiner Tree** | minimum Steiner tree (NP-hard) | DP over subsets | SVG | P4 |
| **Travelling Salesperson (TSP)** | tours & optimal route | brute force, Held-Karp DP, MST 2-approx | SVG | P4 |
| **NP-complete Reductions** | mapping one problem to another | reduction walkthroughs | SVG | P4 |

---

## 6. Phased roadmap

### Phase 1 — MVP (foundation + highest-value modules)
- Build **core** (frame model, `VizPlayer`, base interface, registry).
- Build **shared UI** (player-bar, pseudocode-panel, viz-controls, legend).
- Build **catalog** (`/visualize`) and **viz-page** (`/visualize/:slug`) shells.
- Reference modules: **Array + Sorting** (bubble/selection/insertion/merge/quick),
  **Linear & Binary Search**, **Stack/Queue**, **Linked List**, **BST**.
- Add **"Visualize"** to the navbar.

### Phase 2 — core CS2
Binary Heap / Priority Queue · Hash Table · Recursion/DP tree · Graph structures · BFS/DFS · AVL · Counting/Radix sort.

### Phase 3 — classic algorithms
Union-Find · Fenwick Tree · Segment Tree · MST (Prim/Kruskal) · Shortest paths (Dijkstra/Bellman-Ford) · advanced traversal (SCC, bridges, toposort) · cycle finding.

### Phase 4 — advanced / NP-hard / geometry / strings
Network flow · Graph matching · Convex hull · Geometry · Suffix tree/array · Bitmask · Min vertex cover · Steiner tree · TSP · NP-complete reductions.

---

## 7. Integration with existing content

- Navbar gets a **Visualize** entry → `/visualize`.
- Link each visualizer from the matching lesson/course already in the app:
  - **Data Structures** course → array, linked-list, stack/queue, BST, heap, hash table.
  - **Algorithms / Intro to Algorithms** → sorting, searching, graph algorithms.
- Optional "Visualize this" button on exercises in those topics.
- Later: `visualizer` lesson type to embed a specific module inline.

---

## 8. Build process & agent parallelization

1. **Core first, solo** — implement the player, frame model, base interface, shared UI, catalog,
   viz-page, and **one reference module (Array/Sorting)**. This freezes the contract.
2. **Fan out with agents** — each remaining module is independent, so build them in parallel
   (same approach as the course content), each agent implementing one module against the shared
   `Visualizer` interface + a SPEC. Do Phase 1 modules first, then 2, 3, 4.
3. **Wire & verify** — navbar + lesson links, `npm run build`, manual browser pass per module
   (animations can't be validated by the build alone).

### Per-module SPEC (what each agent receives)
- Module slug, category, list of operations, and time/space complexity per operation.
- The `Visualizer` interface + `VizFrame` model + an example module to copy.
- Rendering layer to use (DOM/SVG) and layout rules.
- Requirement: a synced pseudocode block per operation, custom-input support, ≥1 example dataset.
- Constraint: stay within `modules/<slug>/`; don't touch core/shared or other modules.

---

## 9. Recommended decisions

- **Standalone `/visualize` first**, lesson-embedding second (lower risk, immediately useful).
- **Include pseudocode-sync from the MVP** — biggest pedagogical win and cheap if baked into the
  frame model early (`pseudoLine`).
- **No animation library** for Phases 1–3; reconsider for Phase 4 graphs/geometry.
- **Frontend-only** until lesson-embedding requires a registry/link table.

---

## 10. Open questions

- MVP scope: ship pseudocode-sync + custom-input on day one, or animations + controls only first?
- Graph layout: fixed/preset layouts vs a force-directed library (`d3-force`/`elkjs`).
- Do exercises link out to visualizers, or stay separate from the `/visualize` catalog?
