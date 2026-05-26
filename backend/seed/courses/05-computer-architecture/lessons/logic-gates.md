# Logic Gates: The Building Blocks of Digital Circuits

Every computation your CPU performs ultimately reduces to combinations of simple **logic gates** — electronic circuits that produce a binary output based on one or more binary inputs. This lesson goes deep: full truth tables, De Morgan derivations, multi-level gate networks, and how an actual ripple-carry adder emerges from first principles.

## Binary Signals

Digital circuits treat voltage levels as one of two values:

- **Logic 1 (HIGH)**: typically ~3.3 V or ~5 V
- **Logic 0 (LOW)**: typically ~0 V (ground)

A CMOS inverter (the most basic gate) uses a PMOS pull-up transistor and an NMOS pull-down transistor. When the input is HIGH, the NMOS conducts, pulling the output to 0 V. When the input is LOW, the PMOS conducts, pulling the output to VDD. All gates are built from similar pairs of transistors.

## The Basic Gates and Their Truth Tables

### NOT (Inverter)

One input, one output. The simplest gate — a single CMOS inverter pair.

```
A | NOT A
0 |   1
1 |   0
```

Boolean expression: `F = A'`  (apostrophe = NOT)

### AND

Outputs 1 only when **all** inputs are 1. Requires 6 transistors in CMOS (a NAND followed by an inverter is actually cheaper at 4+2 transistors).

```
A | B | A AND B
0 | 0 |    0
0 | 1 |    0
1 | 0 |    0
1 | 1 |    1
```

Boolean: `F = A · B`

### OR

Outputs 1 when **at least one** input is 1.

```
A | B | A OR B
0 | 0 |   0
0 | 1 |   1
1 | 0 |   1
1 | 1 |   1
```

Boolean: `F = A + B`

### XOR (Exclusive OR)

Outputs 1 when inputs are **different**. This gate is the core of binary addition.

```
A | B | A XOR B
0 | 0 |    0
0 | 1 |    1
1 | 0 |    1
1 | 1 |    0
```

Boolean: `F = A ⊕ B = A'B + AB'`

Verifying with `A=1, B=1`: `0·1 + 1·0 = 0 + 0 = 0`. Correct.

### NAND and NOR — Universal Gates

**NAND** = NOT(AND): `F = (A · B)'`
**NOR** = NOT(OR): `F = (A + B)'`

```
A | B | A NAND B | A NOR B
0 | 0 |    1     |    1
0 | 1 |    1     |    0
1 | 0 |    1     |    0
1 | 1 |    0     |    0
```

These are **universal gates**: any Boolean function can be built from NAND gates alone, or NOR gates alone. This matters for chip fabrication — a single standard cell can implement everything.

**Proof that NAND is universal** (implement NOT and AND from NAND):

```
NOT A   = A NAND A        (tie both inputs together)
A AND B = (A NAND B) NAND (A NAND B)  = NOT(A NAND B)
A OR B  = (A NAND A) NAND (B NAND B)  = A' NAND B'  = NOT(A') + NOT(B') is wrong,
          apply De Morgan: (A')' + (B')' = A + B ✓
```

## Boolean Algebra and Simplification

Gate networks implement Boolean expressions. The key laws:

| Law | AND form | OR form |
|-----|----------|---------|
| Identity | A · 1 = A | A + 0 = A |
| Null | A · 0 = 0 | A + 1 = 1 |
| Idempotent | A · A = A | A + A = A |
| Complement | A · A' = 0 | A + A' = 1 |
| Absorption | A · (A + B) = A | A + (A · B) = A |
| De Morgan | (A · B)' = A' + B' | (A + B)' = A' · B' |

**De Morgan worked example**: simplify `NOT(X AND Y AND Z)` into OR form.

```
(X · Y · Z)' = X' + Y' + Z'
```

This is exactly what a 3-input NAND gate computes. Useful for implementing active-low logic.

### Simplification Example

Expression: `F = A'BC + ABC' + ABC`

```
Step 1: Factor last two terms: ABC' + ABC = AB(C' + C) = AB · 1 = AB
Step 2: F = A'BC + AB
Step 3: Factor B: F = B(A'C + A) = B(A + C)   ← using absorption: A'C + A = A + C
Final: F = B(A + C) = AB + BC
```

