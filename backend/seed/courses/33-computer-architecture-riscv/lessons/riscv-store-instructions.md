# RISC-V Store Instructions: SB, SH, SW, SD

Store instructions write register values back to memory. Unlike loads, stores have **no destination register** — their only effect is a memory write. This shapes their encoding and makes them distinct from all other RISC-V instruction types.

## The Store Instruction Family

| Mnemonic | Full Name | Width Written |
|---|---|---|
| `SB` | Store Byte | 8 bits (lowest byte of rs2) |
| `SH` | Store Halfword | 16 bits (lowest 2 bytes of rs2) |
| `SW` | Store Word | 32 bits (lowest 4 bytes of rs2) |
| `SD` | Store Doubleword | 64 bits (all 8 bytes of rs2, RV64 only) |

All store instructions write the **least-significant** N bits of the source register to memory. The upper bits are silently discarded.

## S-Type Encoding (Unique to Stores)

Stores cannot use I-type encoding because they have two source registers (`rs1` for base address, `rs2` for data) and no destination register. RISC-V uses the **S-type** format:

```
[31:25]  imm[11:5]   upper 7 bits of 12-bit offset
[24:20]  rs2          source register (data to store)
[19:15]  rs1          base address register
[14:12]  funct3       width selector
[11:7]   imm[4:0]    lower 5 bits of 12-bit offset
[6:0]    opcode       0100011 (STORE)
```

The 12-bit immediate is split across two fields. This unusual layout keeps `rs1` and `rs2` at the **same bit positions** as in R-type and I-type instructions, which simplifies the hardware decoder — register file read ports can always be wired to fixed bit positions.

Effective address: `address = rs1 + sign_extend({imm[11:5], imm[4:0]})`

## SB — Store Byte

```asm
sb  x2, 0(x1)     # mem[x1+0] = x2[7:0]   (1 byte written)
```

If `x2 = 0xABCDEF12`, only the byte `0x12` is written to memory.

## SH — Store Halfword

```asm
sh  x2, 2(x1)     # mem[x1+2..x1+3] = x2[15:0]  (2 bytes written)
```

If `x2 = 0xABCDEF12`, only `0xEF12` is written. Byte order depends on the system's endianness (RISC-V is typically little-endian, so `0x12` goes to the lower address).

## SW — Store Word

```asm
sw  x2, 4(x1)     # mem[x1+4..x1+7] = x2[31:0]  (4 bytes written)
```

On RV64, `x2` holds 64 bits; only the lower 32 bits are stored.

## SD — Store Doubleword (RV64 Only)

```asm
sd  x2, 8(x1)     # mem[x1+8..x1+15] = x2[63:0]  (8 bytes written)
```

Used for 64-bit integers and pointers.

## Worked Example: Writing a Struct to Memory

```c
struct Packet {
    uint8_t  flags;   // offset 0
    uint16_t length;  // offset 2
    uint32_t id;      // offset 4
};
```

Assuming the struct base address is in `x10`:

```asm
li   x11, 0x03
sb   x11, 0(x10)    # flags = 0x03

li   x12, 256
sh   x12, 2(x10)    # length = 256

li   x13, 0xDEADBEEF
sw   x13, 4(x10)    # id = 0xDEADBEEF
```

## Key Differences from Loads

| Property | Load | Store |
|---|---|---|
| Instruction type | I-type | S-type |
| Destination register | Yes (rd) | None |
| Source registers | rs1 (base) | rs1 (base), rs2 (data) |
| Immediate split | No | Yes (bits 11:5 and 4:0) |
| Sign extension | Yes (signed variants) | Never — writes raw bits |

## Common Pitfall

Stores do not produce a result that you can inspect in a register. If you store a value and immediately want to verify it, you must perform a separate load. In debugging scenarios, using `LD`/`LW` after `SD`/`SW` to check the write is a valid pattern.

Another common error: storing from the wrong register. `SW x2, 0(x3)` stores `x2`'s lower 32 bits at the address held in `x3` — not `x3`'s value.

> **Interview answer:** Store instructions in RISC-V use S-type encoding, which splits the 12-bit offset across two fields to keep register indices at fixed bit positions. They write the low-order N bits of a source register to a base-plus-offset memory address.
