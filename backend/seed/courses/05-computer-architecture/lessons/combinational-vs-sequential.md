# Combinational vs Sequential Logic

Digital circuits fall into two fundamental categories. Combinational logic computes outputs purely from current inputs. Sequential logic adds memory — outputs depend on both inputs and stored history. The CPU is a sequential machine built on a combinational datapath.

## Combinational Logic in Depth

A **combinational circuit** has outputs that are a pure Boolean function of its current inputs. There is no feedback, no storage, and no clock. Given identical inputs, you always get identical outputs.

### The ALU as Combinational Logic

The Arithmetic Logic Unit is the largest combinational block in a CPU. For a 1-bit ALU slice performing ADD, AND, and OR:

```
Inputs:  A, B, CarryIn, Op[1:0]
Outputs: Result, CarryOut

Sum    = A XOR B XOR CarryIn
CarryOut = (A AND B) OR (B AND CarryIn) OR (A AND CarryIn)
Result = MUX(Sum, A AND B, A OR B, 0)  depending on Op
```

All of this is pure combinational logic — no flip-flops required.

### Decoder

An N-to-2^N decoder takes an N-bit address and asserts exactly one of 2^N output lines. A 2-to-4 decoder:

```
A1 | A0 | Y3 | Y2 | Y1 | Y0
 0 |  0 |  0 |  0 |  0 |  1
 0 |  1 |  0 |  0 |  1 |  0
 1 |  0 |  0 |  1 |  0 |  0
 1 |  1 |  1 |  0 |  0 |  0

Yi = 1 only when (A1,A0) = binary representation of i
```

The register file uses a decoder to select which register to write.

### 2-to-1 Multiplexer (MUX)

```
Output = (NOT S AND A) OR (S AND B)

S=0 → output is A
S=1 → output is B
```

MUXes are the CPU's routing switches. They appear in: selecting ALU operands, choosing the PC source (PC+4 vs branch target), and routing load data vs ALU result to the register write port.

### Priority Encoder

Takes N inputs and outputs the binary index of the highest-priority active input. Used in interrupt controllers and arbiters.

### Propagation Delay

Combinational circuits have **propagation delay** — the time from input change to stable output. Gate delays add up along a path. The longest path (critical path) sets the minimum clock period for any synchronous system that uses this circuit.

```
Example: 8-bit ripple-carry adder
  Each full adder: ~2 gate delays for Sum, ~3 for Carry
  8-bit carry chain: 8 × 3 = 24 gate delays for the final carry
  At 200 ps per gate delay: 24 × 200 ps = 4.8 ns → max clock ~208 MHz

  A carry-lookahead adder reduces carry to ~4 gate delays:
  4 × 200 ps = 0.8 ns → max clock ~1.25 GHz for just this unit
```

## Sequential Logic in Depth

A **sequential circuit** has **memory** — its output depends on both current inputs and stored state. Storage is implemented with feedback.

### The SR Latch (NOR Implementation)

Two NOR gates connected in a feedback loop:

```
         S ─────┬──── NOR1 ────┬──── Q
                │              │
         R ─────┴──── NOR2 ────┴──── Q'
```

Truth table (NOR-based):

```
S | R | Q (next) | Q' (next) | Notes
1 | 0 |    1     |     0     | Set
0 | 1 |    0     |     1     | Reset
0 | 0 |  Q_prev  |  Q'_prev  | Hold
1 | 1 |    0     |     0     | Forbidden (both = 0, contradicts Q ≠ Q')
```

**Why the hold state works**: when S=0, R=0, NOR1's output depends on R=0 and Q'. NOR2's output depends on S=0 and Q. The circuit is in a stable loop — each gate reinforces the other's output.

### NAND-Based SR Latch

Uses active-LOW inputs (S=0 means "set", R=0 means "reset"):

