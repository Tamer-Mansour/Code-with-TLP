# What Is the ALU and What Does It Do?

The Arithmetic Logic Unit (ALU) is the computational heart of every processor. It is the hardware block responsible for performing arithmetic operations (addition, subtraction, multiplication, division) and logical operations (AND, OR, XOR, NOT, shifts). Every time a program adds two numbers or compares a value against zero, the ALU is doing the work.

## Where the ALU Lives

The ALU sits inside the CPU's datapath. In a classic five-stage pipeline (Fetch → Decode → Execute → Memory → Write-back), the ALU operates during the **Execute** stage. It receives two source operands — typically read from registers — and a control signal that tells it which operation to perform. It then outputs a result and a set of status flags.

```
        ┌─────────┐
 A ────>│         │
        │   ALU   │──── Result
 B ────>│         │──── Flags (Zero, Carry, Overflow, Sign)
        └─────────┘
             ↑
         ALU Control
```

## Inputs and Outputs

| Signal | Direction | Description |
|--------|-----------|-------------|
| Operand A | Input | First source value (e.g., register rs1) |
| Operand B | Input | Second source value (register rs2 or immediate) |
| ALU Control | Input | Selects the operation (ADD, SUB, AND, …) |
| Result | Output | Computed value written back to destination register |
| Flags | Output | Zero, Carry, Overflow, Sign — used by branch logic |

## Operations an ALU Performs

A real ALU handles a family of operations, not just addition:

- **Arithmetic** — ADD, SUB, increment, decrement, negate
- **Logical** — AND, OR, XOR, NOT (bitwise, operate on every bit independently)
- **Comparison** — set-less-than (SLT), equality check (implemented as SUB + check Zero flag)
- **Shifts** — logical shift left/right, arithmetic shift right
- **Pass-through** — some designs allow the ALU to pass one operand unchanged for address calculations

In RISC-V, the ALU control lines are derived from the instruction's `funct3` and `funct7` fields. For example, an `ADD` and a `SUB` share the same `funct3` value (`000`) but differ in `funct7` bit 5, so the control unit uses that bit to flip the ALU between add and subtract mode.

## A Minimal 1-Bit ALU

Before building a 32-bit ALU, engineers design a 1-bit slice. Each 1-bit ALU takes two input bits, a carry-in, and a control signal, and produces one output bit plus a carry-out. Thirty-two of these slices chained together form a 32-bit ripple-carry ALU.

```
1-bit ALU slice:
  a, b  → Full Adder  → sum bit, carry-out
  a, b  → AND gate    → and bit
  a, b  → OR gate     → or bit
  Mux selects which result to pass to the output based on ALU control
```

## Why the ALU Matters for Interviews

Understanding the ALU answers several common interview questions:

- How does a CPU add two numbers? (Ripple-carry or carry-lookahead adder inside the ALU)
- How does a CPU compare two numbers for a branch? (Subtract and check the Zero flag)
- What is the difference between logical and arithmetic right shift? (ALU shift logic)

> **Interview answer:** The ALU is the combinational logic block inside the CPU that performs all arithmetic and bitwise operations on data operands; every compute instruction in the ISA maps to a specific ALU operation selected by the control unit.

## Common Pitfalls

- The ALU itself is **stateless** — it is pure combinational logic with no memory. All state lives in registers, not the ALU.
- The flags (Zero, Carry, Overflow, Sign) are produced as side-outputs, not part of the result register in RISC-V. This differs from x86, where flags are stored in a dedicated FLAGS register.
- Overflow and carry are different: carry applies to unsigned arithmetic; overflow applies to signed arithmetic.
