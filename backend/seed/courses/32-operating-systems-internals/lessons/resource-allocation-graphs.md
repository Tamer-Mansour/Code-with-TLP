# Resource Allocation Graphs and Cycles

A **Resource Allocation Graph (RAG)** is the standard visual and formal tool used by operating systems researchers and practitioners to reason about deadlock. It converts the abstract question "is there a deadlock?" into a concrete graph problem: "does this graph contain a cycle?"

## Graph Anatomy

A RAG is a directed bipartite graph with two types of nodes:

| Node Type | Symbol | Represents |
|-----------|--------|------------|
| **Process** | Circle `○` | A running (or blocked) process |
| **Resource** | Rectangle `□` | A resource type; dots inside show instances |

Two types of directed edges connect them:

- **Request edge** `P → R` — Process P is *waiting* for an instance of resource R.
- **Assignment edge** `R → P` — An instance of resource R is *held by* process P.

```
P1 ──request──► R1 ◄──assignment── P2
               │
          (1 instance)
```

## Single-Instance Resources: Cycles = Deadlock

When every resource type has exactly one instance, a cycle in the RAG is **both necessary and sufficient** for deadlock.

```
P1 ──► R1 ──► P2 ──► R2 ──► P1
```

Read this as:
- P1 holds R2 and waits for R1.
- P2 holds R1 and waits for R2.

This is a deadlock. Neither process can ever proceed.

## Multi-Instance Resources: Cycles Are Necessary but Not Sufficient

When a resource type has multiple instances, a cycle indicates a *possible* deadlock, not a guaranteed one. You must apply further analysis (e.g., the Banker's Algorithm or reachability analysis).

**Example — cycle without deadlock:**

```
P1 ──► R1 ──► P3
P2 ──► R1
R1 ──► P2     (R1 has 2 instances)
```

P3 is not waiting for anything; when it finishes it releases its instance of R1, unblocking P1 or P2. No deadlock despite the apparent cycle.

## Wait-For Graph (WFG)

For single-instance resources, the RAG simplifies to a **Wait-For Graph**: collapse each resource node and draw a direct edge P_i → P_j whenever P_i is waiting for a resource held by P_j. Deadlock detection then reduces to cycle detection in a directed graph — tractable with DFS in O(V + E).

```python
# DFS-based cycle detection in a wait-for graph
def has_cycle(adj: dict[int, list[int]]) -> bool:
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {v: WHITE for v in adj}

    def dfs(u):
        color[u] = GRAY
        for v in adj.get(u, []):
            if color[v] == GRAY:   # back edge → cycle
                return True
            if color[v] == WHITE and dfs(v):
                return True
        color[u] = BLACK
        return False

    return any(dfs(v) for v in adj if color[v] == WHITE)
```

## Worked Example

Processes: P1, P2, P3. Resources: R1 (1 instance), R2 (1 instance).

| Event | Edge added |
|-------|-----------|
| P1 acquires R1 | R1 → P1 |
| P2 acquires R2 | R2 → P2 |
| P1 requests R2 | P1 → R2 |
| P2 requests R1 | P2 → R1 |

RAG cycle: `P1 → R2 → P2 → R1 → P1`. Deadlock confirmed.

## Key Takeaways

- RAGs make deadlock analysis visual and algorithmic.
- For single-instance resources, cycle = deadlock (use DFS to detect).
- For multi-instance resources, a cycle is a warning sign that requires deeper analysis.
- Operating systems that perform runtime deadlock detection (e.g., database lock managers) maintain a WFG and run cycle detection periodically or after each lock operation.

## Interview Answer

> "A Resource Allocation Graph models processes and resources as nodes with request and assignment edges. For single-instance resources, a cycle in the RAG is both necessary and sufficient for deadlock. For multi-instance resources, a cycle is necessary but not sufficient."
