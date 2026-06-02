# The RISC-V Weak Memory Ordering (RVWMO) Model

RISC-V defines its memory model explicitly in the ISA specification rather than leaving it to implementation choices. The result is **RVWMO — RISC-V Weak Memory Ordering** — a formally specified, deliberately relaxed model that allows aggressive hardware optimizations while providing clear rules for software.

## Design Philosophy

RISC-V's designers chose a **weak** (relaxed) memory model for good reasons:

- Weak models allow out-of-order execution, speculative loads, and store buffer bypassing without additional hardware constraints.
- Stronger guarantees (like TSO) must be enforced with hardware interlocks that cost power and area.
- Software that needs stronger guarantees can insert explicit fences, paying the cost only when needed.

> RVWMO is compatible with the "DRF implies SC" guarantee: data-race-free programs behave as if sequentially consistent.

## The Global Memory Order

RVWMO defines a **global memory order (GMO)** — a total order on memory operations as observed by the entire system. The model says:

1. Each hart (hardware thread) executes instructions in program order.
2. The GMO may reorder operations from different harts.
3. Within a hart, certain ordering constraints must be preserved.

### Preserved Program Order Rules

Operations `a` and `b` from the same hart must appear in program order in the GMO if:

- `a` and `b` access overlapping addresses and at least one is a store.
- There is a **FENCE** between them that covers the operation types.
- `a` is a load that returns a value written by `b` (data dependency).
- `a` produces an address used by `b` (address dependency).
- `a` produces data stored by `b` (store-data dependency).

All other orderings are **not guaranteed** — the hardware may execute them in any order.

## FENCE Instruction

RISC-V's `FENCE` instruction carries predecessor and successor access-type bits:

```asm
FENCE  pred, succ

# pred = operations BEFORE the fence that must be ordered
# succ = operations AFTER the fence that must be ordered

# Bit fields: I=input (loads), O=output (stores), R=reads, W=writes
```

Common patterns:

```asm
FENCE RW, RW   # Full barrier: all loads and stores before must complete
               # before any load or store after (like x86 MFENCE)

FENCE W, R     # Store-load barrier: all stores before must be visible
               # before any load after (the most expensive fence)

FENCE R, R     # Load-load barrier (rarely needed)
FENCE W, W     # Store-store barrier (ensures store ordering)
```

## Acquire and Release Semantics

RVWMO provides lightweight ordering via **ordering annotations** on load-reserved/store-conditional and atomic operations:

```asm
# Load with acquire semantics (aq bit set)
LR.W.AQ  t0, (a0)       # No later operation can reorder before this load

# Store with release semantics (rl bit set)
SC.W.RL  t1, t2, (a0)   # No earlier operation can reorder after this store

# Full sequential consistency (both aq and rl set)
LR.W.AQ.RL  t0, (a0)
SC.W.AQ.RL  t1, t2, (a0)
```

The acquire annotation on a load prevents subsequent memory operations from being reordered before it. The release annotation on a store prevents prior memory operations from being reordered after it. Together they implement the **release-acquire** pattern.

## AMO Instructions (Atomic Memory Operations)

RISC-V's `A` extension provides atomic read-modify-write operations:

```asm
# Atomic add: atomically adds t1 to memory at a0, returns old value in t0
AMOADD.W  t0, t1, (a0)

# Atomic swap: atomically writes t1 to memory at a0, returns old value in t0
AMOSWAP.W t0, t1, (a0)

# All AMOs support .AQ and .RL annotations
AMOADD.W.AQ.RL  t0, t1, (a0)   # sequentially consistent atomic add
```

Available AMOs: `AMOADD`, `AMOSWAP`, `AMOAND`, `AMOOR`, `AMOXOR`, `AMOMIN`, `AMOMAX` (signed and unsigned variants for min/max).

## LR/SC — Load-Reserved / Store-Conditional

For operations like compare-and-swap that cannot be expressed as a single AMO:

```asm
retry:
    LR.W.AQ   t0, (a0)       # Load-reserved: marks a0 as reserved
    BNE       t0, t1, fail   # Check if value is what we expect
    SC.W.RL   t2, t3, (a0)   # Store-conditional: only succeeds if reservation holds
    BNEZ      t2, retry      # t2 != 0 means SC failed (reservation lost)
    # Success: compare-and-swap succeeded
fail:
```

The reservation is lost if another hart writes the address between `LR` and `SC`. The loop retries until it succeeds — this is the hardware-assisted compare-and-swap idiom.

## Mapping C11 Operations to RVWMO

| C11 / C++ Ordering | RISC-V Implementation |
|---|---|
| `memory_order_relaxed` | Plain load/store, no fence |
| `memory_order_acquire` | Load with `.AQ` annotation |
| `memory_order_release` | Store with `.RL` annotation |
| `memory_order_acq_rel` | Both `.AQ` and `.RL` |
| `memory_order_seq_cst` | `.AQ.RL` + `FENCE RW,RW` |

## RVWMO vs TSO

| Property | RVWMO | TSO (x86) |
|---|---|---|
| Default store→load ordering | Relaxed (no guarantee) | Store buffer ordered |
| Store→store reordering | Allowed | Not allowed |
| Load→load reordering | Allowed | Not allowed |
| Fence needed for mutual exclusion | Yes (FENCE W,R at minimum) | Less often |
| Performance ceiling | Higher (fewer constraints) | Lower |

## Interview Answer

> "RVWMO is RISC-V's formally specified weak memory model. By default it allows stores and loads to be reordered freely across different addresses. Programs express ordering requirements using FENCE instructions with predecessor/successor type bits, or by annotating atomic operations with acquire and release bits. Data-race-free programs under RVWMO still behave as sequentially consistent, so correctly written concurrent code using C11 atomics or proper mutexes works correctly — the compiler just emits the right fence or annotation for each ordering level."
