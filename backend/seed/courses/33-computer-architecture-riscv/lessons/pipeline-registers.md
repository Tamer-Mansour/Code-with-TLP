# Pipeline Registers and Stage Balancing

A pipeline is not just conceptual — it requires real hardware between each stage to hold intermediate results. These **pipeline registers** are what make overlapped execution physically possible. Getting their design right, and balancing the work across stages, determines the maximum clock frequency the processor can achieve.

## What Are Pipeline Registers?

At the end of each clock cycle, each pipeline stage must "hand off" its results to the next stage without losing them — because on the very next cycle, the previous stage will start processing a new instruction and will overwrite those results.

Pipeline registers are banks of flip-flops that latch all the values a stage produces and hold them for one cycle, presenting them as inputs to the next stage.

In a five-stage pipeline the registers are named after the two stages they connect:

| Register | Between stages | Holds |
|----------|---------------|-------|
| IF/ID | IF → ID | Fetched instruction bits, PC+4 |
| ID/EX | ID → EX | Decoded control signals, register values, immediate, PC+4 |
| EX/MEM | EX → MEM | ALU result, zero flag, write data, control signals |
| MEM/WB | MEM → WB | Memory read data or ALU result, destination register number |

## What Flows Through the Registers

```
IF/ID  : [ instruction[31:0] | PC+4 ]

ID/EX  : [ control_signals | rs1_val | rs2_val | imm | rd | PC+4 ]

EX/MEM : [ control_signals | alu_result | zero | rs2_val | rd ]

MEM/WB : [ control_signals | read_data | alu_result | rd ]
```

Control signals (MemRead, MemWrite, RegWrite, etc.) are generated in ID and must travel down the pipeline alongside the instruction they belong to. A common mistake is forgetting to propagate control signals through intermediate registers.

## Stage Balancing

The clock period is determined by the **slowest stage**. Every stage must complete its work within one clock period. If stages have unequal delays, the clock must accommodate the worst case:

```
Clock period = max(t_IF, t_ID, t_EX, t_MEM, t_WB) + t_register_overhead
```

### Example of Imbalanced Stages

Suppose stage delays are (in ns): IF=2, ID=1, EX=3, MEM=2, WB=1.

- The EX stage dominates at 3 ns
- Clock period = 3 ns + 0.1 ns overhead = 3.1 ns
- Stages IF, ID, MEM, WB all sit idle for part of each cycle — wasted silicon

### Consequences of Imbalance

- Faster stages waste time waiting for the clock edge
- The processor runs at the frequency of the slowest stage
- A 5-stage pipeline with stages of [1, 1, 5, 1, 1] ns runs at 5 ns/cycle, giving no benefit over a 3-stage pipeline grouping the slow stage

### Fixing Imbalance: Sub-pipelining

One solution is to split a slow stage into two or more sub-stages, each short enough to fit within the target clock period. This increases the pipeline depth and adds one more pipeline register, but allows a faster clock.

```
Original: IF(2) | ID(1) | EX(3) | MEM(2) | WB(1)
                            ↓ split EX
Revised:  IF(2) | ID(1) | EX1(1.5) | EX2(1.5) | MEM(2) | WB(1)
          Clock = 2 ns → 33% speedup
```

## Forwarding Paths and Pipeline Registers

Pipeline registers also enable **data forwarding** (bypassing), the primary technique for resolving data hazards without stalling. The EX/MEM and MEM/WB registers hold results that can be forwarded back to the EX stage inputs:

```
         EX/MEM.ALU_result ──┐
                             ├──> MUX → ALU input A or B
         MEM/WB.read_data  ──┘
```

Without forwarding, every data dependency would require stalls — killing pipeline performance.

## Common Pitfall: Forgetting Register Numbers in WB

The destination register number (rd) must be carried all the way from ID through to WB in the pipeline registers. If it is not explicitly stored in EX/MEM and MEM/WB, the write-back stage does not know which register to update.

> **Interview answer:** Pipeline registers are flip-flop banks between each stage that latch all results and control signals at the end of every clock cycle, enabling the next stage to process the previous instruction's output while the current stage works on a new instruction; stage balancing ensures no single stage becomes the bottleneck that limits clock speed.