Fewer gates needed after simplification.

## Combining Gates: 1-bit Arithmetic

### Half Adder

Adds two 1-bit inputs:

```
Sum   = A XOR B
Carry = A AND B
```

Full truth table:

```
A | B | Sum | Carry
0 | 0 |  0  |  0
0 | 1 |  1  |  0
1 | 0 |  1  |  0
1 | 1 |  0  |  1
```

Gate count: 1 XOR + 1 AND = 2 gates.

### Full Adder

Adds three 1-bit values (A, B, and a carry-in Cin):

```
Sum    = A XOR B XOR Cin
Cout   = (A AND B) OR (B AND Cin) OR (A AND Cin)
```

Full truth table:

```
A | B | Cin | Sum | Cout
0 | 0 |  0  |  0  |  0
0 | 0 |  1  |  1  |  0
0 | 1 |  0  |  1  |  0
0 | 1 |  1  |  0  |  1
1 | 0 |  0  |  1  |  0
1 | 0 |  1  |  0  |  1
1 | 1 |  0  |  0  |  1
1 | 1 |  1  |  1  |  1
```

Verify row `A=1, B=1, Cin=1`: Sum = `1 XOR 1 XOR 1 = 0 XOR 1 = 1`. Cout = `(1·1) OR (1·1) OR (1·1) = 1`. ✓

A full adder can be built from two half adders plus one OR gate.

## The 4-bit Ripple-Carry Adder

Chain four full adders, routing `Cout` of bit position N to `Cin` of bit position N+1:

```
Bit 3             Bit 2             Bit 1             Bit 0
 A3 B3            A2 B2            A1 B1            A0 B0
  │  │             │  │             │  │             │  │
┌─┴──┴─┐   C3  ┌──┴──┴─┐   C2  ┌──┴──┴─┐   C1  ┌──┴──┴─┐
│ Full │◄──────│ Full  │◄──────│ Full  │◄──────│ Full  │◄── Cin=0
│ Add  │       │ Add   │       │ Add   │       │ Add   │
└──┬───┘       └──┬────┘       └──┬────┘       └──┬────┘
   S3              S2              S1              S0
```

**Worked example: add 0110 (6) + 0111 (7) = ?**

```
Bit 0: A=0, B=1, Cin=0 → Sum=1, Cout=0
Bit 1: A=1, B=1, Cin=0 → Sum=0, Cout=1
Bit 2: A=1, B=1, Cin=1 → Sum=1, Cout=1
Bit 3: A=0, B=0, Cin=1 → Sum=1, Cout=0

Result: 1101 = 13 ✓
```

The carry must **ripple** from bit 0 to bit 3, so the critical path is 4 full adder delays. A 64-bit ripple-carry adder has 64× that delay — too slow for a modern CPU. Real CPUs use **carry-lookahead** or **carry-select** adders that compute all carries in O(log N) gate levels.

## Multiplexers (MUX)

A 2-to-1 MUX chooses between two inputs based on a selector:

```
Inputs: A, B
Selector: S
Output: F = S'·A + S·B

S=0 → F = A
S=1 → F = B
```

Truth table:

```
S | A | B | F
0 | 0 | 0 | 0
0 | 0 | 1 | 0   ← F = A = 0
0 | 1 | 0 | 1
0 | 1 | 1 | 1   ← F = A = 1
1 | 0 | 0 | 0
1 | 0 | 1 | 1   ← F = B = 1
1 | 1 | 0 | 0
1 | 1 | 1 | 1   ← F = B = 1
```

CPUs use MUXes everywhere: to choose between the register file output and an immediate value (ALUSrc), to route memory data or ALU result to the register write port (MemToReg), and to select the next PC value.

## Why All This Matters

When you write `a + b` in C, the compiler emits an `ADD` instruction. That instruction triggers the CPU's 64-bit carry-lookahead adder — thousands of gates switching in under 200 picoseconds. Every if-statement compiles to a comparison (XOR + subtraction + flags) followed by a branch. Every array index computes an address with a shift-and-add unit. All of it ultimately reduces to NAND and NOR gates on silicon.
