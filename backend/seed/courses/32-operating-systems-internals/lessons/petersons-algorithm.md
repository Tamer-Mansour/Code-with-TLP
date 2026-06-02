# Peterson's Algorithm for Two Processes

**Peterson's algorithm** (1981) is a landmark software-only solution to the two-process critical-section problem. It uses only shared memory — no special hardware instructions — yet correctly satisfies all three requirements: mutual exclusion, progress, and bounded waiting.

Although modern compilers and CPUs require explicit memory barriers to run Peterson's algorithm correctly, it remains the canonical textbook example of how pure logic can enforce mutual exclusion.

## Shared Variables

```c
// Shared between Thread 0 and Thread 1
int flag[2] = {0, 0};  // flag[i] = 1: thread i wants to enter
int turn = 0;          // whose turn it is to enter (0 or 1)
```

- `flag[i]` is set to `1` by Thread `i` to announce its *intention* to enter.
- `turn` acts as a tiebreaker when both threads want to enter simultaneously.

## The Algorithm

```c
// Thread i (where j = 1 - i, the other thread)
void enter_critical(int i) {
    int j = 1 - i;
    flag[i] = 1;         // "I want to enter"
    turn = j;            // "But you go first if you also want to"
    while (flag[j] == 1 && turn == j)
        ;                // Wait if the other thread wants in AND it's their turn
}

void leave_critical(int i) {
    flag[i] = 0;         // "I'm done"
}
```

## Worked Example — Concurrent Entry Attempt

Suppose Thread 0 and Thread 1 both try to enter simultaneously:

| Step | Thread 0                  | Thread 1                  | flag[0] | flag[1] | turn |
|------|---------------------------|---------------------------|---------|---------|------|
| 1    | `flag[0] = 1`             |                           | 1       | 0       | 0    |
| 2    | `turn = 1`                |                           | 1       | 0       | 1    |
| 3    |                           | `flag[1] = 1`             | 1       | 1       | 1    |
| 4    |                           | `turn = 0`                | 1       | 1       | 0    |
| 5    | while(flag[1]==1 && turn==1)? | while(flag[0]==1 && turn==0)? | | | |
|      | flag[1]=1 but turn=0, so **FALSE** → enters CS | flag[0]=1 and turn=0, so **TRUE** → spins | | | 0 |

Thread 0 enters the critical section. Thread 1 waits. After Thread 0 calls `leave_critical(0)`, `flag[0]` becomes `0`, and Thread 1's spin condition becomes false — it enters.

## Proof Sketch

### Mutual Exclusion

Both threads can only enter if their own `flag` is `1` and `turn` points to the other thread. `turn` is a single integer — it can only equal `0` or `1`, not both simultaneously. Therefore both threads cannot satisfy `turn == j` at the same time, so at most one thread passes the while loop.

### Progress

If Thread `j` is not interested (`flag[j] == 0`), the while condition is immediately false for Thread `i`. Thread `i` enters without delay. The critical section is never left unnecessarily occupied.

### Bounded Waiting

After Thread `i` sets `flag[i] = 1` and `turn = j`, it will be blocked at most once — it must wait for Thread `j` to complete one critical section entry. After that, Thread `j` sets `flag[j] = 0` on exit, allowing Thread `i` to proceed.

## The Memory Ordering Caveat

On modern hardware (especially ARM) and with optimizing compilers, the reads and writes to `flag` and `turn` can be reordered, breaking the algorithm. A correct implementation requires **acquire/release fences** (or sequentially consistent atomics):

```c
#include <stdatomic.h>

_Atomic int flag[2];
_Atomic int turn;

void enter_critical(int i) {
    int j = 1 - i;
    atomic_store_explicit(&flag[i], 1, memory_order_relaxed);
    atomic_store_explicit(&turn, j, memory_order_seq_cst);  // full fence
    while (atomic_load_explicit(&flag[j], memory_order_seq_cst) == 1
           && atomic_load_explicit(&turn, memory_order_seq_cst) == j)
        ;
}
```

## Why Study Peterson's Algorithm?

- It demonstrates that mutual exclusion is achievable with *logic alone*, given a sequentially consistent memory model.
- It introduces the key insight of combining **intent** (`flag`) with a **tiebreaker** (`turn`).
- Every OS textbook uses it as the baseline before introducing hardware solutions (TAS, CAS) and OS-managed solutions (mutexes, semaphores).

> **Interview answer:** Peterson's algorithm uses two shared variables — a `flag` array where each thread announces its intent to enter, and a `turn` variable as a tiebreaker. A thread sets its flag, yields the turn to the other, then waits only if the other thread also wants to enter AND it's the other thread's turn. This guarantees mutual exclusion (turn can favor only one at a time), progress (a disinterested thread can't block entry), and bounded waiting (at most one pass before you get in).
