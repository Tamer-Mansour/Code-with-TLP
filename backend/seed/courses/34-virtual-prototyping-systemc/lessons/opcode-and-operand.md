# Opcodes and Operands

Every machine instruction consists of two conceptual parts: the **opcode** that names the operation, and the **operands** that supply the data. Understanding how these fields are laid out in a binary instruction word is essential for writing a correct decode stage in your SystemC CPU model.

## The Opcode

The opcode (operation code) is the bit field that tells the processor which operation to perform — add, subtract, load, store, branch, etc. In a fixed-width ISA the opcode occupies a predictable bit range, making hardware decode fast and regular.

| ISA | Opcode width | Location |
|---|---|---|
| RISC-V RV32I | 7 bits | Bits [6:0] |
| ARM A32 | 4 bits (cond) + 4 bits (op) | Bits [31:28], [27:24] |
| x86 (variable) | 1-3 bytes | Leading byte(s) |

Because RISC designs use a fixed opcode position, a decode multiplexer can read the opcode field in a single clock cycle without inspecting the rest of the word first.

## Operands

Operands specify the inputs and output of the operation. They come in three flavors:

- **Register operands** — a small integer index (e.g., 5 bits for 32 registers) identifying a CPU register.
- **Immediate operands** — a constant value embedded directly in the instruction word.
- **Memory operands** — an effective address, usually formed as `base register + displacement`.

### RISC-V R-Type Instruction Layout

```
 31      25 24   20 19   15 14  12 11    7 6      0
 [ funct7 ] [ rs2 ] [ rs1 ] [fn3] [  rd  ] [opcode]
    7 bits    5 bits  5 bits  3 bits  5 bits   7 bits
```

For `add x1, x2, x3` (rd=x1, rs1=x2, rs2=x3):

```asm
add x1, x2, x3
```

Encoded as hex `0x003100B3`:

```
funct7=0000000  rs2=00011  rs1=00010  funct3=000  rd=00001  opcode=0110011
```

### RISC-V I-Type (Immediate) Layout

```
 31          20 19   15 14  12 11    7 6      0
 [   imm[11:0]  ] [ rs1 ] [fn3] [  rd  ] [opcode]
     12 bits        5 bits  3 bits  5 bits   7 bits
```

The 12-bit immediate is **sign-extended** to 32 bits before use — a frequent source of bugs.

```cpp
// Correct sign extension of a 12-bit immediate
int32_t sign_extend_12(uint32_t raw) {
    // Shift left to bring sign bit to bit 31, then arithmetic shift right
    return (int32_t)(raw << 20) >> 20;
}
```

## Funct Fields — Extending the Opcode

RISC-V and many other ISAs include secondary function fields (`funct3`, `funct7`) that subdivide a single opcode into a family of related operations. For example, opcode `0110011` (OP) combined with:

| funct7 | funct3 | Instruction |
|---|---|---|
| 0000000 | 000 | ADD |
| 0100000 | 000 | SUB |
| 0000000 | 111 | AND |
| 0000000 | 110 | OR  |

This lets one 7-bit opcode cover an entire class of arithmetic/logic operations.

## Common Pitfalls

- **Forgetting sign extension** on immediates — always cast to a signed type before arithmetic.
- **Conflating opcode with instruction format** — two instructions can share an opcode but differ in format (R vs I vs S).
- **Off-by-one in bit masks** — always double-check the ISA manual for inclusive/exclusive bit numbering conventions.

## Interview Answer

> "An opcode is the bit field that identifies the operation; operands are the register indices or immediate constants that supply the data. In a fixed-width ISA the opcode occupies a known bit range, enabling single-cycle decode. Secondary funct fields extend the opcode to distinguish instructions within a family."
