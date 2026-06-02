# Single-Cycle vs Multi-Cycle Execution

When a processor designer decides how to implement the instruction cycle, the first and most consequential choice is: **how many clock cycles does one instruction take?** The two classical answers — one cycle or multiple cycles — lead to radically different hardware organisations, each with distinct trade-offs.

## Single-Cycle Implementation

In a **single-cycle** processor, every instruction completes in exactly one clock period. All five stages (IF, ID, EX, MEM, WB) execute within a single clock edge.

### How It Works

The clock period must be long enough to accommodate the **slowest possible instruction**. In RISC-V, that is typically a load (`LW`), which must:

1. Read instruction memory (IF)
2. Read the register file (ID)
3. Compute the address in the ALU (EX)
4. Read data memory (MEM)
5. Write back to the register file (WB)

If each sub-operation takes 200 ps, 150 ps, 200 ps, 200 ps, and 100 ps respectively, the critical path is 850 ps, so the clock period must be at least 850 ps — giving a clock frequency of ~1.18 GHz.

```
Clock period: |──────────────── 850 ps ────────────────|
ADD: [IF][ID][EX][  idle  ][WB]   ← MEM stage unused but still "waits"
LW:  [IF][ID][EX][MEM     ][WB]   ← uses every stage
```

An `ADD` instruction only needs 750 ps (no MEM stage), but it still occupies the full 850 ps clock period. **Time is wasted for faster instructions.**

### Advantages

- **Simplest control logic.** No need to track instruction state across cycles.
- **Easy to reason about.** Each instruction is completely independent in time.
- **No hazards.** Each instruction fully completes before the next begins.

### Disadvantages

- **Clock frequency is limited by the slowest instruction.** All instructions pay the penalty of the worst case.
- **Hardware is duplicated or idle.** Instruction memory and data memory could be unified in hardware, but doing so creates a structural hazard — a single-cycle processor with unified memory must use two ports or stall.
- **Poor performance.** CPI = 1, but with a slow clock.

## Multi-Cycle Implementation

In a **multi-cycle** processor, each stage takes one clock cycle, and instructions take as many cycles as they actually need. State is held in pipeline registers between cycles.

### How It Works

Each functional unit (memory, ALU, register file) is used in the cycle it is needed, then released. An `ADD` might take 4 cycles; a `LW` takes 5 cycles.

```
Cycle:       1    2    3    4    5
ADD:        [IF] [ID] [EX] [WB]
LW:         [IF] [ID] [EX] [MEM] [WB]
Branch:     [IF] [ID] [EX]
```

The clock period is now set by the **slowest single stage**, not the slowest full instruction. If the MEM stage is the bottleneck at 200 ps, the clock runs at 5 GHz.

### Advantages

- **Higher clock frequency.** Only one stage per cycle must complete within the clock period.
- **Resource sharing.** A single memory unit serves both instruction fetch (cycle 1) and data access (cycle 4) on different clock edges — no duplication needed.
- **Variable CPI by instruction type.** Simple instructions finish sooner.

### Disadvantages

- **More complex control unit.** The controller must be a finite state machine (FSM) that tracks which cycle within an instruction it is in.
- **Still no overlapping.** Only one instruction is in flight at a time — hardware sits idle when not used by the current instruction.
- **CPI > 1.** Even though the clock is faster, each instruction takes multiple cycles.

## Performance Comparison

Using the Patterson & Hennessy classic example with a typical instruction mix:

| Instruction | Frequency | Single-Cycle cycles | Multi-Cycle cycles |
|---|---|---|---|
| R-type | 44% | 1 (at 850 ps) | 4 (at 200 ps) |
| Load | 26% | 1 (at 850 ps) | 5 (at 200 ps) |
| Store | 12% | 1 (at 850 ps) | 4 (at 200 ps) |
| Branch | 18% | 1 (at 850 ps) | 3 (at 200 ps) |

**Average single-cycle time per instruction:** 850 ps  
**Average multi-cycle time per instruction:** (0.44×4 + 0.26×5 + 0.12×4 + 0.18×3) × 200 ps = 4.04 × 200 = **808 ps**

The multi-cycle design wins here by a small margin, but the real advantage of multi-cycle thinking is that it enables **pipelining**.

## The Natural Evolution: Pipelining

Pipelining takes the multi-cycle idea one step further: rather than waiting for one instruction to finish before starting the next, the processor starts a new instruction every cycle, overlapping all five stages simultaneously.

```
Cycle:      1    2    3    4    5    6    7
Instr 1:   [IF] [ID] [EX] [MEM][WB]
Instr 2:        [IF] [ID] [EX] [MEM][WB]
Instr 3:             [IF] [ID] [EX] [MEM][WB]
```

In steady state, a 5-stage pipeline completes one instruction per cycle (CPI ≈ 1) while keeping the clock period at single-stage latency — achieving the best of both worlds. Hazards (data, structural, control) are the cost that pipeline designers must manage.

## Common Pitfalls

- **Confusing CPI with clock frequency.** A single-cycle processor might have CPI = 1 but a slow clock; a pipelined processor has CPI ≈ 1 with a fast clock. The product (CPI × clock period) is what matters.
- **Assuming multi-cycle is always better.** For very short pipelines or workloads dominated by slow-path instructions, the FSM complexity may outweigh the benefit.
- **Forgetting structural hazards in single-cycle.** Using a single unified memory requires two simultaneous accesses (instruction + data) in the same cycle, which forces either dual-ported memory or a stall.

> **Interview answer:** A single-cycle processor completes every instruction in one long clock period sized for the worst-case path, giving CPI = 1 but a slow clock. A multi-cycle processor breaks execution into stages with a shorter clock period, uses variable cycles per instruction, and shares hardware — naturally leading to pipelining, where multiple instructions overlap in the same hardware.
