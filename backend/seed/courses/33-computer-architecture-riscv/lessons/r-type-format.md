# R-Type Format: Register-Register Operations

R-type is the simplest of the six RISC-V formats because it carries no immediate. Every bit is consumed by control fields and register specifiers. Understanding R-type first gives you the baseline from which every other format deviates.

## Bit Layout

```
 31      25 24    20 19    15 14   12 11      7 6       0
+---------+--------+--------+-------+---------+---------+
|  funct7 |  rs2   |  rs1   | funct3|   rd    | opcode  |
|  7 bits | 5 bits | 5 bits | 3 bits|  5 bits |  7 bits |
+---------+--------+--------+-------+---------+---------+
```

| Field  | Bits   | Width | Purpose |
|--------|--------|-------|---------|
| opcode | [6:0]  | 7     | Identifies the instruction group (0110011 for integer R-type) |
| rd     | [11:7] | 5     | Destination register |
| funct3 | [14:12]| 3     | Selects the specific operation within the group |
| rs1    | [19:15]| 5     | First source register |
| rs2    | [24:20]| 5     | Second source register |
| funct7 | [31:25]| 7     | Further qualifies the operation (e.g., ADD vs SUB) |

Five-bit register specifiers address 32 architectural registers (x0–x31), which is exactly the number RISC-V defines.

## The funct3 + funct7 Split

A 7-bit opcode alone distinguishes instruction *groups*, not individual instructions. `funct3` adds 3 more bits (8 possibilities), and `funct7` adds 7 more (128 possibilities). In practice, RISC-V uses only a few `funct7` codes:

| funct7    | Meaning |
|-----------|---------|
| 0000000   | Default (ADD, SRL, SLT, …) |
| 0100000   | Alternate (SUB, SRA) |
| 0000001   | M-extension multiply/divide |

The bit that flips between ADD and SUB is bit 30 (the second MSB of funct7). Hardware checks only that bit — it does not decode all seven.

## Common R-Type Instructions

```asm
add  x3, x1, x2    # x3 = x1 + x2   (funct7=0000000, funct3=000)
sub  x3, x1, x2    # x3 = x1 - x2   (funct7=0100000, funct3=000)
and  x3, x1, x2    # x3 = x1 & x2   (funct7=0000000, funct3=111)
or   x3, x1, x2    # x3 = x1 | x2   (funct7=0000000, funct3=110)
xor  x3, x1, x2    # x3 = x1 ^ x2   (funct7=0000000, funct3=100)
sll  x3, x1, x2    # x3 = x1 << x2  (shift left logical)
srl  x3, x1, x2    # x3 = x1 >> x2  (shift right logical)
sra  x3, x1, x2    # x3 = x1 >>> x2 (shift right arithmetic)
slt  x3, x1, x2    # x3 = (x1 < x2) ? 1 : 0 (signed)
sltu x3, x1, x2    # x3 = (x1 < x2) ? 1 : 0 (unsigned)
```

## Worked Example: Encoding `add x5, x1, x2`

1. **opcode** = 0110011 (integer register-register)
2. **rd** = x5 = 00101
3. **funct3** = 000 (ADD)
4. **rs1** = x1 = 00001
5. **rs2** = x2 = 00010
6. **funct7** = 0000000

Concatenating in instruction order [31:0]:

```
0000000  00010  00001  000  00101  0110011
funct7   rs2    rs1   f3    rd    opcode
```

Binary: `0000 0000 0010 0000 1000 0010 1011 0011`
Hex: `0x00208233`

You can verify this in a RISC-V assembler or objdump output.

## Common Pitfall

Candidates often confuse `srl` and `sra`. Both have `funct3 = 101`, distinguished only by `funct7` bit 30 (0 = logical, 1 = arithmetic). On hardware this is a single mux select line — not a completely different ALU path.

## Interview Answer

> "R-type is a 32-bit format with fields funct7 (7b), rs2 (5b), rs1 (5b), funct3 (3b), rd (5b), and opcode (7b). It encodes register-register operations; the opcode selects the instruction class, while funct3 and funct7 together pick the exact operation — for example bit 30 of funct7 distinguishes ADD from SUB."
