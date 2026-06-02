# Memory Ordering, Reordering, and Visibility

Even when individual operations are atomic, concurrent programs can still produce surprising results because of **memory reordering**. Both compilers and CPUs are permitted to reorder memory accesses — as long as the reordering is invisible to a *single-threaded* observer. In a multi-threaded context, however, these reorderings can break your assumptions about the order other threads see your writes.

## Two Sources of Reordering

### 1. Compiler Reordering

The compiler optimizes for instruction-level parallelism and register reuse. It may move loads before stores, or hoist loop-invariant loads outside a loop, as long as the single-threaded semantics of the function are preserved.

```c
// Source order:
flag = 1;
data = 42;

// Compiler may emit:
data = 42;    // reordered — both are stores to independent locations
flag = 1;
```

To a single thread this is equivalent. To another thread that polls `flag` and then reads `data`, it is not.

### 2. CPU / Hardware Reordering

Modern out-of-order CPUs have store buffers, load queues, and non-coherent caches. Different architectures expose different **memory models**:

| Architecture | Model | What can be reordered |
|---|---|---|
| x86-64 | TSO (Total Store Order) | Stores can be delayed; loads are generally ordered |
| ARM (v7/v8) | Weakly ordered | Loads and stores can be freely reordered |
| RISC-V | RVWMO | Weakly ordered with explicit fence instructions |
| PowerPC | Weakly ordered | Aggressive reordering, requires many fences |

On ARM, two cores can observe the *same* pair of writes in *different orders*, even if they appear sequential in the source.

## Memory Barriers (Fences)

A **memory barrier** (or fence) is an instruction that prevents the CPU or compiler from moving memory accesses across it. There are several flavors:

| Barrier Type | Effect |
|---|---|
| **Full fence** (`MFENCE` on x86, `DMB SY` on ARM) | No load or store may cross the fence in either direction |
| **Store fence** (`SFENCE`) | All stores before the fence complete before any store after |
| **Load fence** (`LFENCE`) | All loads before the fence complete before any load after |
| **Acquire** | Loads/stores after this point are not moved before it |
| **Release** | Loads/stores before this point are not moved after it |

The **acquire-release** pair is the standard pattern for lock/unlock:

```
LOCK ACQUIRE          LOCK RELEASE
─────────────         ─────────────
  (no load/store        (no load/store
   moves above)          moves below)
     │                      │
     ▼                      ▼
  Critical                Critical
  Section                 Section
```

## C++ Memory Order

C++11 `std::atomic` lets you specify the ordering contract per operation:

```cpp
#include <atomic>

std::atomic<int> data{0};
std::atomic<bool> ready{false};

// Producer thread:
data.store(42, std::memory_order_relaxed);   // no ordering guarantee
ready.store(true, std::memory_order_release); // all prior stores visible before this

// Consumer thread:
while (!ready.load(std::memory_order_acquire))
    ;   // acquire: all stores done before the release are now visible
int v = data.load(std::memory_order_relaxed);
// v is guaranteed to be 42
```

The `release` on the producer ensures that `data = 42` is visible before `ready = true` is published. The `acquire` on the consumer ensures that once it sees `ready == true`, it also sees `data == 42`.

## The Visibility Problem in Practice

```cpp
// BAD: no synchronization
bool ready = false;
int data = 0;

// Thread 1:
data = 42;
ready = true;   // compiler or CPU may reorder this before data = 42

// Thread 2:
while (!ready);
// data might still be 0 here on ARM!
printf("%d\n", data);
```

Marking `ready` as `std::atomic<bool>` with default `memory_order_seq_cst` fixes this but incurs fence overhead. Using `memory_order_release`/`acquire` is lighter weight and still correct.

## Key Takeaways

- **Compiler barriers** prevent *compiler* reordering (e.g., `asm volatile("" ::: "memory")` in GCC).
- **CPU barriers** prevent *hardware* reordering.
- `std::atomic` with `memory_order_seq_cst` (the default) inserts both.
- On x86, TSO means you rarely need explicit load fences, but ARM requires fences far more often.
- Lock acquisition implies **acquire** semantics; lock release implies **release** semantics — this is why mutex-protected code doesn't need additional fences.

> **Interview answer:** Memory reordering means the CPU and compiler can execute memory accesses in a different order than written in the source, as long as the single-thread behavior is unchanged. In concurrent code this breaks assumptions. Memory barriers (fences) and acquire/release semantics on atomic operations enforce the ordering constraints that make synchronization protocols correct across cores and architectures.
