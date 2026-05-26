# BFS, DFS, and A* Search

Three algorithms cover the vast majority of classical search problems. Understanding their trade-offs — completeness, optimality, time, and memory — is a core AI skill. This lesson works through each with concrete examples and numbers.

## Breadth-First Search (BFS)

BFS explores level by level: all states reachable in 1 step, then all reachable in 2 steps, and so on. It uses a **FIFO queue** for the frontier.

```python
from collections import deque

def bfs(start, goal, neighbors):
    frontier = deque([(start, [start])])
    visited = {start}
    while frontier:
        state, path = frontier.popleft()
        if state == goal:
            return path
        for child in neighbors(state):
            if child not in visited:
                visited.add(child)
                frontier.append((child, path + [child]))
    return None  # no path found
```

| Property | BFS result |
|---|---|
| Complete? | Yes (finite branching factor) |
| Optimal? | Yes, when all step costs are equal |
| Time complexity | O(b^d) |
| Space complexity | O(b^d) — stores the entire frontier |

Where `b` = branching factor, `d` = depth of shallowest goal.

**Memory is BFS's Achilles heel.** If b=10 and d=10, the frontier holds up to 10^10 = 10 billion nodes. At 1 KB per node: 10 TB. Impractical for deep problems.

### Worked Example

Graph (undirected): 0–1, 1–2, 2–3, 0–3. Source=0, Goal=3.

BFS queue evolution:
- Initial: `[0]`, visited: `{0}`
- Pop 0, expand neighbors {1, 3}: queue `[(1, [0,1]), (3, [0,3])]`, visited `{0,1,3}`
- Pop 1, its neighbor 0 is visited, neighbor 2 is new: queue `[(3, [0,3]), (2, [0,1,2])]`
- Pop 3 — **goal found!** Path: 0→3, length 1.

BFS returns the shallowest (fewest edges) path: direct edge 0→3 with length 1.

## Depth-First Search (DFS)

DFS dives as deep as possible before backtracking. It uses a **LIFO stack** — or equivalently, recursion.

| Property | DFS result |
|---|---|
| Complete? | No — can loop forever in graphs with cycles (unless cycle detection is used) |
| Optimal? | No — finds *a* solution, not necessarily the shortest |
| Time complexity | O(b^m) where m = max search depth |
| Space complexity | O(b·m) — stores only the current path |

DFS's great virtue is **memory efficiency**: it only stores the path from root to the current node plus the unexplored siblings at each level. Where BFS uses O(b^d) memory, DFS uses only O(b·m) — linear in depth rather than exponential.

DFS is appropriate when: any solution (not the best) is acceptable, or when the search space is very deep and BFS's memory requirement is prohibitive.

## Heuristics: The Key to Informed Search

An **admissible heuristic** `h(n)` estimates the cost from state `n` to the nearest goal and **never overestimates** the true cost. If the true remaining cost is 10, h(n) must be ≤ 10.

Classic admissible heuristics:

- **8-puzzle, misplaced tiles**: count tiles not in their goal position. If 5 tiles are out of place, at least 5 moves are needed. Never an overestimate (each move can fix at most one tile). Value for the initial state shown in the state-space lesson: 5 tiles misplaced → h = 5.
- **8-puzzle, Manhattan distance**: sum of |row_current − row_goal| + |col_current − col_goal| for each tile. Tile 2 is at (0,0) but should be at (0,1): distance = 1. This heuristic is tighter (closer to true cost) than misplaced tiles, so A* expands fewer nodes.
- **Route planning, straight-line distance**: actual road distance ≥ straight-line distance (Euclidean) between cities. This is always admissible because roads cannot be shorter than a straight line.

A heuristic that is both admissible and **consistent** (a.k.a. monotone) satisfies:
```
h(n) ≤ cost(n, n') + h(n')
```
for every successor n' of n with action cost cost(n, n'). Consistency guarantees A* never re-opens a node, simplifying the implementation.

## A* Search

A* combines the actual path cost `g(n)` (exact cost from start to n) with the heuristic estimate `h(n)` (estimated cost from n to goal):

```
f(n) = g(n) + h(n)
```

Nodes are expanded in order of lowest `f`. A* uses a **priority queue** (min-heap).

```python
import heapq

def astar(start, goal, neighbors_with_cost, heuristic):
    # frontier entries: (f, g, state, path)
    frontier = [(heuristic(start), 0, start, [start])]
    best_g = {start: 0}
    while frontier:
        f, g, state, path = heapq.heappop(frontier)
        if state == goal:
            return path, g
        if g > best_g.get(state, float('inf')):
            continue  # stale entry
        for child, step_cost in neighbors_with_cost(state):
            new_g = g + step_cost
            if new_g < best_g.get(child, float('inf')):
                best_g[child] = new_g
                f_val = new_g + heuristic(child)
                heapq.heappush(frontier, (f_val, new_g, child, path + [child]))
    return None, float('inf')
```

| Property | A* (admissible h) |
|---|---|
| Complete? | Yes |
| Optimal? | Yes — guaranteed with admissible heuristic |
| Time complexity | O(b^d) worst case, exponentially better with tight heuristic |
| Space complexity | O(b^d) — stores frontier |

### A* Worked Example (Step-by-Step Table)

Grid with step costs (each cell is a node, moves cost the edge weight shown):

```
Start(A) --2--> B --3--> Goal(D)
    |                    ^
    1                    |
    v                    |
    C   ------4---------/
```

Heuristic values (straight-line estimate to D): h(A)=5, h(B)=3, h(C)=4, h(D)=0.

| Step | Pop | g(n) | h(n) | f(n) | Frontier after |
|---|---|---|---|---|---|
| 1 | A (start) | 0 | 5 | 5 | B: f=0+2+3=5, C: f=0+1+4=5 |
| 2 | B (f=5) | 2 | 3 | 5 | C: f=5, D via B: f=2+3+0=5 |
| 3 | D via B (f=5) | 5 | 0 | 5 | **Goal!** Path: A→B→D, cost=5 |

Note: A→C→D would cost 1+4=5 — also optimal. A* finds one of the optimal paths.

For comparison, without the heuristic (Dijkstra), we might expand C before D. The heuristic steered A* away from exploring C first.

## Comparison: When to Use Which

| Situation | Best algorithm | Why |
|---|---|---|
| Small graph, unit costs | BFS | Simple, finds shortest path |
| Any solution, deep/memory-tight | DFS | O(b·m) memory |
| Varying costs, no heuristic | Dijkstra (uniform-cost search) | Expands by cheapest path cost |
| Varying costs + good heuristic | A* | Fewer expansions than Dijkstra |
| Very large state space (games) | MCTS or IDA* | Bounded memory, anytime results |

**IDA*** (Iterative Deepening A*) combines A*'s optimality with DFS's memory footprint: it runs depth-first search with an f-value cutoff, increasing the cutoff each iteration. It uses O(b·d) memory — crucial for puzzles like the 15-puzzle (24.6 billion reachable states).

## Heuristic Quality Matters Enormously

The **effective branching factor** b* measures how many nodes A* expands compared to the theoretical minimum. A perfect heuristic (h(n) = true remaining cost) means b* = 1 — A* expands only the nodes on the optimal path.

For the 8-puzzle:
- No heuristic (BFS): expands ~181,000 nodes on average.
- Misplaced tiles: expands ~13,000 nodes.
- Manhattan distance: expands ~400 nodes.

Better heuristics compress the search by orders of magnitude. This is why domain knowledge (encoding it in h) pays off so dramatically.
