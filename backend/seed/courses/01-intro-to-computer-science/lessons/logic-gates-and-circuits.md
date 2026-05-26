# Logic Gates and Circuits

Boolean operations are not just abstract mathematics—they are physically implemented in hardware as **logic gates**: tiny electronic circuits etched onto silicon chips. A modern CPU contains billions of transistors grouped into logic gates, which are combined into functional units (adders, registers, multiplexers), which form a complete processor. This lesson traces that path from individual gates all the way to the CPU.

## What Is a Logic Gate?

A **logic gate** is a circuit element that takes one or two binary inputs (voltage levels representing 0 or 1) and produces one binary output, according to a Boolean operation.

The underlying technology is the **transistor**. In CMOS (Complementary Metal-Oxide-Semiconductor) technology, a gate is built from two complementary transistor networks: one that pulls the output to a high voltage (1) and one that pulls it to a low voltage (0). Only one network is active at a time, which keeps power consumption very low—crucial when you have billions of gates on one chip.

## Standard Logic Gate Symbols and Behaviour

### NOT Gate (Inverter)

```
A ──[▷○]── Q = NOT A
```

The small circle (bubble) at the output indicates inversion.

| A | Q |
|---|---|
| 0 | 1 |
| 1 | 0 |

**CMOS implementation:** A single PMOS transistor (turns on when input is 0) in series with a single NMOS transistor (turns on when input is 1). It is the simplest gate.

### AND Gate

```
A ──┐
    [&]── Q = A AND B
B ──┘
```

| A | B | Q |
|---|---|---|
| 0 | 0 | 0 |
| 0 | 1 | 0 |
| 1 | 0 | 0 |
| 1 | 1 | 1 |

The output is HIGH only when **all** inputs are HIGH. An AND gate with three inputs is HIGH only when all three inputs are HIGH.

### OR Gate

```
A ──┐
    [≥1]── Q = A OR B
B ──┘
```

| A | B | Q |
|---|---|---|
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 1 |

### NAND Gate

```
A ──┐
    [&○]── Q = NOT (A AND B)
B ──┘
```

| A | B | Q |
|---|---|---|
| 0 | 0 | 1 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 0 |

NAND is the most commonly implemented gate because in CMOS it requires fewer transistors (4 vs. 6 for separate NOT + AND) and consumes less power. It is also **functionally complete**: any Boolean function can be built entirely from NAND gates.

### NOR Gate

```
A ──┐
    [≥1○]── Q = NOT (A OR B)
B ──┘
```

NOR is also functionally complete (used in early calculators and spacecraft computers for that reason).

### XOR Gate

```
A ──┐
    [=1]── Q = A XOR B
B ──┘
```

| A | B | Q |
|---|---|---|
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 0 |

XOR detects *difference*—it is HIGH when inputs differ. Internally, an XOR gate is built from 4 NAND gates, making it more complex than AND or OR.

## Building a Half Adder

Now we combine gates to perform a useful computation: **binary addition of two single bits**.

A **half adder** takes two 1-bit inputs (A and B) and produces two 1-bit outputs:
- **Sum**: the least significant bit of A + B
- **Carry**: the bit that carries over to the next column

| A | B | Sum | Carry |
|---|---|-----|-------|
| 0 | 0 |  0  |   0   |
| 0 | 1 |  1  |   0   |
| 1 | 0 |  1  |   0   |
| 1 | 1 |  0  |   1   |

Notice the pattern:
- **Sum** = A **XOR** B (1 when inputs differ)
- **Carry** = A **AND** B (1 only when both are 1)

Circuit:

```
A ──┬──[XOR]── Sum
B ──┤
    └──[AND]── Carry
```

Just two gates! The half adder uses exactly 1 XOR + 1 AND. This single circuit can be replicated and chained to add numbers of any width.

## Building a Full Adder

A **full adder** extends the half adder by also accepting a **carry-in** (Cin) from the previous bit position. This is what allows multi-bit addition.

Inputs: A, B, Cin
Outputs: Sum, Carry-out (Cout)

| A | B | Cin | Sum | Cout |
|---|---|-----|-----|------|
| 0 | 0 |  0  |  0  |   0  |
| 0 | 0 |  1  |  1  |   0  |
| 0 | 1 |  0  |  1  |   0  |
| 0 | 1 |  1  |  0  |   1  |
| 1 | 0 |  0  |  1  |   0  |
| 1 | 0 |  1  |  0  |   1  |
| 1 | 1 |  0  |  0  |   1  |
| 1 | 1 |  1  |  1  |   1  |

