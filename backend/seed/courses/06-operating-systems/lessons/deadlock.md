# Deadlock: Conditions, Detection, and Prevention

A **deadlock** is a situation where a set of processes are each waiting for a resource held by another process in the set — a circular wait from which no process can proceed without external intervention. Deadlocks are silent killers: no error message, no crash — just processes hanging forever, consuming memory but making no progress.

## The Four Coffman Conditions

All four conditions must hold **simultaneously** for a deadlock to exist (Coffman et al., 1971):

| Condition | Meaning | How to Recognize It |
|-----------|---------|---------------------|
| **Mutual exclusion** | Resources are non-shareable — only one process holds it at a time | A database row with an exclusive lock |
| **Hold and wait** | A process holds at least one resource while waiting to acquire more | Thread A holds mutex_1 and blocks on mutex_2 |
| **No preemption** | A resource can only be released voluntarily by its holder | A lock cannot be stolen from a thread |
| **Circular wait** | P1 waits for P2, P2 waits for P3, …, Pn waits for P1 | A ring of dependencies |

Remove **any one** condition and deadlock is impossible. This motivates three strategies: prevention, avoidance, and detection+recovery.

## Classic Example: The Dining Philosophers

Five philosophers sit around a round table. Between each adjacent pair lies one chopstick (five total). Each philosopher alternates between thinking and eating. To eat, a philosopher must hold **both** adjacent chopsticks.

```
      [P0]
  fork4    fork0
[P4]          [P1]
  fork3    fork1
      [P3]-fork2-[P2]
```

If all five philosophers simultaneously pick up their **left** chopstick:
```
P0 holds fork0, waits for fork1 (held by P1)
P1 holds fork1, waits for fork2 (held by P2)
P2 holds fork2, waits for fork3 (held by P3)
P3 holds fork3, waits for fork4 (held by P4)
P4 holds fork4, waits for fork0 (held by P0)
→ Circular wait: DEADLOCK
```

**Correct solutions:**
1. **Asymmetric ordering:** Philosopher 4 picks up fork0 (right) before fork4 (left). This breaks the cycle.
2. **Semaphore limit:** Allow at most 4 philosophers to try simultaneously; at least one will succeed.
3. **Lock ordering:** Always acquire lower-numbered fork first.

## Resource-Allocation Graph (RAG)

The OS can represent resource assignments as a directed bipartite graph:

```
Nodes: circles = processes, squares = resources
Edges:
  P → R : process P is REQUESTING resource R (request edge)
  R → P : resource R is ASSIGNED to process P (assignment edge)
```

**Example — Deadlock:**
```
P1 ──request──► R1
R1 ──assigned──► P2
P2 ──request──► R2
R2 ──assigned──► P3
P3 ──request──► R1

Cycle: P1 → R1 → P2 → R2 → P3 → R1  ← DEADLOCK (single-instance resources)
```

**Example — No Deadlock (multi-instance):**
```
P1 ──request──► R1 (2 instances)
R1 ──instance──► P2
R1 ──instance──► P3
P2 ──request──► R2
R2 ──assigned──► P4
```
Even though R1 has a cycle involving P1, P2, P3 — if P3 can complete (using its current R1 instance) and release, the cycle dissolves. For multi-instance resources, a cycle is necessary but not sufficient for deadlock.

**Key rule:** For single-instance resources, a cycle in the RAG is both necessary and sufficient for deadlock.

## Deadlock Prevention (Eliminate a Coffman Condition)

### 1. Eliminate Circular Wait — Lock Ordering

Assign a global total order to all resources. Require every thread to acquire resources in increasing order.

```python
# Lock IDs: mutex_A < mutex_B
import threading
mutex_A = threading.Lock()   # id=1
mutex_B = threading.Lock()   # id=2

def thread_1():
    with mutex_A:
        with mutex_B:        # always A before B
            do_work()

def thread_2():
    with mutex_A:            # both threads acquire A first
        with mutex_B:
            do_work()
```

If every thread respects the ordering, circular wait cannot form. This is the most practical prevention technique and is widely enforced by code review conventions.

### 2. Eliminate Hold and Wait — Request All at Once

A process must request **all** needed resources before starting. If it cannot get all, it releases what it has and waits.

```
Downside: low resource utilization — a process holds resources it might not need yet.
           Prone to starvation if one resource is perpetually unavailable.
```

### 3. Allow Preemption

If a process holding resources cannot get more, forcibly preempt (take away) the resources it holds and add it to a wait list. Only practical for resources whose state can be saved and restored (CPU registers yes; printer job — no).

### 4. Eliminate Mutual Exclusion — Spooling

For some resources (e.g., printers), only the OS accesses the resource. Processes "print" by writing to a spool queue; the OS serializes actual printer access. The process never directly holds the printer.

## Deadlock Avoidance: The Banker's Algorithm

Dijkstra's **Banker's Algorithm** (1965) dynamically keeps the system in a **safe state** by refusing any resource allocation that could lead to deadlock.

**Safe state definition:** A state is safe if there exists at least one **safe sequence** P1, P2, …, Pn of all processes such that each Pi can be satisfied by:
- Currently available resources, **plus**
- Resources held by all Pj (j < i) that have already finished.

**Algorithm for a resource request by process Pi:**

