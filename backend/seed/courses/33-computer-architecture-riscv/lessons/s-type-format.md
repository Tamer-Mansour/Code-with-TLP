# S-Type Format: Stores

Store instructions need three register values: a base address (rs1), data to store (rs2), and a byte offset (the immediate). But there is no destination register — the result lands in memory, not in a register. S-type is the first format that repurposes the rd field for something else: the lower five bits of the immediate.

## Bit Layout

```
 31      25 24    20 19    15 14   12 11      7 6       0
+---------+--------+--------+-------+---------+---------+
|imm[11:5]|  rs2   |  rs1   | funct3| imm[4:0]| opcode  |
|  7 bits | 5 bits | 5 bits | 3 bits|  5 bits |  7 bits |
+---------+--------+--------+-------+---------+---------+
```

| Field     | Bits    | Width | Purpose |
|-----------|---------|-------|---------|
| opcode    | [6:0]   | 7     | 0100011 for all stores |
| imm[4:0]  | [11:7]  | 5     | Low 5 bits of the byte offset |
| funct3    | [14:12] | 3     | Transfer width (byte, half, word) |
| rs1       | [19:15] | 5     | Base address register |
| rs2       | [24:20] | 5     | Source data register |
| imm[11:5] | [31:25] | 7     | High 7 bits of the byte offset |

The full 12-bit immediate is reconstructed as: `{ imm[11:5], imm[4:0] }` = bits [31:25] concatenated with bits [11:7]. After reconstruction the immediate is sign-extended to 32/64 bits.

## Immediate Reconstruction in Hardware

```c
// Pseudocode — how a decoder reassembles the S-type immediate
int32_t imm = ((inst >> 25) << 5)    // imm[11:5] -> bits [11:5]
            | ((inst >> 7) & 0x1F);  // imm[4:0]  -> bits [4:0]
// sign extend from bit 11
imm = (imm << 20) >> 20;
```

The split exists so that rs1 and rs2 occupy the same bit positions as in R-type. Hardware can read the two register addresses immediately, before fully decoding the immediate.

## Store Instructions

| Mnemonic | funct3 | Transfer |
|----------|--------|----------|
| `sb`     | 000    | 8-bit byte |
| `sh`     | 001    | 16-bit halfword |
| `sw`     | 010    | 32-bit word |
| `sd`     | 011    | 64-bit doubleword (RV64 only) |

```asm
sw  x5, 8(x2)    # Memory[x2 + 8] = x5[31:0]
sh  x5, 4(x2)    # Memory[x2 + 4] = x5[15:0]
sb  x5, 0(x2)    # Memory[x2 + 0] = x5[7:0]
```

## Worked Example: Encoding `sw x5, 20(x2)`

- **opcode** = 0100011
- **imm** = 20 = 0b0000_0001_0100; split: imm[11:5] = 0000000, imm[4:0] = 10100
- **funct3** = 010 (word)
- **rs1** = x2 = 00010
- **rs2** = x5 = 00101

```
0000000  00101  00010  010  10100  0100011
imm[11:5] rs2   rs1   f3  imm[4:0] opcode
```

Hex: `0x00512A23`

## Why Not Keep rd and Use a 12-bit Contiguous Immediate?

Having a destination register field means hardware register-file ports can be wired identically across R-type and I-type. For stores, RISC-V designers chose to split the immediate across bits [31:25] and [11:7] rather than shift bits around, keeping rs1 and rs2 in the same positions as always. The cost is one extra mux in the immediate reconstruction path — a cheap trade-off.

## Common Pitfalls

- **Confusing load and store immediates**: Loads (I-type) have a contiguous 12-bit immediate. Stores (S-type) split it. Candidates who memorize only one get encoding questions wrong.
- **Storing more bytes than the register has**: `sw` always writes exactly 32 bits. On RV32I, `sd` does not exist — use two `sw` instructions.
- **Offset must be signed**: `sw x5, -4(x2)` is valid (stack push pattern); the negative immediate is correctly reconstructed by sign extension.

## Interview Answer

> "S-type splits the 12-bit signed offset across bits [31:25] and [11:7], keeping rs1 and rs2 in their standard positions. The decoder ORs the two pieces back together and sign-extends from bit 11 to get the effective address offset."
