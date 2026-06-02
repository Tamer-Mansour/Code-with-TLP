# Memory Ordering and the FENCE Instruction

Modern CPUs and memory systems do not necessarily complete memory operations in the order they appear in your program. RISC-V provides the `FENCE` instruction to impose ordering constraints when this reordering would cause correctness problems — particularly in multi-core or I/O contexts.

## Why Memory Reordering Happens

Three sources of reordering exist:

1. **CPU out-of-order execution**: The processor may execute loads and stores in any order that preserves single-thread semantics (visible only to other threads).
2. **Store buffers**: A write may sit in a store buffer and be visible to other cores later than the instruction's program order.
3. **Compiler reordering**: The compiler may reorder memory operations within a thread for optimization.

```c
// Thread A:
flag = 1;       // Store 1
data = 42;      // Store 2

// Thread B:
while (!flag);  // Load flag
use(data);      // Load data — may see old data if stores reordered!
```

Without memory ordering constraints, Thread B might observe `flag = 1` but `data = 0` if the CPU or compiler placed Store 2 after the flag becomes visible.

## The RISC-V Memory Model (RVWMO)

RISC-V defines the **RISC-V Weak Memory Ordering (RVWMO)** model. Under RVWMO:

- Loads and stores within a single hart (hardware thread) appear in order to that hart.
- Across harts, operations may appear in different orders unless ordering is enforced.
- This is a **weak** or **relaxed** memory model — weaker than x86's Total Store Order (TSO).

## The FENCE Instruction

`FENCE` ensures that all memory operations of type **predecessor** complete before any operations of type **successor** begin, as observed by all other harts.

```asm
FENCE  predecessor, successor
```

Both predecessor and successor are 4-bit fields specifying which operation types to order:

| Bit | Meaning |
|---|---|
| `I` | Device Input (reads from I/O) |
| `O` | Device Output (writes to I/O) |
| `R` | Memory Reads |
| `W` | Memory Writes |

The common forms:

```asm
FENCE  RW, RW    # Full memory barrier: all reads/writes before FENCE
                 # complete before any reads/writes after it
FENCE  W, W      # Write-to-write barrier (store ordering)
FENCE  R, RW     # Acquire semantics
FENCE  RW, W     # Release semantics
```

## Acquire and Release Semantics

Two fundamental patterns appear in lock-free programming:

**Acquire** (before reading shared data):
```asm
FENCE  R, RW    # Ensure all loads after FENCE see writes from the releasing thread
```

**Release** (after writing shared data):
```asm
FENCE  RW, W    # Ensure all writes before FENCE are visible before the unlock store
```

The `A` extension's `LR.W`/`SC.W` and `AMO` instructions with `.aq`/`.rl` suffixes embed these semantics directly, which is more efficient than a standalone `FENCE`.

## FENCE.I: Instruction-Fetch Ordering

`FENCE.I` is a separate instruction for ordering **instruction fetches** with **data writes**. It ensures that a store to memory (e.g., JIT-compiled code) is visible to subsequent instruction fetches on the same hart.

```asm
# After writing new machine code to a buffer:
FENCE.I    # Ensure icache sees the newly written code
jalr  x0, x10, 0   # Jump to the JIT-compiled code
```

Without `FENCE.I`, the instruction cache might execute stale bytes.

## Worked Example: Spinlock

```asm
# Unlock spinlock stored at address in x10
# 1. Ensure all protected writes are complete
FENCE   RW, W

# 2. Release the lock (store 0)
sw      x0, 0(x10)
```

On the acquiring side:

```asm
# 1. Acquire the lock (poll until zero, then claim)
retry:
    lw   x11, 0(x10)
    bnez x11, retry        # spin while locked
    # (real implementation would use LR/SC here)

# 2. Ensure reads inside the critical section see updated data
FENCE   R, RW
```

## Common Pitfall

Using `FENCE` where none is needed wastes cycles (it stalls the pipeline). Using no `FENCE` in concurrent code is a data race. The minimal correct approach: use the `A` extension's atomic instructions with `.aq`/`.rl` suffixes, which encode ordering precisely without a separate `FENCE`.

> **Interview answer:** RISC-V uses the RVWMO weak memory model, where loads and stores across threads can appear out of order. The `FENCE` instruction enforces ordering: all predecessor operations of the specified type complete before any successor operations begin. `FENCE.I` separately orders instruction-fetch after data writes.
