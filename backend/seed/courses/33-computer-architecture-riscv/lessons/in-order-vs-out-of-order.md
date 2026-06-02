# In-Order vs Out-of-Order Execution

The classic five-stage pipeline is **in-order**: instructions enter the pipeline, move through stages, and complete in exactly the order they appear in the program. Out-of-order (OOO) execution breaks this constraint to extract more ILP from real programs.

## The Problem with In-Order Execution

Consider this sequence:

```asm
lw   t0, 0(t1)       # load from memory — may take 100+ cycles on cache miss
add  t2, t0, t3      # depends on t0 — must stall
add  t4, t5, t6      # completely independent — no reason to stall
```

An in-order processor must stall on the second instruction, which also blocks the third even though it is ready to execute immediately. Wasted cycles accumulate quickly.

## Out-of-Order Execution

An OOO processor allows instruction 3 (`add t4, t5, t6`) to **execute before** instruction 2, because it has no data dependency on the load. The hardware:

1. Fetches and decodes instructions in-order
2. Places them in a **Re-Order Buffer (ROB)** and **Reservation Stations (RS)**
3. Dispatches instructions to execution units as soon as their operands are ready — regardless of program order
4. **Commits** (retires) results to architectural state in program order, using the ROB

## Key Hardware Structures

### Reservation Stations (RS)

Hold instructions that are waiting for their operands. When an operand becomes available (broadcast on a results bus), matching reservation station entries "wake up" and become eligible to execute.

### Re-Order Buffer (ROB)

Tracks all in-flight instructions in program order. Instructions execute out-of-order but only commit to the register file or memory in original program order. This ensures:

- Precise exceptions (the processor can roll back to a clean state)
- Correct handling of branch mispredictions (discard unapproved results)

### Register Renaming

OOO processors rename architectural registers (e.g., x5 in RISC-V) to **physical registers** from a larger pool. This eliminates **false dependencies**:

```asm
add  t0, t1, t2    # writes architectural t0 → mapped to physical P47
add  t0, t3, t4    # also writes t0 → mapped to physical P63 (different!)
```

Without renaming, the second `add` must wait for the first because they share the same architectural register name — even though there is no true data flow between them.

## In-Order vs Out-of-Order: Comparison

| Property | In-Order | Out-of-Order |
|----------|---------|-------------|
| Complexity | Low | High |
| Power consumption | Low | High (3–5x) |
| IPC on dependent code | Low | High |
| IPC on independent code | Moderate | High |
| Typical use | Embedded, IoT, MCUs | Desktop, server, phone SoCs |
| RISC-V examples | SiFive E31, CV32E40P | SiFive P670, Rocket Chip (limited) |

## The OOO Pipeline (Simplified)

```
Fetch → Decode → Rename → Dispatch → Issue (out-of-order) → Execute → Complete → Commit (in-order)
```

- **Rename**: map architectural registers to physical registers
- **Dispatch**: place instruction in ROB and RS
- **Issue**: when operands ready, send to execution unit
- **Complete**: write result to physical register, broadcast to waiting RS entries
- **Commit**: retire from ROB in program order, free physical register of previous mapping

## Limits and Practical Considerations

Out-of-order execution has diminishing returns:

- The ROB has finite size (64–512 entries in modern CPUs). If a long-latency operation (cache miss) sits at the head of the ROB, the ROB fills up and the processor stalls — **ROB full stall**.
- Branch mispredictions require flushing the ROB and re-fetching, wasting all in-flight work.
- Memory ordering constraints prevent arbitrary reordering of loads and stores even with OOO hardware.

## Why In-Order Still Matters

For embedded systems, real-time applications, and power-constrained devices, in-order processors are preferred. ARM Cortex-M, RISC-V E-series cores, and most microcontrollers use in-order pipelines. Predictable performance (no variable-latency OOO effects) is sometimes more valuable than peak throughput.

> **Interview answer:** Out-of-order execution allows instructions to execute as soon as their operands are ready rather than in program order; a re-order buffer ensures results commit in order for correctness, and register renaming eliminates false dependencies — at the cost of significant hardware complexity and power, which is why embedded processors stay in-order.
