# Deadlock Prevention: Breaking the Four Conditions

Deadlock prevention is the most conservative strategy: design the system so at least one of the four Coffman conditions can *never* hold. The trade-off is reduced concurrency or increased complexity, but the payoff is a system that provably cannot deadlock.

## Strategy 1 — Eliminate Mutual Exclusion

Make resources shareable. Read-only data, immutable objects, and lock-free data structures need no mutual exclusion and therefore cannot participate in a deadlock.

- Replace mutex-protected counters with **atomic operations** (`std::atomic<int>`).
- Use **copy-on-write** (COW) for shared data that is read far more often than written.
- Use **reader-writer locks** so concurrent reads never block each other.

**Limitation:** Some resources are inherently non-shareable (a printer, a serial port). You cannot eliminate mutual exclusion for them.

## Strategy 2 — Eliminate Hold and Wait

Force every process to either:

**Option A — Request all resources at once (static allocation):**

```c
// Acquire BOTH locks before entering the critical section
pthread_mutex_lock(&A);
pthread_mutex_lock(&B);
/* work */
pthread_mutex_unlock(&B);
pthread_mutex_unlock(&A);
// If you can't get B, you don't enter at all — atomically request both
```

In practice this is implemented with a "try-lock all or release all" loop, or by a resource manager that grants the full set atomically.

**Option B — Release before requesting:**

A process gives up all currently held resources before requesting new ones, then re-acquires everything it needs.

**Pitfall:** Both options can cause **starvation** (a process that needs many popular resources may wait forever) and reduce throughput (resources sit idle while a process waits to collect the full set).

## Strategy 3 — Allow Preemption

If a process holding resources requests another that is not available, the OS forcibly reclaims the held resources, saves state, and retries later.

- Works well for resources whose state can be saved/restored: **CPU registers**, **memory pages** (swap out), **GPU contexts**.
- Works poorly for resources that cannot be rolled back: **printed pages**, **database write locks** (partial writes corrupt state).

```
P1 holds: {printer, file_lock}
P1 requests: network_socket (unavailable)
OS preempts: takes printer and file_lock from P1,
             grants them to P2, resumes P2.
P1 is rolled back and will retry later.
```

## Strategy 4 — Eliminate Circular Wait (Resource Ordering)

Assign every resource a unique integer priority. Require all processes to request resources in **strictly increasing order of their priority numbers**.

```cpp
// Resource IDs:  mutex_A=1, mutex_B=2, mutex_C=3
// RULE: always lock in ascending ID order

void safe_operation() {
    std::lock_guard<std::mutex> lk1(mutex_A);  // ID 1 first
    std::lock_guard<std::mutex> lk2(mutex_B);  // ID 2 second
    std::lock_guard<std::mutex> lk3(mutex_C);  // ID 3 third
}
```

**Why it works:** If every process acquires in the same order, a cycle is topologically impossible — no process can be "behind" another in the chain and also "ahead" of it.

**C++ shortcut — `std::lock`:** Acquires multiple locks simultaneously without deadlock, regardless of order, using a backoff/retry strategy:

```cpp
std::lock(mutex_A, mutex_B);
std::lock_guard<std::mutex> lk1(mutex_A, std::adopt_lock);
std::lock_guard<std::mutex> lk2(mutex_B, std::adopt_lock);
```

## Comparison

| Strategy | Condition Broken | Real-World Use |
|----------|-----------------|---------------|
| Shareable resources | Mutual exclusion | Lock-free structures, read locks |
| Atomic request / release-before-request | Hold and wait | Database transaction managers |
| Forced preemption | No preemption | CPU scheduling, virtual memory |
| Resource ordering | Circular wait | Kernel lock hierarchies, pthreads |

## Common Pitfall

Resource ordering only prevents deadlock if the ordering is **global and enforced everywhere**. A single code path that acquires in the wrong order breaks the guarantee. Linux kernel developers maintain documented lock-ordering rules for exactly this reason.

## Interview Answer

> "Deadlock prevention eliminates one of the four Coffman conditions at design time. The most practical strategy is resource ordering — require all threads to acquire locks in a globally fixed sequence, making circular wait impossible."
