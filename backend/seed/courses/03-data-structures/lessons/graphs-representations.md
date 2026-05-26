# Graphs — Representations & Traversals

A **graph** G = (V, E) is a set of **vertices** (nodes) V and a set of **edges** E — each edge connecting a pair of vertices. Graphs model the real world in ways no other structure can: road networks, social relationships, dependency chains, electrical circuits, and the web are all graphs.

## Graph Taxonomy

| Property            | Values                                   | Example                          |
|---------------------|------------------------------------------|----------------------------------|
| Directionality      | Undirected / Directed (digraph)          | Road ↔ vs. one-way street →      |
| Edge weight         | Unweighted / Weighted                    | Hop count vs. distance in km     |
| Cycles              | Cyclic / Acyclic (DAG)                   | Social network vs. build deps    |
| Connectivity        | Connected / Disconnected                 | Single island vs. archipelago    |
| Density             | Sparse (E ≪ V²) / Dense (E ≈ V²)        | Internet vs. complete tournament |

**Directed Acyclic Graph (DAG):** A directed graph with no cycles. Used for dependency resolution (build systems, package managers), course prerequisites, and topological ordering.

## Representation 1 — Adjacency List

Store an array (or dict) of neighbour lists. The most common representation.

```python
# Undirected graph with 5 vertices and 5 edges
adj = {
    0: [1, 2],
    1: [0, 3],
    2: [0, 3, 4],
    3: [1, 2],
    4: [2],
}

# Or as a list of lists (vertices are 0-indexed integers)
V = 5
adj_list = [[] for _ in range(V)]
edges = [(0,1),(0,2),(1,3),(2,3),(2,4)]
for u, v in edges:
    adj_list[u].append(v)
    adj_list[v].append(u)   # undirected: add both directions
```

| Operation              | Time              |
|------------------------|-------------------|
| Space                  | O(V + E)          |
| Add vertex             | O(1)              |
| Add edge               | O(1)              |
| Check edge (u, v)      | O(degree(u))      |
| Iterate neighbours(u)  | O(degree(u))      |
| Iterate all edges      | O(V + E)          |

**Best for:** sparse graphs (E ≪ V²), memory-constrained settings, iterating over neighbours.

## Representation 2 — Adjacency Matrix

A V×V boolean (or weight) matrix. `matrix[u][v]` is True if edge (u, v) exists.

```python
V = 5
matrix = [[0] * V for _ in range(V)]

for u, v in [(0,1),(0,2),(1,3),(2,3),(2,4)]:
    matrix[u][v] = 1
    matrix[v][u] = 1   # undirected

# Check if edge exists: O(1)
print(matrix[0][1])   # 1 (edge exists)
print(matrix[0][3])   # 0 (no direct edge)
```

| Operation              | Time   |
|------------------------|--------|
| Space                  | O(V²)  |
| Add vertex             | O(V)   |
| Add edge               | O(1)   |
| Check edge (u, v)      | O(1)   |
| Iterate neighbours(u)  | O(V)   |
| Iterate all edges      | O(V²)  |

**Best for:** dense graphs (E ≈ V²), frequent edge-existence queries (e.g., Floyd-Warshall all-pairs shortest path).

## Representation 3 — Edge List

A flat list of `(u, v)` pairs (or `(u, v, weight)` triples). Simple but slow for neighbourhood queries.

```python
edges = [(0,1,3), (0,2,1), (1,3,4), (2,3,2), (2,4,5)]  # (u, v, weight)
```

**Best for:** Kruskal's MST (sort all edges by weight), when you only need to process each edge once.

## Representation Trade-offs Table

| Aspect                     | Adj List       | Adj Matrix      | Edge List   |
|----------------------------|----------------|-----------------|-------------|
| Space                      | O(V + E)       | O(V²)           | O(E)        |
| Edge existence check       | O(degree)      | O(1)            | O(E)        |
| Iterate neighbours of u    | O(degree)      | O(V)            | O(E)        |
| Add edge                   | O(1)           | O(1)            | O(1)        |
| Remove edge                | O(degree)      | O(1)            | O(E)        |
| Good for sparse?           | Yes            | No (wastes V²)  | Yes         |
| Good for dense?            | Okay           | Yes             | Okay        |

For most problems use an **adjacency list**. Switch to a matrix when V ≤ 1000 and you need O(1) edge checks, or when implementing Floyd-Warshall.

## BFS — Breadth-First Search

BFS explores all vertices at distance d from the source before exploring distance d+1. It uses a **queue** and marks nodes visited immediately on enqueue (not dequeue) to prevent duplicates.

```python
from collections import deque

def bfs(adj, start: int, V: int) -> list:
    dist = [-1] * V
    dist[start] = 0
    q = deque([start])
    while q:
        node = q.popleft()
        for nb in adj[node]:
            if dist[nb] == -1:        # unvisited
                dist[nb] = dist[node] + 1
                q.append(nb)
    return dist
```

