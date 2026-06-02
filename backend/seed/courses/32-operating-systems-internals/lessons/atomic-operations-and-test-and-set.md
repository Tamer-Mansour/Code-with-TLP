# Atomic Operations, Test-and-Set, and Compare-and-Swap

Hardware designers recognized early that software-only mutual exclusion solutions (like Peterson's algorithm) are fragile and require careful memory-ordering assumptions. Modern CPUs therefore provide **hardware atomic instructions** that perform a read-modify-write on a memory location indivisibly — no other core can observe an intermediate state.

## Why Hardware Support Is Needed

A pure software solution like:

```c
while (lock != 0);   // wait
lock = 1;            // acquire
```

has a race between the `while` check and the `lock = 1` assignment. Hardware atomics eliminate this gap by doing both in a single uninterruptible operation.

## Test-and-Set (TAS)

**Test-and-Set** reads a memory word, sets it to `1`, and returns the *old* value — all as one atomic operation.

```c
// Conceptual (non-atomic) model — the hardware makes this indivisible:
int test_and_set(int *target) {
    int old = *target;
    *target = 1;
    return old;
}
```

### Building a Spinlock with TAS

```c
int lock = 0;   // 0 = free, 1 = held

void acquire() {
    while (test_and_set(&lock) == 1)
        ;   // spin until we get 0 back (meaning we grabbed a free lock)
}

void release() {
    lock = 0;
}
```

If `test_and_set` returns `0`, the thread just atomically set the lock to `1` — it owns the lock. If it returns `1`, the lock was already held; try again.

**x86 instruction:** `XCHG reg, mem` (always locked on x86 when operating on memory).

## Compare-and-Swap (CAS)

**Compare-and-Swap** is more powerful. It takes three arguments: a memory address, an **expected** value, and a **new** value. Atomically:

1. If `*addr == expected`, write `new` to `*addr` and return `true` (or the old value).
2. Otherwise, do nothing and return `false` (or the old value).

```c
// Conceptual model:
bool compare_and_swap(int *addr, int expected, int new_val) {
    if (*addr == expected) {
        *addr = new_val;
        return true;
    }
    return false;
}
```

### Building a Lock with CAS

```c
int lock = 0;

void acquire() {
    while (!compare_and_swap(&lock, 0, 1))
        ;   // spin: expected=0 (free), swap to 1 (held)
}

void release() {
    lock = 0;
}
```

### Lock-Free Counter with CAS (Retry Loop)

CAS enables **lock-free** data structures — concurrent updates without a mutex:

```c
#include <stdatomic.h>

atomic_int counter = 0;

void atomic_increment() {
    int old, new;
    do {
        old = atomic_load(&counter);
        new = old + 1;
    } while (!atomic_compare_exchange_weak(&counter, &old, new));
    // Retry if another thread changed counter between load and CAS
}
```

This pattern — load, compute, CAS, retry on failure — is the backbone of all lock-free algorithms.

**x86 instruction:** `CMPXCHG dest, src` (requires `LOCK` prefix for multi-core atomicity).  
**ARM instruction:** `LDXR`/`STXR` load-exclusive/store-exclusive pair, or the newer `CAS` instruction on ARMv8.1.

## Fetch-and-Add (FAA)

FAA atomically adds a value to a memory location and returns the old value. It is the direct atomic equivalent of `count++`:

```c
// x86: LOCK XADD
int fetch_and_add(int *addr, int delta) {
    // atomically: old = *addr; *addr += delta; return old;
}
```

## Comparison of Atomic Primitives

| Primitive | What it does | Best for |
|---|---|---|
| Test-and-Set | Set to 1, return old | Simple spinlocks |
| Compare-and-Swap | Conditional write | Lock-free structures, retry loops |
| Fetch-and-Add | Add and return old | Atomic counters, ticket locks |
| Load-Linked / Store-Conditional | LL/SC pair (ARM, RISC-V) | Alternative to CAS, avoids ABA |

## The ABA Problem

CAS has a subtle pitfall. A thread reads value `A`, gets preempted, another thread changes the value to `B` then back to `A`. The CAS sees `A` and succeeds — but the memory may have been logically modified in a meaningful way (e.g., a pointer that was freed and reallocated).

Solutions include:
- Attaching a version counter (tagged pointers).
- Using LL/SC instead of CAS (LL/SC detects *any* write, not just a value change).

> **Interview answer:** Test-and-Set atomically sets a word to 1 and returns its old value — it eliminates the race between checking and setting a lock flag. Compare-and-Swap is more general: it writes a new value only if the current value matches an expected value, enabling lock-free retry loops. Both are implemented as single hardware instructions with a LOCK prefix (or equivalent) to prevent concurrent access from other cores.
