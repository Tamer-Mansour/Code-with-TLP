# Combinational vs Sequential Logic

Digital circuits divide cleanly into two families based on one question: **does the output depend only on current inputs, or also on past inputs?**

## Combinational Logic

A **combinational circuit** has no memory. The output is a pure function of the present inputs — change the inputs, the output changes immediately (minus propagation delay).

**Defining property**: `Output = f(current inputs)`

Examples:
- Logic gates, half adder, full adder
- Multiplexer, decoder, encoder
- ALU arithmetic path (addition, AND, OR)
- Priority encoder

```
       ┌─────────────┐
A ────►│             │
B ────►│  Comb. Logic│────► Output
C ────►│             │
       └─────────────┘
       (no feedback, no clock)
```

### Timing Concern: Propagation Delay

Every gate introduces a small delay (typically 50–500 ps in modern CMOS). A chain of gates accumulates delay — this is the **critical path** and limits the maximum clock frequency:

```
f_max = 1 / (t_setup + t_critical_path + t_clock_skew)
```

## Sequential Logic

A **sequential circuit** contains memory elements (latches or flip-flops). The output depends on both current inputs **and** the stored **state**.

**Defining property**: `Next state = f(current inputs, current state)`

```
       ┌─────────────┐
A ────►│             │────► Output
       │  Comb. Logic│
       │             │◄──── State (feedback)
       └──────┬──────┘
              │
         ┌────▼────┐
         │  Memory │  (flip-flops, latches)
         └─────────┘
              ▲
           Clock
```

Examples:
- Registers, counters
- CPU pipeline stages
- Finite state machines (FSMs)
- DRAM row-address circuitry

## Synchronous vs Asynchronous Sequential

| Feature | Synchronous | Asynchronous |
|---------|-------------|--------------|
| State changes on | Clock edge | Any input change |
| Easier to design? | Yes | No |
| Used in? | Almost all CPUs | Some controllers, PLLs |
| Hazard risk | Low (clock guards) | High (glitches) |

Modern CPUs are almost exclusively **synchronous** — all flip-flops share a global clock so state updates are predictable and analyzable.

## Setup and Hold Time

Flip-flops have two timing requirements:

- **Setup time** (`t_su`): the data input must be stable for this long **before** the clock edge.
- **Hold time** (`t_h`): the data input must remain stable for this long **after** the clock edge.

Violating either causes **metastability** — the flip-flop output oscillates between 0 and 1 unpredictably, potentially crashing the entire system.

```
Data: ──────┤ t_su ┤EDGE┤ t_h ┤──────
Clock:               ↑
```

## Worked Example: 1-Bit Accumulator

Combinational part: `sum = A + reg_out` (full adder)
Sequential part: a D flip-flop stores `sum` on each clock edge.

```
        ┌──────────┐      ┌────────┐
A ─────►│ Full     │─────►│  D FF  │──► Q (accumulated sum)
        │ Adder    │      │        │
        └──────────┘      └────────┘
             ▲                 │
             └─────────────────┘ (feedback)
```

Without the flip-flop, the circuit would oscillate because the adder output feeds back into its own input. The clock-gated flip-flop breaks that loop by sampling once per cycle.

## Key Differences at a Glance

| Property | Combinational | Sequential |
|----------|--------------|------------|
| Memory? | No | Yes |
| Depends on past? | No | Yes |
| Needs clock? | No | Usually |
| Described by? | Truth table | State diagram |
| Example | Adder | Counter |

## Common Pitfalls

- **Forgetting feedback = sequential**: any circuit with a loop back through memory is sequential, even if it looks "simple."
- **Glitches in combinational output**: momentary wrong outputs during input transitions are normal and harmless — unless fed into a flip-flop during the setup window.
- **Hold-time violations** are harder to fix than setup violations: hold violations cannot be fixed by reducing the clock speed.

## Interview Answer

> "Combinational logic outputs are a pure function of current inputs — no memory. Sequential logic adds state stored in flip-flops so outputs depend on history. Almost all real CPU components mix both: combinational logic computes the next state, and flip-flops register it on each clock edge."
