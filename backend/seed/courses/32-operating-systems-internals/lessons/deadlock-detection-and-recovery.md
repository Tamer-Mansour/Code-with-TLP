# Deadlock Detection and Recovery

When prevention and avoidance are too costly or too restrictive, the OS can take a more optimistic approach: **let deadlocks happen, detect them, and recover**. This is the strategy used by most general-purpose operating systems (including Linux and Windows) and by database lock managers.

## The Detection Philosophy

Rather than restricting how resources are requested, the system:
1. Grants all requests immediately (subject to availability).
2. Periodically runs a **detection algorithm** to check for deadlock.
3. On detection, applies a **recovery action** to break the deadlock.

The trade-off: some wasted work and possible rollback, but better resource utilization and simpler code than prevention/avoidance.

## Detection Algorithm — Single-Instance Resources

Maintain a **Wait-For Graph (WFG)**: each edge P_i → P_j means P_i is waiting for a resource held by P_j. Run DFS to detect a cycle.

```python
def detect_deadlock_wfg(wait_for: dict[int, list[int]]) -> list[int]:
    """Returns a cycle (list of process IDs) if deadlock exists, else []."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {v: WHITE for v in wait_for}
    parent = {}
    cycle = []

    def dfs(u):
        color[u] = GRAY
        for v in wait_for.get(u, []):
            if color[v] == GRAY:          # back edge found
                # reconstruct cycle
                path = [v, u]
                cur = u
                while parent.get(cur) != v:
                    cur = parent[cur]
                    path.append(cur)
                cycle.extend(path)
                return True
            if color[v] == WHITE:
                parent[v] = u
                if dfs(v):
                    return True
        color[u] = BLACK
        return False

    for node in list(wait_for):
        if color[node] == WHITE:
            if dfs(node):
                break
    return cycle
```

Time complexity: **O(V + E)** — efficient enough to run continuously in database systems.

## Detection Algorithm — Multi-Instance Resources

The multi-instance version mirrors the Banker's Algorithm's safety check but without the pre-declared maximum demand requirement.

```python
def detect_deadlock_multi(available, allocation, request, n, m):
    """
    Returns list of deadlocked process indices.
    request[i][j] = current pending request of process i for resource j.
    """
    work = list(available)
    finish = [sum(allocation[i]) == 0 for i in range(n)]  # no allocation → assume done

    changed = True
    while changed:
        changed = False
        for i in range(n):
            if finish[i]:
                continue
            if all(request[i][j] <= work[j] for j in range(m)):
                work = [work[j] + allocation[i][j] for j in range(m)]
                finish[i] = True
                changed = True

    return [i for i in range(n) if not finish[i]]  # deadlocked processes
```

Processes that cannot finish are deadlocked. Time complexity: **O(n² m)**.

## When to Run Detection

| Frequency | Pros | Cons |
|-----------|------|------|
| After every request | Catches deadlock immediately | High CPU overhead |
| Periodically (e.g., every 30 s) | Low overhead | Deadlock may persist for seconds |
| When CPU utilization drops | Heuristic trigger | May miss deadlock if CPU stays busy |

Database systems typically detect after every lock acquisition; OSes typically use periodic polling or manual triggering.

## Recovery Strategies

Once a deadlock is detected, the system must break it. Options:

### 1. Process Termination

- **Abort all deadlocked processes** — brutal but simple. Guaranteed to work.
- **Abort one at a time** — terminate the cheapest process, re-run detection, repeat until deadlock is resolved.

Selection criteria (minimal cost heuristic):
- Lowest priority
- Least CPU time consumed
- Least resources held
- Fewest processes would be affected

### 2. Resource Preemption

Select a victim, roll back its state, reclaim its resources, and restart it from a safe checkpoint.

Challenges:
- **Checkpoint overhead** — applications must support rollback.
- **Starvation** — the same process keeps being chosen as the victim. Fix: include "number of times preempted" in the cost function.

## Real-World Examples

- **PostgreSQL / MySQL InnoDB:** Run deadlock detection continuously on the lock graph; abort the transaction with the smallest rollback cost.
- **Linux kernel:** Provides `lockdep` — a runtime validator that tracks lock acquisition order and reports circular-wait patterns *before* they deadlock in production.
- **Windows:** Application-level deadlocks are not auto-detected; developers use tools like WinDbg `!locks` or Event Tracing for Windows.

## Interview Answer

> "Deadlock detection lets deadlocks form, then periodically checks for cycles in the Wait-For Graph (or runs a Banker-style reachability analysis for multi-instance resources). Recovery either terminates victim processes or rolls them back to a checkpoint, breaking the cycle at the cost of some wasted work."
