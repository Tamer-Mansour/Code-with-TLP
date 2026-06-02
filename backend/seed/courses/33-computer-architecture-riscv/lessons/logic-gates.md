# Logic Gates: AND, OR, NOT, XOR, NAND, NOR

Every digital circuit — from a simple calculator to a multi-core CPU — is built from a small set of primitive building blocks called **logic gates**. Each gate takes one or more binary inputs (0 or 1) and produces a single binary output according to a fixed truth table.

## The Core Gates

| Gate | Symbol | Output rule | ANSI notation |
|------|--------|-------------|---------------|
| AND  | `A & B`  | 1 only when **all** inputs are 1 | `A · B` |
| OR   | `A \| B` | 1 when **at least one** input is 1 | `A + B` |
| NOT  | `¬A`   | Inverts the input | `Ā` |
| XOR  | `A ⊕ B` | 1 when inputs **differ** | `A ⊕ B` |
| NAND | `¬(A & B)` | Inverse of AND | `A · B` with overbar |
| NOR  | `¬(A \| B)` | Inverse of OR | `A + B` with overbar |

### AND Gate

```
A=0, B=0 → 0
A=0, B=1 → 0
A=1, B=0 → 0
A=1, B=1 → 1
```

Use case: "Both conditions must be true." Hardware example: a chip-select line that only activates when both address bits are correct.

### OR Gate

```
A=0, B=0 → 0
A=0, B=1 → 1
A=1, B=0 → 1
A=1, B=1 → 1
```

Use case: "Any one condition is sufficient." Hardware example: an interrupt line that fires when any device requests service.

### NOT Gate (Inverter)

```
A=0 → 1
A=1 → 0
```

The simplest gate. Every complemented variable (`Ā`) uses a NOT.

### XOR Gate

```
A=0, B=0 → 0
A=0, B=1 → 1
A=1, B=0 → 1
A=1, B=1 → 0
```

Critical in arithmetic: the **sum bit** of a 1-bit adder is an XOR. Also used in parity checks and cryptographic operations (e.g., AES MixColumns).

### NAND and NOR — Functionally Complete Gates

**NAND and NOR are each individually functionally complete**: you can build ANY Boolean function from only NAND gates (or only NOR gates). This is why real CMOS technology favors these gates — they map directly to series/parallel transistor networks and consume less power than AND/OR.

```
NAND truth table:
A=1, B=1 → 0   (all other inputs → 1)

NOR truth table:
A=0, B=0 → 1   (all other inputs → 0)
```

## Building More from Less

A NOT gate from NAND:
```
NOT(A) = NAND(A, A)
```

An AND gate from NAND:
```
AND(A,B) = NAND(NAND(A,B), NAND(A,B))
```

## Worked Example: 1-Bit Half Adder

A half adder adds two 1-bit numbers and produces a **sum** and a **carry**:

```
Sum   = A XOR B
Carry = A AND B
```

```
A=0, B=0 → Sum=0, Carry=0
A=0, B=1 → Sum=1, Carry=0
A=1, B=0 → Sum=1, Carry=0
A=1, B=1 → Sum=0, Carry=1   ← 1+1 = 10 in binary
```

Two half adders plus an OR gate form a **full adder**, the nucleus of every ALU.

## Common Pitfalls

- **Confusing XOR with OR**: XOR outputs 0 when both inputs are 1; OR does not. A classic interview trap.
- **Assuming gates are free**: in real silicon each gate adds propagation delay; deep gate chains become the critical path that limits clock frequency.
- **Forgetting NAND/NOR universality**: knowing you can build everything from NAND is a standard exam and interview question.

## Interview Answer

> "Logic gates are the hardware primitives of digital design. AND, OR, and NOT form the complete algebraic basis. NAND and NOR are individually universal — any Boolean function can be implemented with only one gate type — which maps efficiently to CMOS transistor pairs."
