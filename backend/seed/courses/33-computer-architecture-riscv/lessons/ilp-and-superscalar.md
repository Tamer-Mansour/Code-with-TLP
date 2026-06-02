# Instruction-Level Parallelism and Superscalar Execution

A single-issue pipeline completes at most one instruction per cycle. But many programs contain instructions that are completely independent of each other — no reason prevents them from executing simultaneously. **Instruction-Level Parallelism (ILP)** is the measure of how many instructions in a program could execute at the same time if hardware allowed it. Superscalar processors are designed to actually exploit that parallelism.

## What Is ILP?

ILP is a property of the program (and its instruction sequence), not of the hardware. It represents the maximum number of instructions that could theoretically execute in the same cycle, given no hardware resource limits — only true data dependencies constraining execution order.

### Example: Independent Instructions

```asm
# RISC-V
add  t0, t1, t2    # result in t0
add  t3, t4, t5    # result in t3 — completely independent of first add
mul  t6, t0, t3    # depends on BOTH adds above
```

The first two `add` instructions have no data dependency between them. Both could execute in the same cycle. The `mul` must wait for both to complete.

## Superscalar Architecture

A **superscalar** processor fetches, decodes, and executes **multiple instructions per cycle** by duplicating execution units. A 2-wide superscalar can complete up to 2 instructions per cycle (IPC = 2 in ideal conditions); a 4-wide can reach IPC = 4.

```
Cycle:    1         2         3
Fetch:    [I1, I2]  [I3, I4]  [I5, I6]
Execute:  [I1, I2]  [I3, I4]  [I5, I6]
```

Hardware requirements for superscalar:

- **Multiple fetch units** — read 2+ instructions per cycle from the instruction cache
- **Multiple decoders** — decode them in parallel
- **Multiple execution units** — at least two ALUs, possibly a separate load/store unit, FPU, etc.
- **Dependency detection logic** — check all pairs of in-flight instructions for hazards

## ILP vs. Realized IPC

There is always a gap between the theoretical ILP of a program and the IPC a real processor achieves:

| Source of Loss | Effect |
|---------------|--------|
| True data dependencies | Force serialization |
| Branch mispredictions | Flush in-flight instructions |
| Cache misses | Stall entire pipeline |
| Structural hazards | Not enough execution units |
| Memory-level effects | Store-load ordering constraints |

Typical IPC for modern superscalar processors on real workloads is 2–4, even on processors capable of issuing 6–8 per cycle.

## Static vs. Dynamic ILP Exploitation

**Static (compile-time):** The compiler reorders instructions to expose independence. VLIW (Very Long Instruction Word) architectures like Intel's Itanium rely entirely on the compiler to pack multiple operations into one wide instruction word.

```asm
# VLIW-style: both ops issue in the same cycle
add t0, t1, t2  ||  add t3, t4, t5
```

**Dynamic (runtime):** The processor itself detects independent instructions at runtime, even across loop iterations or function boundaries. This is what out-of-order processors do — the subject of the next lesson.

## Limits of ILP: Amdahl's Wall

Even in an infinitely wide machine with perfect branch prediction and no cache misses, ILP is limited by **true data dependency chains** (the critical path through the instruction graph). If the longest chain of dependent instructions is 50 instructions long in a 1000-instruction window, no amount of hardware can go faster than 50 cycles for that window.

Empirical studies (Wall's "Limits of Instruction-Level Parallelism") found that real programs typically expose 2–7 IPC of available ILP under realistic assumptions.

## RISC-V and Superscalar

RISC-V's fixed-width, load-store architecture makes superscalar implementation cleaner than CISC. The SiFive P670 and the upcoming Ventana Veyron V2 are RISC-V superscalar processors targeting high-performance applications.

> **Interview answer:** ILP is the inherent parallelism in a program's instruction stream; superscalar processors exploit ILP by issuing multiple instructions per cycle using replicated hardware units, but actual IPC is limited by data dependencies, branch mispredictions, and cache misses, typically yielding 2–4 IPC on real workloads despite issue widths of 4–8.
