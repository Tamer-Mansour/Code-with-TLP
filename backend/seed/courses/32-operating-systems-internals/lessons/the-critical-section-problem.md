# The Critical Section Problem

A **critical section** is any segment of code that accesses shared resources — memory, files, hardware registers — and must not be executed by more than one thread (or process) at a time. The **critical-section problem** is the challenge of designing a protocol that threads can use to coordinate access so that only one enters the critical section at any given moment.

Every solution to the critical-section problem must satisfy three properties (detailed in the next lesson). Understanding *what* a critical section is — and how to identify one — is the first step.

## Structure of a Thread's Execution

Textbooks describe each thread's execution in four phases:

```
+-------------------+
|   Entry section   |  ← Request permission to enter
+-------------------+
|  Critical section |  ← Access shared resource
+-------------------+
|   Exit section    |  ← Signal that you're leaving
+-------------------+
|  Remainder section|  ← All other (non-critical) work
+-------------------+
```

The entry and exit sections together form the **synchronization overhead**. Ideally, a thread spends as little time as possible inside the critical section.

## Identifying a Critical Section

A section of code is critical if:

- It reads **and** another concurrent path writes to the same memory location, OR
- It performs a **non-atomic read-modify-write** on shared data, OR
- It depends on an invariant that spans multiple fields (e.g., a linked-list head pointer and a node count that must remain consistent together).

```c
// Example: a bank transfer — this spans two accounts, so BOTH updates
// must be inside one critical section to preserve the invariant
// total_balance = account_a + account_b
void transfer(int amount) {
    account_a -= amount;   // shared write
    account_b += amount;   // shared write
}
// If another thread reads account_a or account_b between the two lines,
// it sees an inconsistent "phantom" total.
```

## A Minimal Broken Attempt

The simplest (wrong) idea is to use a flag:

```c
int busy = 0;   // 0 = free, 1 = locked

void enter_critical() {
    while (busy);   // spin-wait
    busy = 1;       // set flag
}

void leave_critical() {
    busy = 0;
}
```

This fails because the check (`while (busy)`) and the set (`busy = 1`) are two separate steps. Two threads can both see `busy == 0`, both exit the while-loop, and both enter the critical section simultaneously. This is a race condition *inside the locking code itself*.

## Kernel vs. User-Space Critical Sections

Critical sections appear at every level of a system:

| Context | Example shared resource | Common protection |
|---|---|---|
| User-space threads | Global counter, linked list | Mutex, spinlock |
| Kernel interrupt handler | Hardware queue | Disable interrupts |
| Multi-core kernel | Kernel data structure | Spinlock (kernel) |
| File system | Directory entry | VFS inode lock |

## The Cost of Critical Sections

- **Throughput**: Only one thread proceeds inside the section — others stall.
- **Deadlock risk**: If a thread holds a lock and tries to acquire another lock held by a waiting thread, the system deadlocks.
- **Priority inversion**: A high-priority thread can be blocked by a low-priority thread that holds the lock.

Reducing the *size* of critical sections (holding locks for the shortest possible time, protecting only the minimal set of shared data) is the cardinal rule of concurrent systems design.

> **Interview answer:** A critical section is a code region that accesses shared resources and must execute atomically with respect to other threads doing the same. The critical-section problem asks: how do we design an entry/exit protocol that ensures only one thread is inside at a time, while guaranteeing progress and fairness?
