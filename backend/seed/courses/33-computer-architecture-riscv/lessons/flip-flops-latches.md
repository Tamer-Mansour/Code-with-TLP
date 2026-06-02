# Latches and Flip-Flops

Sequential logic needs a way to **store one bit**. Two related but distinct devices do this: **latches** (level-sensitive) and **flip-flops** (edge-triggered). Understanding the difference is essential for both hardware design and debugging timing problems.

## The SR Latch — Simplest Memory Element

Built from two cross-coupled NAND (or NOR) gates:

```
NOR-based SR Latch:
  S ──►[NOR]──► Q
         ▲
  R ──►[NOR]──► Q̄
```

| S | R | Q (next) | Comment |
|---|---|----------|---------|
| 0 | 0 | Q (hold) | Remember previous state |
| 1 | 0 | 1        | Set |
| 0 | 1 | 0        | Reset |
| 1 | 1 | **Forbidden** | Q and Q̄ both 0 — undefined on release |

The forbidden state arises when both outputs are forced to the same value; when S and R both return to 0 simultaneously, the latch may settle to either state unpredictably.

## The D Latch (Transparent Latch)

The SR latch's forbidden state is eliminated by tying `R = S̄` and adding an **enable** line:

```
D ──┤ NOT ├──► R
│                  SR Latch ──► Q
└──────────► S     (when EN=1, Q follows D)
                   (when EN=0, Q holds)
```

| EN | D | Q (next) |
|----|---|----------|
| 1  | 0 | 0 (transparent) |
| 1  | 1 | 1 (transparent) |
| 0  | X | Q (hold)        |

**Problem**: while `EN=1`, the latch is transparent — Q follows D continuously. This makes timing analysis difficult and can cause glitches to propagate.

## D Flip-Flop (Edge-Triggered)

The D flip-flop samples D **only at the rising (or falling) clock edge**, then holds the value regardless of D changes. It is constructed from two D latches in a **master–slave** configuration:

```
       Master             Slave
D ──►[ D Latch ]──►[ D Latch ]──► Q
      EN=CLK            EN=CLK̄
```

When `CLK` goes high: master is transparent (samples D), slave is opaque (holds Q).
When `CLK` goes low: master holds, slave is transparent (Q updates to master value).

Result: Q changes only on the **rising edge** of CLK.

### Timing Parameters

| Parameter | Meaning |
|-----------|---------|
| `t_setup` | D must be stable this long **before** the clock edge |
| `t_hold` | D must be stable this long **after** the clock edge |
| `t_clk-to-Q` | Delay from clock edge to Q valid |
| `t_propagation` | Gate delay through combinational logic between flip-flops |

Critical path constraint:
```
t_clk_period ≥ t_clk-to-Q + t_propagation + t_setup
```

## JK Flip-Flop

Extends the SR flip-flop by defining a useful behavior for the J=K=1 case:

| J | K | Q (next) |
|---|---|----------|
| 0 | 0 | Q (hold) |
| 0 | 1 | 0 (reset) |
| 1 | 0 | 1 (set) |
| 1 | 1 | Q̄ (**toggle**) |

The toggle mode makes JK flip-flops natural building blocks for **binary counters** — connect Q̄ back to J=K and the output toggles on every clock edge.

## T Flip-Flop (Toggle)

A simplified JK with J=K tied together:

| T | Q (next) |
|---|----------|
| 0 | Q (hold) |
| 1 | Q̄ (toggle) |

Used directly as counter stages.

## Worked Example: Detecting a Rising Edge in Software

Even in software, we emulate flip-flop behavior when detecting button press edges:

```c
uint8_t prev = 0;
uint8_t curr = read_pin();

if (curr == 1 && prev == 0) {
    // Rising edge detected — equivalent to what a D FF captures
    handle_press();
}
prev = curr;
```

The variable `prev` plays the role of `Q`, and the if-condition is the "edge detector" logic.

## Latch vs Flip-Flop Summary

| Property | Latch | Flip-Flop |
|----------|-------|-----------|
| Sensitive to | Level (EN high/low) | Edge (↑ or ↓) |
| Transparent? | Yes (when EN=1) | No |
| Timing analysis | Harder | Straightforward |
| Used in | Asynchronous, low-power | Synchronous CPUs |
| Hazard risk | Higher | Lower |

## Common Pitfalls

- **Inferred latches in HDL**: in Verilog/VHDL, an `if` without an `else` inside a combinational block inadvertently infers a latch. Always assign all outputs in every branch.
- **Hold-time violations**: unlike setup violations, you cannot fix hold violations by slowing the clock. They require inserting delay buffers on the data path.
- **Metastability**: any time an asynchronous signal is sampled (e.g., a button press), there is a nonzero probability the flip-flop enters a metastable state. Mitigate with a two-stage synchronizer.

## Interview Answer

> "A latch is level-sensitive — it passes data while its enable is high. A flip-flop is edge-triggered — it samples data only at the clock edge and holds it otherwise. CPUs use edge-triggered flip-flops because they make timing analysis tractable: state changes exactly once per clock cycle."
