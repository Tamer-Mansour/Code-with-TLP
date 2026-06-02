# I-Type Format: Immediates and Loads

I-type instructions replace the second source register (rs2) and funct7 fields with a 12-bit signed immediate. This single change unlocks a large class of operations: arithmetic with constants, memory loads, JALR, and system calls.

## Bit Layout

```
 31             20 19    15 14   12 11      7 6       0
+----------------+--------+-------+---------+---------+
|   imm[11:0]    |  rs1   | funct3|   rd    | opcode  |
|    12 bits     | 5 bits | 3 bits|  5 bits |  7 bits |
+----------------+--------+-------+---------+---------+
```

| Field     | Bits    | Width | Purpose |
|-----------|---------|-------|---------|
| opcode    | [6:0]   | 7     | Instruction group |
| rd        | [11:7]  | 5     | Destination register |
| funct3    | [14:12] | 3     | Selects specific operation |
| rs1       | [19:15] | 5     | Base register |
| imm[11:0] | [31:20] | 12    | Signed immediate, sign bit at bit 31 |

The immediate is **sign-extended** from bit 31 to produce a full 32-bit (or 64-bit) value before use. This gives a range of -2048 to +2047.

## I-Type Opcode Groups

| opcode (binary) | opcode (hex) | Group |
|-----------------|-------------|-------|
| 0010011 | 0x13 | Integer immediate arithmetic |
| 0000011 | 0x03 | Loads |
| 1100111 | 0x67 | JALR |
| 1110011 | 0x73 | System (ECALL, EBREAK, CSR) |

## Common I-Type Instructions

```asm
addi  x3, x1, 42    # x3 = x1 + 42
slti  x3, x1, -1    # x3 = (x1 < -1) ? 1 : 0 (signed)
sltiu x3, x1, 1     # x3 = (x1 < 1)  ? 1 : 0 (unsigned)
andi  x3, x1, 0xFF  # x3 = x1 & 0xFF
ori   x3, x1, 0x0F  # x3 = x1 | 0x0F
xori  x3, x1, -1    # x3 = ~x1  (XOR with all-ones)
lw    x3, 8(x1)     # x3 = Memory[x1 + 8]  (32-bit load)
lh    x3, 4(x1)     # x3 = sign-extend(Memory[x1+4][15:0])
lb    x3, 0(x1)     # x3 = sign-extend(Memory[x1][7:0])
lhu   x3, 4(x1)     # x3 = zero-extend(Memory[x1+4][15:0])
jalr  x1, x0, 0     # ret: PC = x0 + 0; link address in x1
```

## Shift Immediates: A Special Sub-Case

`slli`, `srli`, and `srai` are encoded as I-type but only bits [4:0] of the immediate are the shift amount. Bits [11:5] are redefined as a `funct6/funct7` discriminator (0000000 for slli/srli, 0100000 for srai). This is compatible with the I-type layout but restricts the shift amount to 0–31 for RV32I.

```asm
slli  x3, x1, 3    # x3 = x1 << 3  (imm[11:5] = 0000000)
srai  x3, x1, 3    # x3 = x1 >>> 3 (imm[11:5] = 0100000)
```

## Worked Example: Encoding `lw x5, 12(x2)`

1. **opcode** = 0000011 (load)
2. **rd** = x5 = 00101
3. **funct3** = 010 (word load)
4. **rs1** = x2 = 00010
5. **imm[11:0]** = 12 = 0000 0000 1100

```
000000001100  00010  010  00101  0000011
 imm[11:0]    rs1   f3    rd    opcode
```

Hex: `0x00C12283`

## Common Pitfalls

- **Forgetting sign extension**: `addi x1, x0, -1` produces `0xFFFFFFFF`, not `0x00000FFF`.
- **Load funct3 confusion**: `010` = word, `001` = halfword, `000` = byte; `101` = lhu, `100` = lbu. Getting these wrong is a classic exam trap.
- **JALR target**: JALR sets the LSB of the computed target to 0 (by design), preventing misaligned jumps even if the address computed is odd.

## Interview Answer

> "I-type uses a 12-bit signed immediate in bits [31:20], with rs1 in [19:15], funct3 in [14:12], rd in [11:7], and opcode in [6:0]. The immediate is always sign-extended from bit 31. This format covers immediate arithmetic, all load instructions, JALR, and system calls."