**Why mark on enqueue?** If you mark on dequeue, a node could be enqueued multiple times (O(E) times in dense graphs), making BFS O(V·E) instead of O(V + E).

### BFS Applications

- **Shortest path in unweighted graph:** `dist[v]` gives the minimum number of hops.
- **Level-order traversal of trees:** Visit all nodes depth by depth.
- **Connected components:** Run BFS from every unvisited vertex; count how many times you start a new BFS.
- **Bipartite check:** Try to 2-colour the graph (BFS assigns colours; check for conflicts).

## DFS — Depth-First Search

DFS explores as deep as possible along each branch before backtracking. Uses recursion (implicit stack) or an explicit stack.

```python
def dfs_recursive(adj, node: int, visited: set, order: list) -> None:
    visited.add(node)
    order.append(node)
    for nb in adj[node]:
        if nb not in visited:
            dfs_recursive(adj, nb, visited, order)

def dfs_iterative(adj, start: int, V: int) -> list:
    visited = [False] * V
    stack = [start]
    order = []
    while stack:
        node = stack.pop()
        if not visited[node]:
            visited[node] = True
            order.append(node)
            for nb in reversed(adj[node]):   # reversed to match recursive order
                if not visited[nb]:
                    stack.append(nb)
    return order
```

### DFS Applications

- **Cycle detection in undirected graphs:** If DFS encounters an already-visited neighbour that is not the direct parent, a cycle exists.
- **Cycle detection in directed graphs (DAG check):** Use three states (white=unvisited, grey=in stack, black=done). Grey→grey edge = cycle.
- **Topological sort:** DFS post-order, reversed. Valid only on DAGs.
- **Strongly connected components (Tarjan's / Kosaraju's):** Two-pass DFS.
- **Flood fill / connected region discovery** (e.g., paint bucket tool).

## Cycle Detection in Undirected Graphs

Using DFS: track the parent of each node. If we visit a neighbour that's already visited and is NOT our parent, we found a cycle.

```python
def has_cycle_undirected(adj, V: int) -> bool:
    visited = [False] * V

    def dfs(node, parent):
        visited[node] = True
        for nb in adj[node]:
            if not visited[nb]:
                if dfs(nb, node):
                    return True
            elif nb != parent:   # visited and not our parent → cycle!
                return True
        return False

    for v in range(V):
        if not visited[v]:
            if dfs(v, -1):
                return True
    return False
```

Using Union-Find (covered in the Tries & Union-Find lesson) is cleaner for this specific problem.

## Topological Sort (Kahn's Algorithm — BFS-based)

Given a DAG, order vertices so every directed edge goes from earlier to later.

```python
from collections import deque

def topological_sort(adj, V: int) -> list:
    """Kahn's algorithm — O(V + E)."""
    in_degree = [0] * V
    for u in range(V):
        for v in adj[u]:
            in_degree[v] += 1

    q = deque(v for v in range(V) if in_degree[v] == 0)
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                q.append(v)

    if len(order) != V:
        raise ValueError("Graph has a cycle — topological sort impossible")
    return order
```

## BFS vs. DFS: When to Use Which

| Goal                              | Use     | Reason                                       |
|-----------------------------------|---------|----------------------------------------------|
| Shortest path (unweighted)        | BFS     | Explores by increasing distance              |
| Detect cycle                      | Either  | DFS simpler; Union-Find for undirected       |
| Topological sort                  | DFS/BFS | Kahn's is BFS; post-order DFS also works     |
| Find any connected component      | Either  |                                              |
| Determine reachability            | Either  |                                              |
| Strongly connected components     | DFS     | Tarjan's / Kosaraju's use DFS                |
| Flood fill / region counting      | Either  | DFS often simpler to code                    |
| Level-by-level processing         | BFS     | Natural level structure                      |

## Complexity Summary

| Algorithm           | Time     | Space | Notes                           |
|---------------------|----------|-------|---------------------------------|
| BFS                 | O(V + E) | O(V)  | Queue + visited array           |
| DFS                 | O(V + E) | O(V)  | Stack (call stack or explicit)  |
| Topological sort    | O(V + E) | O(V)  | Kahn's algorithm                |
| Cycle detection     | O(V + E) | O(V)  | DFS or Union-Find               |

Both BFS and DFS visit each vertex and each edge exactly once, giving O(V + E).

## Common Bugs in Graph Problems

1. **Not checking visited before enqueue/push** — leads to processing the same node multiple times.
2. **Forgetting disconnected components** — always loop over all vertices if the graph may be disconnected.
3. **Directedness errors** — adding edge `u→v` but forgetting `v→u` for undirected graphs (or vice versa for directed).
4. **0-indexed vs. 1-indexed vertices** — read the problem carefully; adjust your array sizes accordingly.
