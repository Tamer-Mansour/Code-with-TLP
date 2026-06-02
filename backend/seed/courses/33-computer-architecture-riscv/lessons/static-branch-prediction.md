# Static Branch Prediction

Static branch prediction makes its decision at **compile time** — before the program runs. No runtime history is consulted. The prediction is baked into the instruction stream or inferred from simple rules about the direction of the branch.

Despite its simplicity, static prediction can be effective when a compiler has good information about typical program behavior.

## The Four Classic Strategies

### 1. Predict Not-Taken (PNT)

The simplest possible policy: always assume the branch is not taken and continue fetching sequential instructions.

- Correct for `if` bodies that execute rarely (e.g., error handlers).
- Wrong for loops (the back-edge taken branch is the common case).
- Requires zero hardware: just fetch the next PC + 4.

### 2. Predict Taken (PT)

Always assume the branch is taken; jump to the target immediately.

- Correct for loops (backward branches are usually taken).
- Requires the branch target to be known at fetch time (may need early decode).

### 3. BTFN — Backward-Taken, Forward-Not-Taken

Combines the two: if the branch target address is **below** the current PC (a backward branch, i.e., a loop), predict taken. If the target is **above** (a forward branch, i.e., an `if`), predict not-taken.

```
if (target_addr < current_pc)  → predict TAKEN    (loop back-edge)
else                           → predict NOT TAKEN (if/else forward)
```

BTFN achieves ~65-75% accuracy without any runtime information. It is trivially cheap to implement in hardware — just compare two addresses.

### 4. Profile-Guided Prediction

The compiler instruments the binary, runs it on representative inputs, collects branch outcome statistics, then recompiles with **branch hints** embedded in the instruction encoding.

RISC-V reserves a hint bit in compressed branches; x86 historically used the `HINT` prefix byte (0x2E / 0x3E).

```c
// GCC __builtin_expect hint — tells the compiler which path is likely
if (__builtin_expect(ptr != NULL, 1)) {   // 1 = likely true
    process(ptr);
}
```

The compiler can then reorder code so the likely path has fewer or cheaper branches.

## Accuracy Comparison

| Strategy         | Typical accuracy |
|------------------|-----------------|
| Always not-taken | ~60%            |
| Always taken     | ~60%            |
| BTFN             | ~65-75%         |
| Profile-guided   | ~75-90%         |

## When Static Prediction Is Sufficient

Static prediction remains useful in:

- **Embedded and real-time systems** where predictable latency matters more than peak throughput.
- **Simple in-order pipelines** (e.g., RISC-V RV32I on microcontrollers) without a branch history table.
- **Compiler optimizations** — reordering code to match a fixed hardware policy (predict-not-taken) lets the compiler eliminate many runtime penalties by making the "fall-through" path the common case.

## Pitfalls

- **Data-dependent branches** (input validation, error checks) have wildly variable outcomes — static prediction fails entirely.
- **Aliasing:** profile-guided prediction is accurate for the training workload but can regress badly on a different workload.
- **Security:** static prediction is deterministic and therefore more predictable for an attacker. (Dynamic predictors, paradoxically, can be exploited too — see the Spectre lesson.)

## Worked Example: Compiler Code Layout

Given this C:

```c
if (error) {
    handle_error();   // rare
}
// common path continues here
```

A compiler targeting a predict-not-taken processor places `handle_error()` out-of-line and leaves the common path sequential. The branch (`bne error, zero, handle_error`) is almost always not-taken — matching the hardware default — so no penalty is paid.

> **Interview answer:** Static branch prediction uses compile-time rules (BTFN) or profiling data to choose a fixed prediction. It needs no hardware state and is accurate for predictable patterns like loops, but fails for data-dependent or irregular branches where dynamic predictors are necessary.
