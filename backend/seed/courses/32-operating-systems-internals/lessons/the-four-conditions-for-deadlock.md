# The Four Necessary Conditions for Deadlock

Deadlock is one of the most notorious concurrency bugs: a set of processes each holds a resource while waiting for another, and none can ever make progress. Before you can prevent or detect deadlock, you must understand *why* it happens. In 1971, Coffman et al. identified four conditions that must **all** hold simultaneously for a deadlock to exist. Remove any one and deadlock becomes impossible.

## The Four Conditions

| # | Condition | Plain-English Meaning |
|---|-----------|----------------------|
| 1 | **Mutual Exclusion** | At least one resource can be held by only one process at a time. |
| 2 | **Hold and Wait** | A process holding a resource can request additional resources without releasing what it already holds. |
| 3 | **No Preemption** | Resources cannot be forcibly taken away; a process releases them voluntarily. |
| 4 | **Circular Wait** | A closed chain of processes exists, each waiting for a resource held by the next. |

### 1. Mutual Exclusion

Non-shareable resources (e.g., a printer, a mutex-protected data structure) enforce mutual exclusion by definition. Read-only resources (e.g., a file opened for reading) do **not** satisfy this condition, which is why concurrent reads never deadlock.

### 2. Hold and Wait

A process that has locked `mutex_A` then blocks waiting for `mutex_B` is demonstrating hold-and-wait. The dangerous pattern looks like:

```cpp
std::mutex A, B;

void thread1() {
    A.lock();           // holds A
    B.lock();           // waits for B — hold and wait!
    /* critical section */
    B.unlock();
    A.unlock();
}

void thread2() {
    B.lock();           // holds B
    A.lock();           // waits for A — hold and wait!
    /* critical section */
    A.unlock();
    B.unlock();
}
```

Thread 1 holds A and waits for B; Thread 2 holds B and waits for A. Together they satisfy all four conditions.

### 3. No Preemption

The OS cannot silently revoke a mutex from one thread and hand it to another — doing so would corrupt shared state. This is what makes mutexes fundamentally different from CPU time slices, which *can* be preempted by the scheduler.

### 4. Circular Wait

Circular wait formalises the cycle. With two processes:

```
P1 → waiting for resource held by P2
P2 → waiting for resource held by P1
```

With *n* processes the chain just grows longer. Circular wait is the condition most amenable to prevention through resource-ordering disciplines.

## Why All Four Must Hold

The conditions are **jointly necessary**: any single condition absent breaks the cycle. For example:

- If resources are **shareable** (no mutual exclusion), multiple processes can use them concurrently — no conflict, no deadlock.
- If processes **release everything before requesting more** (no hold-and-wait), no cycle can form.
- If the OS **can preempt** a resource, it can break any would-be cycle.
- If processes **always request resources in a global order** (no circular wait), a cycle is topologically impossible.

## Common Pitfalls

- **Forgetting lock ordering** is the most common real-world deadlock cause. Even in large codebases one inconsistency is enough.
- **Lock inversion** in callbacks: a library holds lock L and calls your callback, which tries to acquire L again from a different code path.
- **Deadlock ≠ starvation**. Starvation is indefinite postponement with *theoretical* progress possible; in deadlock, *no* progress is possible.

## Interview Answer

> "Deadlock requires four conditions simultaneously: mutual exclusion, hold-and-wait, no preemption, and circular wait. Eliminating any one of the four prevents deadlock entirely."
