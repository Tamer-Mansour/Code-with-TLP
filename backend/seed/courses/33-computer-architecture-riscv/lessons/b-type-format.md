# B-Type Format: Conditional Branches

B-type encodes conditional branches: `beq`, `bne`, `blt`, `bge`, `bltu`, `bgeu`. Like S-type it has two source registers and no destination register, and it splits an immediate across two non-contiguous fields. The twist: the immediate encodes a **13-bit** PC-relative offset but only carries **12 bits** in the instruction — the missing bit 0 is always implied to be zero because all instructions are at least 2-byte aligned.

## Bit Layout

```
 31      25 24    20 19    15 14   12 11      7 6       0
+---------+--------+--------+-------+---------+---------+
|imm[12|   |  rs2   |  rs1   | funct3|imm[4:1| | opcode  |
|   10:5] |        |        |       |    11]  |         |
|  7 bits | 5 bits | 5 bits | 3 bits|  5 bits |  7 bits |
+---------+--------+--------+-------+---------+---------+
```

More precisely:

| Bits of instruction | Immediate bit |
|---------------------|---------------|
| [31]                | imm[12] (sign bit) |
| [30:25]             | imm[10:5] |
| [11:8]              | imm[4:1] |
| [7]                 | imm[11] |

The full target offset is: `{ imm[12], imm[11], imm[10:5], imm[4:1], 0 }` — 13 bits with an implicit zero at position 0.

## Immediate Reconstruction

```c
// Pseudocode: B-type immediate assembly from a 32-bit instruction word
int32_t imm =
    ((inst >> 31) & 1) << 12  |   // bit 31 -> imm[12]
    ((inst >>  7) & 1) << 11  |   // bit 7  -> imm[11]
    ((inst >> 25) & 0x3F) << 5|   // bits 30:25 -> imm[10:5]
    ((inst >>  8) & 0xF) << 1;    // bits 11:8 -> imm[4:1]
// sign-extend from bit 12
imm = (imm << 19) >> 19;
```

The effective branch target is `PC + imm`. Range: -4096 to +4094 bytes (±4 KB, in steps of 2).

## Why is bit 11 in the rd field?

The rd field (bits [11:7]) is split: bits [11:8] hold `imm[4:1]` and bit [7] holds `imm[11]`. This bizarre swap puts bit 11 next to bit 12 in the *output* of the immediate reconstruction with minimal routing: bit 31 → imm[12] and bit 7 → imm[11] are adjacent in the reconstructed result. The hardware saves one wire layer at the cost of confusing humans.

## Branch Instructions

| Mnemonic | funct3 | Condition |
|----------|--------|-----------|
| `beq`    | 000    | rs1 == rs2 |
| `bne`    | 001    | rs1 != rs2 |
| `blt`    | 100    | rs1 < rs2 (signed) |
| `bge`    | 101    | rs1 >= rs2 (signed) |
| `bltu`   | 110    | rs1 < rs2 (unsigned) |
| `bgeu`   | 111    | rs1 >= rs2 (unsigned) |

All six share opcode `1100011`.

## Worked Example: Encoding `beq x1, x2, +20`

- Offset = 20 = 0b0_0000_0001_0100; split: imm[12]=0, imm[11]=0, imm[10:5]=000000, imm[4:1]=1010
- **opcode** = 1100011
- **funct3** = 000 (BEQ)
- **rs1** = x1 = 00001, **rs2** = x2 = 00010

Place into instruction bits:

```
bit 31  = imm[12]   = 0
bits 30:25 = imm[10:5] = 000000
bits 24:20 = rs2       = 00010
bits 19:15 = rs1       = 00001
bits 14:12 = funct3    = 000
bits 11:8  = imm[4:1]  = 1010
bit  7     = imm[11]   = 0
bits 6:0   = opcode    = 1100011
```

Binary: `0000000 00010 00001 000 10100 1100011`
Hex: `0x00208A63`

## Common Pitfalls

- **Off-by-one in offset**: the immediate is PC-relative and in bytes, not instruction counts. `beq x0, x0, 1` is not valid — the offset must be even.
- **Confusing imm[11] placement**: bit 7 of the instruction encodes imm[11], not imm[0]. Getting this wrong causes a wildly wrong branch target.
- **Signed vs unsigned comparisons**: `blt` and `bltu` differ only in signedness. Comparing pointer-like values (addresses) usually calls for `bltu`/`bgeu`.

## Interview Answer

> "B-type encodes a 13-bit PC-relative offset with the LSB implicitly zero. The 12 explicit bits are scattered across bits [31], [30:25], [11:8], and [7] of the instruction word, arranged so that sign extension hardware always reads the sign bit from bit 31 and adjacent bits stay adjacent after reconstruction."
