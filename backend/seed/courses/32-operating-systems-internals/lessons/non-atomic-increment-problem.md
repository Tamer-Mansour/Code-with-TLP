# Why count++ Is Not Atomic

The expression `count++` looks like a single operation in source code, but it is **not atomic** on virtually any modern architecture. Understanding this distinction — between source-level syntax and machine-level execution — is foundational to writing correct concurrent code.

## From Source to Machine Instructions

Consider this C snippet:

```c
int count = 0;

void increment() {
    count++;
}
```

On x86-64, a non-optimizing compiler produces roughly:

```asm
; count is at some memory address, say [rip+count]
mov  eax, DWORD PTR [rip+count]   ; (1) Load count into register
add  eax, 1                        ; (2) Increment register
mov  DWORD PTR [rip+count], eax   ; (3) Store result back to memory
```

Three separate instructions. The CPU can be interrupted (or on a multi-core machine, another core can execute concurrently) **between any two of them**. This creates the race window.

## The Lost-Update Race

Two threads each calling `increment()` once:

```
Thread A            Thread B            count (memory)
────────────────    ────────────────    ──────────────
(1) Load  → A=0                         0
                    (1) Load  → B=0     0
(2) Add   → A=1                         0
(2)                 Add   → B=1         0
(3) Store A=1                           1
                    (3) Store B=1       1   ← lost update!
```

Expected result: `2`. Actual result: `1`. One increment is silently discarded.

## Does the Compiler Help? No — It Makes Things Worse

Without explicit synchronization, the compiler is allowed to:

- **Reorder** the load and store relative to other operations.
- **Cache** `count` in a register across loop iterations (you never see updated memory values).
- **Eliminate** the store entirely if it believes no other thread can observe it.

In C/C++, a data race is **undefined behavior**. The compiler can legally assume data races do not happen, and it will optimize accordingly — which can produce results that look completely nonsensical.

```c
// Compiler may transform this loop:
for (int i = 0; i < 1000000; i++) count++;

// Into this (hoisting count into a register):
int tmp = count;
tmp += 1000000;
count = tmp;
// Now two threads doing this simultaneously lose 999999 updates each.
```

## Even x86 `INC` Is Not Atomic Across Cores

You might think that using the single `INC` instruction avoids the race:

```asm
inc DWORD PTR [rip+count]   ; read-modify-write in one instruction?
```

On a single-core machine, `INC` *is* atomic with respect to interrupts because no context switch can occur mid-instruction. But on a **multi-core** machine, two cores can issue `INC [count]` at the same moment, and the CPU's cache-coherence protocol does not guarantee atomicity for plain `INC`. Both cores can read the same cached value and produce the same result.

To make it truly atomic you need the `LOCK` prefix:

```asm
lock inc DWORD PTR [rip+count]
```

`LOCK` causes the processor to assert a bus lock (or, on modern CPUs, lock the cache line), making the entire read-modify-write indivisible across all cores.

## The C11/C++11 Fix: `_Atomic` / `std::atomic`

```c
#include <stdatomic.h>

atomic_int count = 0;

void increment() {
    atomic_fetch_add(&count, 1);   // guaranteed atomic RMW
}
```

```cpp
#include <atomic>

std::atomic<int> count{0};

void increment() {
    count.fetch_add(1);            // or count++; same thing
}
```

The standard library generates the appropriate `LOCK`-prefixed instruction (or equivalent on ARM: `LDADD`, `STLXR` retry loops, etc.) and prevents the compiler from reordering around the operation.

## Quick Reference

| Expression | Atomic? | Reason |
|---|---|---|
| `count++` | No | Compiles to load/add/store |
| `count = 0` | Sometimes | Only if naturally aligned and fits in one bus transaction |
| `lock inc [count]` (x86 asm) | Yes | Hardware lock prefix |
| `atomic_fetch_add(&count, 1)` | Yes | Language-level atomic RMW |

> **Interview answer:** `count++` compiles to a load, an add, and a store — three separate instructions. On a multi-core machine, another thread can interleave its own load between your load and store, causing a lost update. Marking the variable `std::atomic` tells both the compiler and the hardware to perform the read-modify-write as an indivisible operation.
