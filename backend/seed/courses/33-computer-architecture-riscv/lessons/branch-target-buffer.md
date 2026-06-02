# Branch Target Buffer and Return Address Stack

Knowing *whether* a branch is taken is only half the problem. The processor also needs to know *where* to fetch from — the branch target address — before that address has even been decoded, let alone computed. The **Branch Target Buffer (BTB)** and the **Return Address Stack (RAS)** solve this problem.

## Why Target Address Matters

In a typical RISC-V pipeline, the fetch stage sends a PC to the instruction cache every cycle. If a branch is predicted taken, the pipeline must redirect fetch to the branch target address immediately — not two cycles later when decode identifies the instruction as a branch.

Without a BTB, even a perfect taken/not-taken predictor would stall by at least one cycle to decode the branch instruction and read its immediate offset.

## Branch Target Buffer (BTB)

The BTB is a small, fast cache indexed by the branch PC. Each entry stores:

| Field       | Size     | Purpose                          |
|-------------|----------|----------------------------------|
| Tag         | ~20 bits | Partial PC to confirm the hit    |
| Target PC   | 32/64 bits | The address to fetch on taken  |
| Valid bit   | 1 bit    | Entry is populated               |
| Branch type | 2 bits   | Conditional / unconditional / indirect / call |

**Lookup:** During fetch, the current PC is used to look up the BTB simultaneously with the instruction cache. If the BTB hits and the predictor says "taken," the fetch unit immediately redirects to the stored target address — zero additional delay.

```
          ┌─────────────────────────────────┐
          │            BTB                  │
  PC ────►│  [index bits] → tag match?      │──→ target PC
          │                                 │       ↓
          └─────────────────────────────────┘  (redirect fetch if taken)
```

**Update:** After a branch resolves in execute, its target address is written into the BTB for future reference.

**BTB miss:** If the PC does not hit the BTB, the predictor cannot know a branch is present yet. This is an unavoidable cold-start penalty for first-time branches.

## BTB Sizing and Conflict Misses

A direct-mapped BTB with 1 K entries handles most inner-loop branches well. Larger codes that call many functions or have deep call graphs benefit from 4 K–16 K BTB entries. Modern processors use **set-associative** BTBs (2-way or 4-way) to reduce conflict misses.

```
Miss rate ≈  (branches) / (BTB entries)   [rough working number for direct-mapped]
```

## Indirect Branch Prediction

For indirect branches (e.g., `jr ra` or a function pointer call), the target address varies at runtime. The BTB stores only one target per entry — useless for a virtual dispatch call site that jumps to many different functions.

Solutions:
- **Indirect Branch Predictor (IBP):** A separate table indexed by (PC XOR GHR) that remembers the *most recent* target for each pattern.
- **Virtualization-aware predictors:** Tag entries by virtual machine context to avoid cross-VM aliasing.

## Return Address Stack (RAS)

Function returns are the most predictable indirect branches: `ret` (`jalr x0, ra, 0` in RISC-V) always returns to the instruction *after* the corresponding `call`. But the target changes with every call — the BTB cannot capture this correctly.

The **RAS** is a hardware LIFO stack that mirrors the software call stack:

- **On CALL:** Push the return address (PC + 4) onto the RAS.
- **On RET:** Pop the top of the RAS and use it as the predicted target.

```
CALL f    → push (PC+4) onto RAS
  CALL g  → push (PC+4) onto RAS
  RET     → pop RAS → predict return to CALL g's PC+4
RET       → pop RAS → predict return to CALL f's PC+4
```

RAS is typically 8–32 entries deep. A call depth exceeding the RAS capacity causes **stack overflow** in the RAS — older return addresses are lost and those returns fall back to a BTB guess or cause mispredictions.

## Worked Example

```asm
# RISC-V
main:
    call foo          # push (main_ret) onto RAS
    ...               # ← predicted return target
foo:
    call bar          # push (foo_ret) onto RAS
    ...
bar:
    ret               # pop → predict foo_ret (correct)
    ...
foo_cont:
    ret               # pop → predict main_ret (correct)
```

Both returns are predicted correctly with zero misprediction penalty, even though the target addresses differ from call to call.

## Pitfall: Longjmp and Tail Calls

`longjmp` bypasses the normal call/return discipline, causing the RAS to hold stale entries. Tail-call optimization (where a function jumps directly to another instead of calling-and-returning) similarly imbalances the RAS. Architectures sometimes provide a hint (`call/ret` encoding conventions) to help the hardware maintain RAS integrity.

> **Interview answer:** The BTB caches branch target addresses so fetch can redirect immediately at predicted-taken branches. The RAS is a hardware call stack that predicts function return addresses with near-perfect accuracy by mirroring each call with a push and each return with a pop.