The formulas:
- **Sum** = A XOR B XOR Cin
- **Cout** = (A AND B) OR (Cin AND (A XOR B))

A full adder is built from two half adders and one OR gate.

## Chaining Full Adders: The Ripple-Carry Adder

To add two *n*-bit numbers, chain *n* full adders in series, passing the carry-out of each into the carry-in of the next.

```
Bit 0:  A₀, B₀, Cin=0  → Sum₀, C₁
Bit 1:  A₁, B₁, Cin=C₁ → Sum₁, C₂
Bit 2:  A₂, B₂, Cin=C₂ → Sum₂, C₃
...
Bit 7:  A₇, B₇, Cin=C₇ → Sum₇, C₈  (C₈ = overflow bit)
```

8 full adders give you an **8-bit adder** that can add any two 8-bit numbers. Scale to 64 bits and you have the core arithmetic unit of a 64-bit CPU.

The name "ripple-carry" comes from the way the carry *ripples* from bit 0 to bit n−1. Modern CPUs use more complex designs (carry lookahead, parallel prefix adders) that compute the carry bits without waiting, enabling higher clock speeds.

## From Adders to ALUs

A **full Arithmetic Logic Unit (ALU)** combines:
- An adder (and subtractor, which reuses the adder via two's complement)
- AND, OR, XOR logic units operating on all bits in parallel
- A comparator (to check equality or ordering)
- A barrel shifter (for left/right bit shifts)
- A multiplexer that selects which operation's result to output

The ALU is controlled by a 3–6 bit **opcode** signal from the control unit. Different opcodes select addition, subtraction, AND, OR, etc.

## Combinational vs Sequential Circuits

| Type | Output depends on | Has memory? | Example |
|------|------------------|-------------|---------|
| **Combinational** | Current inputs only | No | AND/OR gates, adder, multiplexer |
| **Sequential** | Inputs AND past state | Yes | Flip-flops, registers, RAM cells |

### Flip-Flops: How Memory Is Built

A **D flip-flop** (the simplest type) stores a single bit. It has:
- A data input D
- A clock input CLK
- An output Q (the stored bit)

On each rising edge of the clock signal, Q captures the value of D and holds it until the next clock edge. This is how a **register** (a small group of flip-flops) stores a number between clock cycles.

A typical 64-bit CPU register is just 64 D flip-flops wired in parallel.

Build 8 × 1 KB rows of flip-flops, add address decoding circuitry, and you have a tiny static RAM (SRAM) cell—the same technology used in CPU caches.

## The Complete Hierarchy

```
Quantum mechanics / semiconductor physics
      ↓
Transistors  (billions of on/off switches, ~5 nm in 2024)
      ↓
Logic gates  (NOT, AND, OR, NAND, XOR — built from 4–6 transistors each)
      ↓
Functional units  (adders, multiplexers, flip-flops, registers)
      ↓
ALU + Control Unit + Registers  →  CPU core
      ↓
Instruction Set Architecture (ISA)  (x86-64, ARM, RISC-V — the CPU's "language")
      ↓
Machine code  →  Assembly  →  C  →  Python
      ↓
Your program
```

Every `if x > 0:` you write in Python ultimately triggers a comparison in the ALU, which is a cascade of XOR and AND gates, which is CMOS transistors switching in nanoseconds.

## Common Misconceptions

**"Logic gates are just a teaching abstraction—real computers work differently."**
No—real CPUs are literally made of billions of logic gates. The gates are fabricated on silicon using photolithography, but they follow the same Boolean truth tables. Modern chips (like Apple's M3) contain over 25 billion transistors, forming tens of billions of logic gates.

**"XOR has nothing to do with addition."**
XOR *is* binary addition modulo 2 (without carry). The connection is fundamental: the Sum output of a half adder is exactly A XOR B.

**"NAND is just a more complex gate that circuit designers use for convenience."**
NAND is actually *simpler* to build in CMOS (4 transistors vs 6 for separate NOT+AND), which is why chip foundries optimise their NAND cells exhaustively. Everything else is built on top of it.

## Key Takeaways

- Logic gates are physical implementations of Boolean operations, built from transistors.
- The basic gates are **NOT, AND, OR, NAND, NOR, XOR**.
- **NAND** is functionally complete and the most common gate in real hardware.
- A **half adder** (XOR + AND) adds two bits; a **full adder** also handles carry-in; chaining 64 full adders makes a 64-bit adder.
- **Sequential circuits** (flip-flops, registers) store state and form the basis of memory.
- Every line of code you write eventually executes as gate operations on transistors.
