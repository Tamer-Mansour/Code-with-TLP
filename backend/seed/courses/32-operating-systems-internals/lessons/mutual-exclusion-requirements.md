# Mutual Exclusion, Progress, and Bounded Waiting

Any correct solution to the critical-section problem must satisfy exactly **three requirements**. These were formalized by Dijkstra and remain the standard evaluation criteria for every synchronization primitive you will encounter — mutexes, semaphores, spinlocks, and beyond.

## The Three Requirements

### 1. Mutual Exclusion

If thread T1 is executing inside its critical section, no other thread may simultaneously be executing inside *its* critical section (for the same shared resource).

This is the **safety** property — it prevents data corruption. A solution that allows two threads inside at the same time has failed the most basic requirement.

```
At all times: number of threads inside critical section ≤ 1
```

### 2. Progress

If no thread is currently inside the critical section, and one or more threads want to enter, then **one of those waiting threads must be allowed to proceed within a finite amount of time**. The decision about which thread enters next cannot be postponed indefinitely, and threads that are in their *remainder* sections (not trying to enter) must not influence this decision.

This is a **liveness** property — the system must keep making forward progress. A solution that causes all threads to wait forever even though the critical section is free (for example, due to a deadlock in the entry protocol) violates progress.

### 3. Bounded Waiting

Once a thread has requested to enter its critical section, there is an upper bound on how many times *other* threads are allowed to enter before the requesting thread is granted access.

This prevents **starvation** — a thread that perpetually loses out to others despite waiting. The bound does not need to be a fixed number, but it must be finite.

## Summary Table

| Property | Type | What it prevents | Violated by |
|---|---|---|---|
| Mutual exclusion | Safety | Data races, corruption | Two threads inside at once |
| Progress | Liveness | Deadlock in entry protocol | All threads spinning forever with CS free |
| Bounded waiting | Fairness | Starvation | One thread waiting forever |

## Why All Three Matter Together

Satisfying only one or two properties is not enough:

- **Mutual exclusion without progress**: A solution could force all threads to wait before entering, satisfying exclusion trivially (nobody gets in). This is useless.
- **Progress without bounded waiting**: A solution could always let the *same* thread enter, starving others. It makes progress in aggregate but is unfair.
- **Bounded waiting without mutual exclusion**: A fair turn-taking scheme that allows two threads in simultaneously — correct fairness, broken safety.

## Strict Alternation — A Classic Near-Miss

```c
// Shared turn variable
int turn = 0;

// Thread 0
while (turn != 0);   // wait until it's our turn
// --- critical section ---
turn = 1;            // give turn to thread 1

// Thread 1
while (turn != 1);
// --- critical section ---
turn = 0;
```

This satisfies **mutual exclusion** and **bounded waiting** (each thread waits at most one "other" turn), but it **violates progress**. If Thread 0 completes its critical section and Thread 1 is in its remainder section (not interested in entering), Thread 0 can never re-enter — it must wait for Thread 1 to take its turn, which may never happen.

> **Interview answer:** A correct synchronization solution must guarantee mutual exclusion (only one thread in the critical section at a time), progress (a thread can always enter if the section is free and it wants to), and bounded waiting (no thread waits forever). These three properties map to safety, liveness, and fairness respectively.

## Applying the Criteria

When evaluating any lock or algorithm, ask:

1. Can two threads ever be inside simultaneously? (mutual exclusion)
2. If the lock is free and someone wants it, will they eventually get it? (progress)
3. Can a thread that requested the lock be skipped infinitely many times? (bounded waiting)

Pass all three tests and the solution is *correct*. Efficiency and performance are separate concerns layered on top of correctness.
