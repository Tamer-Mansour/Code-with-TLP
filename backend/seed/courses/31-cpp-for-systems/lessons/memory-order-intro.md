# Memory Ordering and Happens-Before (Intro)

Modern CPUs and compilers aggressively reorder instructions for performance. In a single-threaded program this is invisible and harmless. In a multithreaded program, reordering can break code that appears logically correct. The C++ memory model provides tools to control this reordering through **memory order** annotations.

## Why Reordering Happens

Both the compiler and the CPU are free to reorder memory accesses as long as the result is the same **within a single thread** — the "as-if" rule. But other threads may observe these reorderings:

```cpp
// Thread 1
data = 42;          // (A)
ready.store(true);  // (B)

// Thread 2
while (!ready.load()) {}  // wait for B
assert(data == 42);       // may FAIL without proper memory ordering!
```

Without synchronization, the CPU or compiler may execute (B) before (A). Thread 2 could see `ready == true` while `data` still holds its old value.

## The C++ Memory Orders

`std::atomic` operations accept an optional `std::memory_order` argument:

| Memory Order | Meaning |
|---|---|
| `memory_order_relaxed` | No ordering guarantees. Only atomicity. |
| `memory_order_acquire` | No reads/writes in this thread may move **before** this load. |
| `memory_order_release` | No reads/writes in this thread may move **after** this store. |
| `memory_order_acq_rel` | Combines acquire and release (for read-modify-write). |
| `memory_order_seq_cst` | Total sequential consistency. The default. |

## The Happens-Before Relationship

A **happens-before** (HB) edge means that all memory effects of operation A are guaranteed visible to thread B when it executes operation B. HB edges are established by:

- Program order within a thread (sequenced-before)
- A `release` store **synchronizes-with** an `acquire` load of the same atomic that reads the stored value

```
Thread 1 release-stores → Thread 2 acquire-loads
⟹ Everything Thread 1 wrote before its store
   is visible to Thread 2 after its load
```

## Fixing the Flag Pattern with Acquire-Release

```cpp
#include <atomic>
#include <cassert>

std::atomic<bool> ready{false};
int data = 0;

// Thread 1 (producer)
void producer() {
    data = 42;                                    // (A) — happens before B
    ready.store(true, std::memory_order_release); // (B) — release
}

// Thread 2 (consumer)
void consumer() {
    while (!ready.load(std::memory_order_acquire)) {} // (C) — acquire
    assert(data == 42);  // safe: A happens-before C via B synchronizes-with C
}
```

The release-store at (B) and the acquire-load at (C) form a **synchronizes-with** relationship. This guarantees that (A) happens-before anything after (C).

## memory_order_relaxed

Use `relaxed` only when you need atomicity but don't care about ordering — for example, a statistics counter where the exact value at any instant doesn't matter:

```cpp
std::atomic<int> hit_count{0};

void record_hit() {
    hit_count.fetch_add(1, std::memory_order_relaxed);
    // No ordering needed — just count hits accurately
}
```

Relaxed operations are the fastest but the hardest to reason about. Avoid them unless you understand the implications.

## memory_order_seq_cst (the Default)

The default memory order for all atomic operations. It imposes a **total order** — every sequentially consistent operation appears to execute in the same order to all threads. This is the easiest to reason about but has the highest cost on weakly-ordered architectures (ARM, POWER).

```cpp
// These two are equivalent — seq_cst is the default
counter.fetch_add(1);
counter.fetch_add(1, std::memory_order_seq_cst);
```

## Quick Decision Guide

```
Need atomicity only, no ordering?       → relaxed
Publishing data with a flag?             → release (store) + acquire (load)
Read-modify-write in the middle?         → acq_rel
Unsure / simple programs?               → seq_cst (default)
```

## Common Pitfall: Mixing Orders

Using `relaxed` on the flag in a producer-consumer pattern is a common mistake. The atomic operation itself will not be torn, but the happens-before chain breaks and the consumer may see stale `data`.

> **Interview answer:** The C++ memory model prevents UB from data races and gives you `std::memory_order` to control how reorderings are constrained across threads. `acquire`/`release` create a happens-before edge: all writes before a release-store are visible to any thread that observes the corresponding acquire-load. The default (`seq_cst`) is safest; `relaxed` is fastest but provides no ordering.