```
1. Check: Pi's request ≤ its declared maximum need. Else error.
2. Check: request ≤ currently available resources. Else Pi must wait.
3. Pretend to grant the request (update available, allocation, need tables).
4. Run the safety algorithm:
   Work = Available (copy)
   Finish[i] = false for all i
   Loop:
     Find i where Finish[i]=false AND Need[i] ≤ Work
     If found: Work += Allocation[i]; Finish[i] = true
     If no such i found: break
   If all Finish[i] = true → state is SAFE → grant request
   Else → state would be UNSAFE → roll back and make Pi wait
```

**Worked Example:**

```
5 processes (P0–P4), 3 resource types (A, B, C)
Available: A=3, B=3, C=2

          Max     Allocation    Need (Max−Alloc)
P0       7,5,3      0,1,0         7,4,3
P1       3,2,2      2,0,0         1,2,2
P2       9,0,2      3,0,2         6,0,0
P3       2,2,2      2,1,1         0,1,1
P4       4,3,3      0,0,2         4,3,1

Safety check with Available=[3,3,2]:
  P1 needs [1,2,2] ≤ [3,3,2] → run P1; Work=[3+2,3+0,2+0]=[5,3,2]
  P3 needs [0,1,1] ≤ [5,3,2] → run P3; Work=[5+2,3+1,2+1]=[7,4,3]
  P4 needs [4,3,1] ≤ [7,4,3] → run P4; Work=[7+0,4+0,3+2]=[7,4,5]
  P2 needs [6,0,0] ≤ [7,4,5] → run P2; Work=[7+3,4+0,5+2]=[10,4,7]
  P0 needs [7,4,3] ≤ [10,4,7] → run P0
  Safe sequence: P1→P3→P4→P2→P0  ✓ SAFE STATE
```

**Limitations of the Banker's Algorithm:**
- Requires knowing each process's **maximum resource need** in advance — impractical for general-purpose OSes.
- Assumes a fixed number of processes (no dynamic process creation).
- Overhead: O(n²r) per allocation request (n = processes, r = resource types).
- Used in specialized real-time systems; not in Linux or Windows.

## Deadlock Detection and Recovery

Many general-purpose OSes (Linux, Windows) take the pragmatic approach: **ignore deadlock for user processes**. This is sometimes called the **ostrich algorithm** — if deadlocks are rare and the cost of prevention/avoidance is high, just let them happen.

**Detection:** Run cycle-detection on the wait-for graph (simplified RAG: only processes, edge P→Q means "P is waiting for something held by Q").

```python
def detect_deadlock(wait_for):
    """
    wait_for: dict mapping process_id → list of process_ids it waits for
    Returns True if a deadlock (cycle) exists.
    """
    visited, in_stack = set(), set()

    def dfs(node):
        visited.add(node)
        in_stack.add(node)
        for neighbor in wait_for.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in in_stack:
                return True
        in_stack.remove(node)
        return False

    return any(dfs(n) for n in wait_for if n not in visited)

# Example
wait_for = {1: [2], 2: [3], 3: [1]}   # cycle: 1→2→3→1
print(detect_deadlock(wait_for))       # True
```

**Recovery options:**
1. **Process termination:** Kill one or more deadlocked processes (cheapest, most common).
2. **Resource preemption:** Forcibly take a resource from a process, save its state, and resume later.
3. **Rollback:** Checkpoint processes periodically; roll back deadlocked ones to a safe state (database-style recovery).

## Livelock and Starvation

Closely related but distinct problems:

| Problem | State | Progress | Example |
|---------|-------|----------|---------|
| **Deadlock** | All blocked | None | Two threads each hold one mutex and wait for the other |
| **Livelock** | Active (keeps changing state) | None | Two people in a corridor each step aside the same direction, forever |
| **Starvation** | Some blocked, others running | Some | High-priority thread always preempts a low-priority one |

**Livelock example:** Two processes each detect the other has what they need, release their resource, wait a random backoff, then re-acquire. If their backoffs are correlated, they release and re-acquire in lockstep forever. Ethernet's CSMA/CD used exponential random backoff to avoid livelock.

## Real-World Deadlock Examples

- **Database:** Two transactions T1 and T2 each hold a row lock and try to acquire each other's lock. DBMSes detect this with a timeout or cycle detection and kill one transaction (the "victim").
- **Linux kernel spinlocks:** Acquiring two spinlocks in different orders in different kernel paths can deadlock the kernel. The `lockdep` tool (enabled via `CONFIG_DEBUG_LOCKDEP`) tracks every lock acquisition order and detects potential circular dependencies at runtime.
- **Java:** `synchronized` blocks in the wrong order — a common interview question and a real production bug.

## Key Takeaways

- Deadlock requires all four Coffman conditions simultaneously: mutual exclusion, hold-and-wait, no preemption, and circular wait.
- The **resource-allocation graph** makes deadlocks visual; a cycle in a single-instance graph guarantees deadlock.
- **Prevention** eliminates one condition permanently (lock ordering is the most practical).
- **Avoidance** (Banker's Algorithm) keeps the system in a safe state but requires advance knowledge of needs.
- **Detection + recovery** lets deadlocks happen and breaks them (kill a process or rollback).
- Most production OSes use **lock ordering + timeouts** rather than the Banker's algorithm.
- **Livelock** is active but non-progressive; **starvation** bypasses a specific process indefinitely.
