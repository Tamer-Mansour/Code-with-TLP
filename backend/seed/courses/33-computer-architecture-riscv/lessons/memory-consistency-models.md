# Memory Consistency Models

Cache coherence ensures that all processors agree on the value of a single address. **Memory consistency** is a different and harder question: in what order do memory operations to *different* addresses appear to execute? The answer depends on the **memory consistency model** — a contract between hardware and software.

## Why Order Matters

Consider two threads sharing variables `x` and `y`, both initially `0`:

```
Thread 0:        Thread 1:
  x = 1;           y = 1;
  r0 = y;          r1 = x;
```

After both threads complete, is it possible that `r0 = 0` AND `r1 = 0`? Intuitively, no — at least one thread should see the other's write. But on real processors with store buffers and out-of-order execution, this outcome *is* possible without explicit synchronization.

## Sequential Consistency (SC)

**Lamport (1979):** A multiprocessor is sequentially consistent if the result of any execution is the same as if all operations of all processors were executed in some sequential order, and operations of each individual processor appear in program order within that sequence.

- Every processor's operations appear to execute in order.
- All processors see the same global interleaving.
- The classic, intuitive model — what most programmers assume.

**Cost:** SC requires that a processor stall every load until all prior stores are globally visible. This kills the performance benefit of store buffers and out-of-order execution.

```
Allowed under SC:    r0=1, r1=0  or  r0=0, r1=1  or  r0=1, r1=1
NOT allowed under SC: r0=0, r1=0
```

## Total Store Order (TSO)

**Used by: x86 (Intel, AMD)**

TSO relaxes SC by allowing processors to read their own in-flight writes before they are globally visible via a **store buffer (FIFO queue)**. All writes are still globally ordered and eventually seen by all.

```
Core 0 pipeline:
  [WB stage] → [Store Buffer] → [L1 Cache] → [Shared Memory]
                    ↑
            Local reads can bypass here
```

**Under TSO:**

- A load can bypass an earlier store (to a different address) if the load is ready.
- Stores are still made visible in order (FIFO store buffer).
- The `r0=0, r1=0` outcome is **possible** in the example above.

**Fix with fence:** Insert `MFENCE` (x86) or `SFENCE`/`LFENCE` between the write and the read to drain the store buffer.

## Relaxed/Weak Memory Models

**Used by: ARM, POWER, RISC-V (RVWMO)**

These models allow even more reordering:

- Stores can be reordered relative to other stores.
- Loads can be reordered relative to other loads.
- Speculative loads ahead of in-flight stores are permitted.

The hardware provides **fence/barrier instructions** to restore ordering when needed. Code that doesn't insert fences runs faster; concurrent data structures and OS code must insert fences explicitly.

## Comparison Table

| Model | Store→Load reorder | Store→Store reorder | Load→Load reorder | Used by |
|---|---|---|---|---|
| Sequential Consistency | No | No | No | Theoretical; some GPUs |
| TSO | Yes (local) | No | No | x86 (Intel/AMD) |
| PSO (Partial SO) | Yes | Yes | No | SPARC (historical) |
| Weak / RMO | Yes | Yes | Yes | ARM, POWER, RISC-V |

## Data-Race-Free (DRF) Programs

Most memory models offer a key guarantee: if a program is **data-race-free** (all accesses to shared variables are properly synchronized with locks, atomics, or barriers), then the program behaves as if it ran on a sequentially consistent machine.

- This is the **DRF0** guarantee (Adve & Hill, 1990).
- It is the foundation of Java's and C11's memory models.
- In practice: use mutexes or `atomic<>` for shared data, and the hardware model becomes irrelevant.

## The C11/C++11 Memory Model

C11 introduced an abstract memory model with explicit ordering guarantees:

```c
#include <stdatomic.h>

atomic_int flag = ATOMIC_VAR_INIT(0);
int data = 0;

// Producer
data = 42;
atomic_store_explicit(&flag, 1, memory_order_release); // write barrier

// Consumer
while (atomic_load_explicit(&flag, memory_order_acquire) == 0); // read barrier
int v = data;  // guaranteed to see 42
```

`memory_order_release` ensures all prior writes are visible before the flag store. `memory_order_acquire` ensures all subsequent reads see writes that happened before the corresponding release. Together they form a **synchronizes-with** relationship.

## Common Pitfall: Double-Checked Locking

A notorious example of a consistency bug:

```cpp
// BROKEN without memory barriers (pre-C++11)
Singleton* getInstance() {
    if (instance == nullptr) {         // Check 1
        lock();
        if (instance == nullptr) {     // Check 2
            instance = new Singleton(); // Compiler/CPU may reorder:
            // store to instance BEFORE constructor finishes!
        }
        unlock();
    }
    return instance;
}
```

The fix in C++11: make `instance` an `atomic<Singleton*>` with appropriate `memory_order` annotations.

## Interview Answer

> "Memory consistency models define the legal orderings of memory operations across different addresses in a multiprocessor system. Sequential consistency is the most intuitive — operations appear globally ordered in program order — but too slow for modern hardware. TSO (x86) allows loads to bypass in-flight stores via a store buffer. ARM and RISC-V use weaker models that allow even more reordering, relying on fence instructions for correctness. High-level languages like C++11 provide `acquire`/`release` semantics that map to the correct hardware fences, letting programmers write portable concurrent code."
