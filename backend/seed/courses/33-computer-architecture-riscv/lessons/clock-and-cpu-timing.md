# Clocking and CPU Timing

Every digital circuit in the CPU changes state in lockstep with a **clock signal** — a square wave that alternates between 0 and 1 at a fixed frequency. Understanding clocking is essential for understanding performance, power, and why pipelines work the way they do.

## What the Clock Does

The clock signal synchronizes state changes across the entire chip:

- **Combinational logic** (gates, muxes, ALU) computes continuously; its output settles after a **propagation delay**.
- **Sequential elements** (flip-flops, registers, pipeline latches) capture and hold a value only on the **rising edge** of the clock.

```
Clock:    ___    ___    ___    ___
         |   |  |   |  |   |  |   |
    ─────┘   └──┘   └──┘   └──┘   └──

         ↑ rising edge: registers capture input
```

Between two rising edges — one **clock period (T)** — all combinational logic must finish computing so that stable, correct values are present at the flip-flop inputs before the next edge.

## Critical Path and Maximum Clock Frequency

The **critical path** is the longest combinational delay path between any two sequential elements. It determines the minimum clock period:

```
T_min = t_setup + t_comb_critical + t_clk_to_Q
```

Where:
- `t_comb_critical` = delay through the longest gate chain
- `t_setup` = time the flip-flop input must be stable before the clock edge
- `t_clk_to_Q` = time after the clock edge until the flip-flop output is valid

Maximum frequency: **f_max = 1 / T_min**

### Example

Suppose the critical path in a single-cycle RISC-V CPU is through: instruction memory (200 ps) → register file read (100 ps) → ALU (200 ps) → data memory (200 ps) → register file write setup (50 ps).

```python
t_crit = 200 + 100 + 200 + 200 + 50  # ps
t_crit = 750  # ps

f_max = 1 / (750e-12)  # Hz
f_max = 1.33e9  # ≈ 1.33 GHz
```

To run faster, designers must shorten the critical path — achieved by pipelining (cutting the path into shorter stages).

## Single-Cycle vs Multi-Cycle vs Pipelined Timing

| Design | Clock Period | Cycles per Instruction (CPI) | Throughput |
|---|---|---|---|
| Single-cycle | Longest instruction's delay | 1 (always) | Low f × 1 |
| Multi-cycle | Longest single stage | Varies (4–5 for RISC-V) | Higher f ÷ avg CPI |
| Pipelined | Longest single stage | ~1 (ideal) | Higher f × ~1 |

Pipelining is the key insight: by splitting execution into 5 stages (IF, ID, EX, MEM, WB), each stage takes ~1/5 the time, allowing ~5× higher clock frequency at the same lithography node.

## Setup and Hold Times

Flip-flop correctness depends on two timing constraints:

- **Setup time (t_su):** Input must be stable for at least t_su *before* the clock edge.
- **Hold time (t_h):** Input must remain stable for at least t_h *after* the clock edge.

Violating setup time causes **metastability** — the flip-flop output is unpredictable. Violating hold time causes the flip-flop to capture the wrong (new) value.

```
Data:  ──XXXXXXXX|STABLE|XXXX──
Clock:           ↑
                 ├─t_su─┤  (data must be stable before ↑)
                 ├───t_h─┤ (data must be stable after ↑)
```

## Clock Skew and Its Problems

**Clock skew** is the difference in arrival time of the clock edge at different flip-flops due to wire delay variations. If skew is large:

- A fast path from FF1 to FF2 might arrive at FF2 *before* FF2's clock edge has advanced — causing FF2 to capture the old value (hold time violation).
- Timing closure (ensuring no violations across the chip) is a major part of physical design.

## Power and Clock Gating

Dynamic power in CMOS is: **P = α × C × V² × f**

Where α is activity factor (fraction of cycles where the node switches), C is capacitance, V is voltage, f is frequency.

**Clock gating** disables the clock to idle functional units, setting α = 0 for those units and eliminating switching power. Modern CPUs gate clocks at fine granularity — per pipeline stage, per functional unit, even per register.

```c
// Conceptual clock gating (hardware synthesizes this from enable signals)
if (unit_active) {
    clk_to_unit = global_clk;  // pass clock
} else {
    clk_to_unit = 0;           // gate it off
}
```

## Common Pitfalls

- **Equating clock speed with performance.** A 1 GHz pipelined CPU can outperform a 3 GHz unpipelined one if CPI is low enough. Always consider CPI alongside frequency.
- **Ignoring clock distribution.** Routing the clock to millions of flip-flops with equal skew consumes ~30–40% of chip power in some designs.
- **Assuming all cycles do useful work.** Stalls (cache misses, branches, data hazards) increase effective CPI above 1 even in a pipelined CPU.

## Interview Answer

> "The clock synchronizes all state changes in the CPU; the maximum clock frequency is set by the critical path (the longest combinational delay between two registers), and pipelining improves performance by cutting that path into shorter stages so each can run at a higher frequency."
