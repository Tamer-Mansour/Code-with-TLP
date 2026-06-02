# wait() and signal() Semantics

`wait()` and `signal()` (also spelled `P` and `V` from Dutch *proberen* and *verhogen*) are the two atomic operations that define a semaphore. Understanding exactly what happens — and what "atomic" means in this context — is critical for reasoning about correctness.

## Formal Definitions

```
wait(S):
    while S <= 0:
        block this thread
    S = S - 1

signal(S):
    S = S + 1
    if any thread is blocked on S:
        wake one of them
```

The key guarantee: the check-and-decrement in `wait` and the increment-and-wake in `signal` are each performed **atomically** — no other thread can observe an intermediate state.

## What "Atomic" Means Here

On a uniprocessor, atomicity can be achieved by disabling interrupts for the duration of the operation. On multiprocessors, the implementation uses hardware atomic instructions such as `LOCK CMPXCHG` (x86) or `LDREX/STREX` (ARM), combined with kernel assistance for the blocking path.

```asm
; x86 — decrement and jump if result < 0 (simplified)
lock dec [semaphore_value]
jl  .block_thread
```

The OS kernel provides the blocking queue; user-space libraries (like POSIX `sem_wait`) use `futex` on Linux to avoid a kernel call in the uncontended fast path.

## The Blocking Path in Detail

When `wait(S)` finds `S == 0`:

1. The thread adds itself to the semaphore's wait queue.
2. The thread transitions to **WAITING** state — it no longer consumes CPU.
3. Control returns to the scheduler, which picks another runnable thread.

When `signal(S)` is called:

1. `S` is incremented atomically.
2. If the wait queue is non-empty, one waiter is moved to the **READY** state.
3. The scheduler eventually runs that thread, and it completes its decrement.

## Spurious Wakeups and Mesa vs Hoare Semantics

In some implementations a thread can be woken without `signal()` being called — a **spurious wakeup**. This is why the pseudocode uses a `while` loop, not an `if`:

```c
// Correct — re-check condition after wakeup
sem_wait(&sem);  // POSIX handles this internally with the counter

// With condition variables (related concept):
while (!condition_met) {
    pthread_cond_wait(&cond, &mtx);  // must re-check in a while loop
}
```

POSIX `sem_wait` is specified to be spurious-wakeup safe because the counter is the authoritative state.

## Worked Example — Signaling Between Threads

```c
#include <semaphore.h>
#include <pthread.h>
#include <stdio.h>

sem_t ready;

void *worker(void *arg) {
    printf("Worker: waiting for signal\n");
    sem_wait(&ready);          // blocks until signaled
    printf("Worker: proceeding after signal\n");
    return NULL;
}

int main() {
    sem_init(&ready, 0, 0);    // initial value 0 — worker will block
    pthread_t t;
    pthread_create(&t, NULL, worker, NULL);

    // do some work...
    printf("Main: sending signal\n");
    sem_post(&ready);          // wake the worker

    pthread_join(t, NULL);
    sem_destroy(&ready);
    return 0;
}
```

Output is deterministic: the worker always prints its second line after the main thread posts.

## Common Pitfalls

| Mistake | Effect |
|---|---|
| Calling `signal` without a prior `wait` | Counter goes above maximum; extra threads enter critical section |
| Missing `signal` on an error path | Threads waiting on the semaphore starve |
| Calling `wait` twice without `signal` in between | Deadlock if initial value was 1 |

## Key Properties to Remember

- `wait` is a **blocking decrement** — if the value would go negative, the caller sleeps.
- `signal` is a **non-blocking increment** — it never blocks; it only wakes a sleeper if one exists.
- Both operations are atomic with respect to each other.
- The order in which blocked threads are woken is **implementation-defined** (often FIFO, but not guaranteed).

> **Interview answer:** `wait()` atomically decrements the semaphore and blocks if the result would be negative; `signal()` atomically increments it and wakes one blocked thread. Together, they provide a race-free mechanism for mutual exclusion and thread coordination.
