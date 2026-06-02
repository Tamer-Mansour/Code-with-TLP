# Encoding of Load and Store Instructions

Load and store instructions are the bridge between the register file and memory. RISC-V encodes them with a base register plus a signed immediate offset, using I-type for loads and S-type for stores. Knowing the encoding precisely matters for both decoding and for computing the effective address in your ISS.

## Load Instructions (I-Type)

All load instructions share opcode `0000011` and use the I-type format:

```
Bits [31:20] → imm[11:0]   (12-bit signed offset)
Bits [19:15] → rs1          (base address register)
Bits [14:12] → funct3       (data width and sign)
Bits [11:7]  → rd           (destination register)
Bits [6:0]   → 0000011
```

Effective address = `regs[rs1] + sign_extend(imm)`

### Load Variants

| funct3 | Instruction | Width  | Sign behaviour |
|--------|-------------|--------|---------------|
| 000    | LB          | 1 byte | Sign-extended to 32 bits |
| 001    | LH          | 2 byte | Sign-extended to 32 bits |
| 010    | LW          | 4 byte | Full word (RV32) |
| 100    | LBU         | 1 byte | Zero-extended |
| 101    | LHU         | 2 byte | Zero-extended |

`LB` reads one byte from memory and fills the upper 24 bits of `rd` with the byte's sign bit. `LBU` reads the same byte but fills the upper 24 bits with zeros.

### Example: `LW x6, 4(x1)` — Load word 4 bytes past the address in x1

```
imm = 4, rs1 = 1, funct3 = 010, rd = 6, opcode = 0000011

Binary: 000000000100 | 00001 | 010 | 00110 | 0000011
Hex:    0x0040A303
```

In a simulator:

```cpp
case 0b0000011: { // LOAD
    uint32_t addr = regs[rs1] + imm_i; // imm_i is sign-extended
    switch (funct3) {
        case 0b000: regs[rd] = (int32_t)(int8_t) mem_read8(addr);  break; // LB
        case 0b001: regs[rd] = (int32_t)(int16_t)mem_read16(addr); break; // LH
        case 0b010: regs[rd] = mem_read32(addr);                   break; // LW
        case 0b100: regs[rd] = (uint8_t)  mem_read8(addr);         break; // LBU
        case 0b101: regs[rd] = (uint16_t) mem_read16(addr);        break; // LHU
    }
    break;
}
```

## Store Instructions (S-Type)

Stores have no destination register. The 12-bit offset is split to keep rs2 in its standard position:

```
Bits [31:25] → imm[11:5]
Bits [24:20] → rs2         (data to store)
Bits [19:15] → rs1         (base address register)
Bits [14:12] → funct3
Bits [11:7]  → imm[4:0]
Bits [6:0]   → 0100011
```

Effective address = `regs[rs1] + sign_extend(imm)`

Data written to memory = lower N bytes of `regs[rs2]`.

### Store Variants

| funct3 | Instruction | Bytes stored |
|--------|-------------|-------------|
| 000    | SB          | 1 byte (bits [7:0]) |
| 001    | SH          | 2 bytes (bits [15:0]) |
| 010    | SW          | 4 bytes (full word) |

### Example: `SW x5, 8(x2)` — Store word in x5 to address x2+8

```
imm = 8 → imm[11:5] = 0000000, imm[4:0] = 01000
rs2 = 5, rs1 = 2, funct3 = 010, opcode = 0100011

Binary: 0000000 | 00101 | 00010 | 010 | 01000 | 0100011
Hex:    0x00512423
```

Extracting the split immediate in C:

```c
int32_t imm_s(uint32_t instr) {
    uint32_t upper = (instr >> 25) & 0x7F;  // imm[11:5]
    uint32_t lower = (instr >> 7)  & 0x1F;  // imm[4:0]
    uint32_t raw   = (upper << 5) | lower;
    // sign-extend from bit 11
    if (raw & 0x800) return (int32_t)(raw | 0xFFFFF000u);
    return (int32_t)raw;
}
```

## Alignment Requirements

RV32I requires natural alignment by default:
- `LW`/`SW` — address must be 4-byte aligned.
- `LH`/`LHU`/`SH` — address must be 2-byte aligned.
- `LB`/`LBU`/`SB` — any address.

In your VP, unaligned accesses to the "Zicsr" extension do not exist in base RV32I — you may choose to raise a load-address-misaligned exception (cause code 4) or support unaligned accesses via the platform memory model.

## Common Pitfalls

- **Mixing rs2 into the S-type immediate.** The field [11:7] is `imm[4:0]`, not `rd`. Confusing these is the number one S-type decode bug.
- **Forgetting sign extension on the offset.** A negative offset like `LW x1, -4(sp)` will compute the wrong address if you treat the immediate as unsigned.
- **Wrong cast for LBU.** After reading a byte, cast to `uint8_t` before widening to 32 bits; casting a signed `int8_t` first gives the signed-extended value, which is correct for LB but wrong for LBU.

> **Interview answer:** "RISC-V loads are I-type (one contiguous 12-bit signed offset); stores are S-type (offset split into two fields to keep rs2 in its standard position). The effective address is always rs1 + sign_extend(offset)."
