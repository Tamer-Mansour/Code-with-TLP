# Introduction to Pipelining

Pipelining is the most impactful performance technique in CPU design. It applies the assembly-line principle to instruction execution: while one instruction is in the execute stage, the next is being decoded, and the one after that is being fetched — all simultaneously.

## The Assembly-Line Analogy

Imagine a car assembly line with three stations: weld (60 min), paint (40 min), inspect (20 min). Without pipelining:

```
Car 1: [60-weld][40-paint][20-inspect]
Car 2:                                [60-weld][40-paint][20-inspect]
3 cars: 3 × 120 = 360 min
```

With pipelining (start painting car 1 as soon as it leaves welding):

```
Time:   0   60  100 120 160 180 220 240
Car 1: [weld][paint][insp]
Car 2:       [weld ][paint][insp]
Car 3:              [weld ][paint][insp]
Total: 240 min (vs 360 min) — throughput approaches 1 car / 60 min
```

The bottleneck is the **slowest stage** (welding at 60 min), not the total latency.

## The Classic 5-Stage RISC Pipeline

```
Stage 1: IF  — Instruction Fetch     (read instruction from I-cache)
Stage 2: ID  — Instruction Decode    (read registers, generate control signals)
Stage 3: EX  — Execute               (ALU operation or address computation)
Stage 4: MEM — Memory Access         (load from or store to D-cache)
Stage 5: WB  — Write Back            (write result to register file)
```

### Timing Diagram: 5 Instructions, No Hazards

```
Cycle:  |  1  |  2  |  3  |  4  |  5  |  6  |  7  |  8  |  9  |
I1:     | IF  | ID  | EX  | MEM | WB  |     |     |     |     |
I2:     |     | IF  | ID  | EX  | MEM | WB  |     |     |     |
I3:     |     |     | IF  | ID  | EX  | MEM | WB  |     |     |
I4:     |     |     |     | IF  | ID  | EX  | MEM | WB  |     |
I5:     |     |     |     |     | IF  | ID  | EX  | MEM | WB  |
```

From cycle 5 onward, one instruction **completes per cycle** (CPI = 1 ideally). The non-pipelined equivalent would take 5 × 5 = 25 cycles for 5 instructions.

## Ideal Speedup Formula

If a non-pipelined CPU takes T cycles per instruction and we split it into K equal stages:

```
Throughput_pipelined = 1 instruction / (T/K) seconds
Speedup_ideal = K

For K = 5: ideal speedup = 5× over single-cycle
```

In practice, stages are not perfectly balanced (some take longer than others), and hazards reduce throughput. Actual speedup is 3–4× for a 5-stage pipeline.

## Pipeline Registers

Between each stage, **pipeline registers** latch the values produced by the current stage. On each rising clock edge, values advance one stage. This prevents stages from interfering with each other.

```
IF/ID register   — holds: fetched instruction[31:0], PC+4
                          (populated at end of cycle 1 for I1)

ID/EX register   — holds: register data1, register data2,
                          sign-extended immediate, rd[4:0],
                          ALL control signals (RegWrite, ALUSrc, ...)
                          (populated at end of cycle 2 for I1)

EX/MEM register  — holds: ALU result[31:0], zero flag,
                          rs2 data (for stores), rd[4:0],
                          remaining control signals
                          (populated at end of cycle 3 for I1)

MEM/WB register  — holds: memory read data (if load) OR ALU result,
                          rd[4:0], MemToReg, RegWrite
                          (populated at end of cycle 4 for I1)
```

The control signals generated in ID must travel with the instruction through all subsequent pipeline stages — they are stored in the pipeline registers, not in centralized latches.

## Latency vs Throughput — An Important Distinction

| Metric | Non-pipelined (5-cycle instruction) | 5-stage pipelined |
|--------|--------------------------------------|-------------------|
| Latency (single instruction) | 5 cycles | 5 cycles (unchanged) |
| Throughput (steady state) | 1/5 instruction per cycle | 1 instruction per cycle |

Pipelining improves **throughput** (instructions per second) but does **not** reduce the latency of a single instruction — it still takes 5 stages. This matters for: cache miss penalties (a missing load stalls the pipeline), interrupt response time, and out-of-order completion.

## Clock Frequency and Pipeline Depth

Each pipeline stage must complete its work within one clock period. The clock period is constrained by the **slowest stage** (critical path of that stage's combinational logic):

```
T_clock ≥ max(t_IF, t_ID, t_EX, t_MEM, t_WB) + t_pipeline_register

Example stage timings:
  t_IF  = 200 ps  (I-cache read)
  t_ID  = 100 ps  (decode + register read)
  t_EX  = 200 ps  (ALU)
  t_MEM = 200 ps  (D-cache read)
  t_WB  = 100 ps  (register write)
  t_pipeline_register ≈ 30 ps (flip-flop overhead)

Slowest stage: 200 ps + 30 ps = 230 ps → max clock ≈ 4.3 GHz
```

**Deeper pipelines** (more stages) allow higher clock frequencies: each stage does less work. Intel's Pentium 4 Prescott (2004) used a 31-stage pipeline to reach 4 GHz. But deeper pipelines increase the **branch misprediction penalty** (more stages to flush) and waste more energy on speculative work.

Modern CPUs (Apple M2, AMD Zen 4) use 12–20 stage pipelines, balancing clock speed against misprediction cost.

## Pipeline CPI Calculation

```
Effective CPI = Ideal CPI + Stall cycles per instruction
              = 1 + Stalls_load_use + Stalls_branch + Stalls_structural

Example:
  Load-use stalls:       0.05 instructions cause 1 stall = 0.05 cycles
  Branch stalls (2% mispredicted, 2-cycle penalty): 0.02 × 2 = 0.04 cycles
  Structural stalls:     negligible (separated I$/D$)

Effective CPI = 1 + 0.05 + 0.04 = 1.09
Performance = CPI × T_clock = 1.09 × 0.23 ns = 0.251 ns per instruction
IPC = 1/CPI ≈ 0.92 (instructions per cycle)
```

## Superscalar Pipelines (Modern CPUs)

Modern CPUs issue **multiple instructions per cycle** from multiple parallel pipelines. A 4-wide superscalar:

```
Cycle:  |  1  |  2  |  3  |  4  |  5  |  6  |
I1–I4:  | IF  | ID  | EX  | MEM | WB  |     |
I5–I8:  |     | IF  | ID  | EX  | MEM | WB  |
```

With 4 parallel pipelines (4 ALUs, 2 load/store units, 2 branch units), the theoretical CPI = 0.25 (= 4 instructions per cycle). Apple M2 is 8-wide; AMD Zen 4 is 6-wide.

Out-of-order execution allows instructions to execute in an order different from program order, keeping the execution units busy even when some instructions stall.

The next lesson covers the primary obstacle to ideal pipeline performance: **hazards**.
