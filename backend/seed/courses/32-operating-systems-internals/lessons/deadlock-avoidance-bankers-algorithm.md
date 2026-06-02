# Deadlock Avoidance and the Banker's Algorithm

While prevention eliminates conditions at design time, **deadlock avoidance** allows more flexibility: the system grants resource requests dynamically, but only when it can prove that doing so leaves the system in a **safe state** — a state from which all processes can eventually finish.

## Safe vs. Unsafe States

- **Safe state:** There exists at least one execution sequence (a *safe sequence*) in which every process can complete, even if they all request their maximum resources.
- **Unsafe state:** No such sequence exists. An unsafe state does not guarantee deadlock, but deadlock is possible; the system no longer has a safety net.
- **Deadlocked state:** A subset of processes are permanently blocked — a special case of unsafe state.

```
Safe ──► Unsafe ──► (possible) Deadlock
```

The avoidance strategy is simple: **never move from safe to unsafe**.

## The Banker's Algorithm (Dijkstra, 1965)

Dijkstra named the algorithm after a banker who grants loans only when the bank can satisfy *every* customer's maximum demand even in the worst case.

### Data Structures

Given *n* processes and *m* resource types:

| Matrix/Vector | Size | Meaning |
|--------------|------|---------|
| `Max[i][j]` | n × m | Max demand of process i for resource j |
| `Allocation[i][j]` | n × m | Resources currently allocated to process i |
| `Need[i][j]` | n × m | `Max[i][j] − Allocation[i][j]` (still needed) |
| `Available[j]` | m | Unallocated instances of resource j |

### Safety Algorithm

```python
def is_safe(available, need, allocation, n, m):
    work = list(available)          # copy of available
    finish = [False] * n

    changed = True
    while changed:
        changed = False
        for i in range(n):
            if finish[i]:
                continue
            # Can process i finish with current 'work'?
            if all(need[i][j] <= work[j] for j in range(m)):
                for j in range(m):
                    work[j] += allocation[i][j]  # it releases resources
                finish[i] = True
                changed = True

    return all(finish)              # safe iff every process can finish
```

### Resource-Request Algorithm

When process P_i requests `Request[i]`:

1. If `Request[i] > Need[i]` → error (exceeds declared maximum).
2. If `Request[i] > Available` → block P_i (resources unavailable).
3. **Pretend to grant**: subtract from `Available`, add to `Allocation[i]`, subtract from `Need[i]`.
4. Run the Safety Algorithm on the new state.
5. If safe → commit the grant. If unsafe → roll back the pretend grant and block P_i.

## Worked Example

3 processes (P0, P1, P2), 2 resource types (A, B). Total: A=10, B=5.

| Process | Max A,B | Alloc A,B | Need A,B |
|---------|---------|-----------|---------|
| P0 | 7, 3 | 0, 1 | 7, 2 |
| P1 | 3, 2 | 2, 0 | 1, 2 |
| P2 | 9, 0 | 3, 0 | 6, 0 |

Available = (10−5, 5−1) = **(5, 4)**

Safety check:
1. P1 needs (1,2) ≤ available (5,4) → P1 finishes, releases (2,0). Available = (7,4).
2. P0 needs (7,2) ≤ (7,4) → P0 finishes, releases (0,1). Available = (7,5).
3. P2 needs (6,0) ≤ (7,5) → P2 finishes.

Safe sequence: **P1 → P0 → P2**. State is safe.

Now P2 requests (1,0):
- Pretend: Available=(4,4), Alloc P2=(4,0), Need P2=(5,0).
- Re-run safety — P1 can go, then P0 can go, then P2 (needs 5,0 ≤ 7,5). Still safe. **Grant.**

## Limitations

- Requires processes to declare **maximum resource needs** upfront — often impractical.
- Computationally **O(n² m)** per request — fine for dozens of processes, impractical at OS kernel scale.
- Does not handle **new processes arriving dynamically** without extensions.
- Most general-purpose OSes skip avoidance; databases and real-time systems are where it sees real use.

## Interview Answer

> "The Banker's Algorithm prevents deadlock by only granting a resource request when a safety algorithm confirms the system can still reach a state where all processes finish. It trades some resource utilization for a deadlock-free guarantee, but requires processes to pre-declare their maximum demands."