```
S' | R' | Q | Notes
 0 |  1 |  1 | Set  (S' active)
 1 |  0 |  0 | Reset (R' active)
 1 |  1 | Q_prev | Hold
 0 |  0 | FORBIDDEN
```

### Gated D Latch

Eliminates the forbidden state. Single data input D plus an Enable (EN):

```
D | EN | Q_next
0 |  1 |   0    ← Q follows D
1 |  1 |   1    ← Q follows D
X |  0 | Q_prev ← Q holds
```

Implementation: `Q_next = EN·D + EN'·Q`

The gate is **transparent** when EN=1 (Q tracks D in real time) and **opaque** when EN=0. This is level-sensitive behavior — any glitch on D while EN is HIGH propagates to Q.

## Clocked Systems and the Clock Signal

Synchronous systems drive all flip-flops from the same global **clock**. Every rising edge is a "heartbeat" at which all registers simultaneously capture their inputs.

```
Clock waveform:
                     ↓rising  ↓rising  ↓rising
CLK:     ___________↑‾‾‾‾‾‾‾↓_______↑‾‾‾‾‾‾‾↓_______

Period T = 1/f    (e.g., T = 0.333 ns at 3 GHz)
```

Key timing parameters:

| Parameter | Meaning | Typical Value |
|-----------|---------|---------------|
| Setup time (t_su) | D must be stable before rising edge | 50–200 ps |
| Hold time (t_h) | D must remain stable after rising edge | 10–50 ps |
| Clock-to-Q (t_pcq) | Q becomes valid after rising edge | 100–300 ps |
| Max combinational delay | t_period − t_pcq − t_su | Determines max clock speed |

**Timing budget example** at 3 GHz (T = 333 ps):

```
Max combinational delay = 333 - 150 (t_pcq) - 100 (t_su) = 83 ps

That's very tight! Hence modern CPUs pipeline deeply:
each stage has a small combinational block (one ALU operation, one MUX, etc.)
```

## Registers

A **register** is N D flip-flops sharing clock and (optionally) write-enable:

```
4-bit register with write-enable (WE):

For each bit i:
  D_ff = WE ? D_in[i] : Q[i]   ← MUX on D input
  Q[i] updated on rising CLK edge
```

A 32-bit register file with 32 registers and two read ports / one write port:

```
Read port 1: addr1[4:0] → decoder → assert 1 of 32 word-lines → drive data1[31:0]
Read port 2: addr2[4:0] → decoder → assert 1 of 32 word-lines → drive data2[31:0]
Write port:  addr_wr[4:0] → decoder → WE gate on target flip-flops → D_in[31:0]
```

Both reads happen combinationally (same cycle). The write happens on the next clock edge.

## Finite State Machines

A sequential circuit with a fixed set of states is a **Finite State Machine (FSM)**. The CPU's control unit is itself an FSM (or microsequencer). A 2-bit saturating up/down counter (as used in branch predictors) is a classic example:

```
States: 00 (strongly not-taken), 01 (weakly not-taken),
        10 (weakly taken), 11 (strongly taken)

Transitions (on branch outcome):
  outcome=taken:    state = min(state + 1, 11)
  outcome=not-taken: state = max(state - 1, 00)
```

This 2-bit counter correctly predicts repetitive branches (loops taken 10 times → predicts "taken" after the first miss).

## Summary

| Property | Combinational | Sequential |
|----------|---------------|------------|
| Memory | None | Yes (flip-flops) |
| Output depends on | Current inputs only | Inputs + stored state |
| Clock needed | No | Yes (synchronous) |
| Key building block | NAND/NOR gates, MUX | D flip-flop |
| CPU example | ALU, decoder, MUX | Register file, PC, pipeline registers |
| Critical parameter | Propagation delay | Setup/hold time + clock period |

Every stage of the CPU pipeline is a combinational block sandwiched between sequential (flip-flop) registers. The clock orchestrates the flow of data through this chain, one pipeline stage per cycle.
