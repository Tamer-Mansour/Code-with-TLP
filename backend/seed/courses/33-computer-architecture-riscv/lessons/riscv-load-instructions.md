# RISC-V Load Instructions: LB, LH, LW, LD

RISC-V provides a family of load instructions that differ in the **width** of data they read from memory and how they extend the result to fill the destination register. Understanding the full family is essential for working with different data types at the hardware level.

## The Load Instruction Family

| Mnemonic | Full Name | Width | Sign-extends? |
|---|---|---|---|
| `LB` | Load Byte | 8 bits | Yes |
| `LH` | Load Halfword | 16 bits | Yes |
| `LW` | Load Word | 32 bits | Yes (RV64 only) |
| `LD` | Load Doubleword | 64 bits | N/A (fills reg) |
| `LBU` | Load Byte Unsigned | 8 bits | No (zero-extends) |
| `LHU` | Load Halfword Unsigned | 16 bits | No (zero-extends) |
| `LWU` | Load Word Unsigned | 32 bits | No (zero-extends, RV64 only) |

The unsigned variants (`LBU`, `LHU`, `LWU`) are covered in the next lesson. Here we focus on the signed loads.

## Instruction Encoding

All load instructions share the **I-type** encoding format:

```
[31:20]  imm[11:0]   12-bit immediate (offset)
[19:15]  rs1          base register
[14:12]  funct3       width selector
[11:7]   rd           destination register
[6:0]    opcode       0000011 (LOAD)
```

The effective address is computed as: `address = rs1 + sign_extend(imm[11:0])`

## LB — Load Byte

Reads 1 byte from memory and **sign-extends** it to fill the register width (32 or 64 bits).

```asm
lb  x2, 0(x1)     # x2 = sign_extend(mem[x1], 8 -> XLEN)
```

If the byte at `mem[x1]` is `0xFF` (decimal 255 or -1 signed), then in `x2` (64-bit):
- `LB` produces `0xFFFFFFFFFFFFFFFF` (-1 as a 64-bit signed integer)
- `LBU` produces `0x00000000000000FF` (255 unsigned)

## LH — Load Halfword

Reads 2 consecutive bytes (a 16-bit halfword) and sign-extends to XLEN.

```asm
lh  x3, 4(x1)     # x3 = sign_extend(mem[x1+4..x1+5], 16 -> XLEN)
```

The address must be 2-byte aligned on systems that enforce alignment (some implementations may trap on misaligned access).

## LW — Load Word

Reads 4 consecutive bytes (a 32-bit word). On RV32, this fills the entire register. On RV64, it sign-extends from 32 to 64 bits.

```asm
lw  x4, 8(x1)     # x4 = sign_extend(mem[x1+8..x1+11], 32 -> XLEN)
```

This is the most common load in C programs — it handles `int` (typically 32-bit).

## LD — Load Doubleword (RV64 Only)

Reads 8 consecutive bytes and fills the full 64-bit register. There is no sign extension because the loaded value already fills the register completely.

```asm
ld  x5, 16(x1)    # x5 = mem[x1+16..x1+23]  (all 64 bits)
```

Used for `long`, `int64_t`, and pointer types in 64-bit programs.

## Worked Example: Reading a Struct

Suppose a C struct is laid out in memory at address held in `x10`:

```c
struct Point {
    int8_t  tag;    // offset 0
    int16_t y;      // offset 2 (due to alignment padding)
    int32_t x;      // offset 4
};
```

```asm
lb   x11, 0(x10)    # load tag  (signed byte)
lh   x12, 2(x10)    # load y    (signed halfword)
lw   x13, 4(x10)    # load x    (signed word)
```

## Common Pitfall

Using `LW` to load an address on a 64-bit RISC-V system will sign-extend the upper 32 bits. If the pointer happens to have bit 31 set (e.g., `0x80000000`), the result will be a large negative number, causing crashes. Always use `LD` for pointers on RV64.

> **Interview answer:** RISC-V load instructions differ by data width (byte/halfword/word/doubleword) and sign behavior. Signed loads (`LB`, `LH`, `LW`) sign-extend the result; the I-type encoding provides a 12-bit signed offset from a base register.
