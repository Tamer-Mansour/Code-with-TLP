# Performance Metrics: CPI, IPC, and Clock Speed

Processor performance is determined by three interacting factors. Understanding each independently — and how they multiply together — lets you reason clearly about benchmarks, hardware comparisons, and optimization targets.

## The CPU Performance Equation

```
Execution Time = Instruction Count × CPI × Clock Period
               = Instruction Count × CPI / Clock Frequency
```

Every term in this equation can be optimized, but they are not independent. Improving one often worsens another.

## Clock Frequency (f)

The clock is a square wave that synchronizes all activity inside the processor. Each rising edge triggers one pipeline stage's worth of work.

- **Unit:** Hertz (Hz). Modern CPUs run at 3–5 GHz (3–5 billion cycles per second).
- **Clock period:** T = 1/f. At 4 GHz, T = 0.25 nanoseconds.
- **Limit:** The longest combinational logic path in any pipeline stage (the *critical path*) must complete within one clock period. Shortening this path — by splitting stages or using faster transistors — allows higher frequencies.

Increasing clock frequency alone does not improve performance if the work per cycle decreases proportionally. This is why naive "more MHz = faster" reasoning fails for comparing CPUs with different microarchitectures.

## CPI — Cycles Per Instruction

CPI is the average number of clock cycles the processor spends executing one instruction.

```
CPI = Total Cycles / Total Instructions
```

| Scenario | Typical CPI |
|---|---|
| Simple in-order RISC (no stalls) | 1.0 |
| Pipeline stalls (data hazards) | 1.1 – 2.0 |
| Cache misses (memory-bound code) | 5 – 50+ |
| Out-of-order superscalar (good code) | 0.3 – 0.8 |

CPI below 1.0 is possible when a superscalar processor **issues multiple instructions per cycle**.

### What increases CPI (bad)

- **Data hazards** — instruction depends on a result not yet written back.
- **Control hazards** — branch misprediction flushes the pipeline (10–20 cycle penalty).
- **Cache misses** — L1 miss: ~4 cycles; L2 miss: ~12 cycles; LLC miss: ~200 cycles; DRAM: ~300 cycles.
- **Structural hazards** — two instructions need the same execution unit simultaneously.

## IPC — Instructions Per Cycle

IPC is the reciprocal of CPI and is often used when comparing CPU microarchitectures.

```
IPC = 1 / CPI = Instructions executed / Cycles taken
```

Higher IPC means the processor does more useful work each cycle. Superscalar processors (multiple issue slots) and out-of-order execution both raise IPC. A modern high-performance core may reach IPC of 4–6 for well-behaved integer code.

**Important:** IPC is meaningless without fixing the benchmark. A processor with IPC = 4 on a trivial loop may have IPC = 1.2 on a cache-miss-heavy workload.

## Instruction Count (IC)

The number of instructions a program executes depends on:
- The **algorithm** chosen.
- The **compiler optimizations** applied.
- The **ISA** — a CISC instruction (e.g., `REP MOVSB`) may do the work of many RISC instructions.

## Worked Example

A program executes 2 billion instructions. The processor runs at 3 GHz with a measured CPI of 1.5.

```
Execution Time = IC × CPI / f
               = 2×10⁹ × 1.5 / 3×10⁹
               = 1.0 second
```

After cache optimization, CPI drops to 1.0:

```
New Time = 2×10⁹ × 1.0 / 3×10⁹ = 0.667 seconds
Speedup  = 1.0 / 0.667 = 1.5×
```

The clock frequency was unchanged. The speedup came entirely from reducing stall cycles (improving CPI).

## Common Pitfalls

- **"GHz = performance"** — wrong. A 4 GHz processor with CPI = 2.0 is slower than a 3 GHz processor with CPI = 0.8 on the same workload.
- **"IPC is fixed"** — wrong. IPC is workload-dependent. A CPU that claims "IPC of 5" achieves this only on specific synthetic benchmarks.
- **Ignoring instruction count** — a compiler that generates fewer, more complex instructions can make CPI look worse while cutting total execution time.

```python
# Estimating execution time from specs
ic  = 2e9    # instruction count
cpi = 1.5    # cycles per instruction
f   = 3e9    # clock frequency (Hz)

exec_time = ic * cpi / f
print(f"Execution time: {exec_time:.3f} s")  # 1.000 s
```

> **Interview answer:** "Execution time equals instruction count times CPI divided by clock frequency. CPI captures the average pipeline stall burden — cache misses and branch mispredictions push it up. IPC is 1/CPI. A high-IPC, lower-frequency core can outperform a low-IPC, higher-frequency core. You must consider all three factors together."
