# Atomics, Barriers, and Synchronization

Correct concurrent programming requires that certain operations appear **indivisible** to other threads and that memory updates are **ordered** appropriately. Hardware provides two building blocks: **atomic operations** and **memory barriers (fences)**. Everything else — mutexes, semaphores, channels — is built on top.

## Why Regular Loads and Stores Are Not Enough

A simple increment `x++` compiles to three operations:

```asm
# Non-atomic increment (read-modify-write)
LOAD  t0, x       # 1. Load
ADDI  t0, t0, 1   # 2. Add
STORE t0, x       # 3. Store
```

If two cores execute this simultaneously, both might load the old value, add 1, and store the same incremented value — effectively losing one increment. This is a **data race**.

## Atomic Read-Modify-Write Operations

An atomic RMW makes the load, modify, and store appear as a single indivisible operation. No other core can observe an intermediate state.

### C11 / C++ Atomics

```c
#include <stdatomic.h>

atomic_int counter = ATOMIC_VAR_INIT(0);

// Thread-safe increment — no mutex needed
atomic_fetch_add(&counter, 1);
// Returns the value BEFORE the add; final value is old+1
```

### Compare-and-Swap (CAS)

The universal atomic primitive — most lock-free data structures build on this:

```c
// C11 compare_exchange_strong
int expected = 0;
int desired = 1;
bool success = atomic_compare_exchange_strong(&flag, &expected, desired);
// If flag == expected (0), writes desired (1) and returns true
// If flag != expected, writes current value into expected and returns false
```

**RISC-V implementation** uses LR/SC:

```asm
cas_loop:
    LR.W.AQ   t0, (a0)        # Load-reserved from &flag
    BNE       t0, a1, fail    # Compare: if *flag != expected, fail
    SC.W.RL   t1, a2, (a0)    # Store-conditional: write desired
    BNEZ      t1, cas_loop    # Retry if SC failed (another hart intervened)
    LI        a0, 1           # Return true (success)
    RET
fail:
    MV        a1, t0          # Update expected with actual value
    LI        a0, 0           # Return false
    RET
```

### x86 Atomic Instructions

```asm
; Atomic increment (lock prefix makes it indivisible)
LOCK INC DWORD PTR [rcx]

; Compare-and-swap
; If [rax] == [memory], set [memory] = rcx and set ZF=1
LOCK CMPXCHG [memory], rcx

; Atomic exchange
LOCK XCHG [memory], rax
```

The `LOCK` prefix asserts the processor's bus lock (or cache-coherence lock) for the duration of the instruction.

## Memory Barriers (Fences)

Atomic operations ensure **atomicity** but not necessarily **ordering** relative to surrounding operations. Memory barriers control that.

### Types of Barriers

| Barrier Type | Effect |
|---|---|
| **Load barrier** | All loads before are complete before any load after |
| **Store barrier** | All stores before are globally visible before any store after |
| **Full barrier** | Both load and store barriers combined |
| **Acquire** | Loads/stores after cannot move before this point |
| **Release** | Loads/stores before cannot move after this point |

### Acquire-Release Pattern

The canonical idiom for safe publication of data:

```c
// Producer
data = compute_result();                              // (1)
atomic_store_explicit(&ready, 1, memory_order_release); // (2) release fence

// Consumer
while (!atomic_load_explicit(&ready, memory_order_acquire)); // (3) acquire fence
use(data);                                            // (4) guaranteed to see (1)
```

The **synchronizes-with** relationship between (2) and (3) guarantees that (4) sees the write at (1). On RISC-V this compiles to a store with `.RL` and a load with `.AQ`; on x86 the store uses `MOV` (TSO provides the ordering for free) and the load uses `MOV` with no fence.

## Spinlock Implementation

A minimal spinlock built from atomics:

```c
typedef atomic_int spinlock_t;

void spin_lock(spinlock_t *lock) {
    int zero = 0;
    // Keep trying CAS until we acquire (0 → 1)
    while (!atomic_compare_exchange_weak_explicit(
               lock, &zero, 1,
               memory_order_acquire,   // acquire on success
               memory_order_relaxed))  // relaxed on failure
    {
        zero = 0; // reset expected after CAS failure
        // Optionally: pause/yield to avoid bus saturation
    }
}

void spin_unlock(spinlock_t *lock) {
    atomic_store_explicit(lock, 0, memory_order_release); // release fence
}
```

On RISC-V the lock becomes an `AMOSWAP.W.AQ` or `LR.W.AQ / SC.W.RL` sequence; on x86 a `LOCK CMPXCHG`.

## ABA Problem

A subtle bug in lock-free data structures that use CAS:

1. Thread 0 reads value `A` from location X.
2. Thread 1 changes X from `A` to `B`, then back to `A`.
3. Thread 0's CAS sees `A` and succeeds — but the underlying state has changed.

**Fix:** Use a **tagged pointer** or **versioned CAS**: pair the pointer with a monotonically increasing version counter. The CAS checks both pointer and version simultaneously.

```c
struct tagged_ptr {
    void *ptr;
    uintptr_t version;
};
// Use 128-bit CAS (CMPXCHG16B on x86, or LR/SC on 64-bit RISC-V with double-word)
```

## Seqlock — A High-Performance Reader-Writer Lock

Used in the Linux kernel for frequently-read, rarely-written data (e.g., system clock):

```c
// Writer
seqlock.sequence++;           // Increment to odd — signals write in progress
write_barrier();
update_shared_data();
write_barrier();
seqlock.sequence++;           // Increment to even — write complete

// Reader (retry if sequence changes)
do {
    seq = seqlock.sequence;   // Read sequence before
    read_barrier();
    read shared data;
    read_barrier();
} while (seq & 1 || seq != seqlock.sequence); // Retry if odd or changed
```

Readers never block writers; they simply retry if a write races with their read.

## Interview Answer

> "Atomic operations make load-modify-store sequences appear indivisible — no other core can see an intermediate state. Memory barriers (fences) control the ordering of those operations relative to surrounding loads and stores. The acquire-release pairing is the fundamental synchronization idiom: a release fence on the writer side and an acquire fence on the reader side establish a happens-before relationship, ensuring the reader sees all writes that happened before the release. On RISC-V this maps to `.RL` and `.AQ` annotations; on x86, TSO's store buffer provides acquire semantics for loads automatically."
