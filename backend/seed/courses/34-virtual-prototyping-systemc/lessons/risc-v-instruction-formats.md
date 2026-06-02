# RISC-V Instruction Formats: R, I, S, B, U, J

Every 32-bit RISC-V base instruction belongs to one of six encoding formats. The formats share a common skeleton — the opcode is always in bits [6:0] — but differ in how immediate values and register fields are arranged. Knowing these six layouts cold is the foundation of every ISA simulator and hardware decode unit.

## The Six Formats at a Glance

```
Bit position: 31      25 24   20 19   15 14  12 11    7 6      0
              ─────────────────────────────────────────────────────
R-type        [ funct7 ] [ rs2 ] [ rs1 ] [fn3] [  rd  ] [opcode]
I-type        [   imm[11:0]    ] [ rs1 ] [fn3] [  rd  ] [opcode]
S-type        [imm[11:5]] [rs2] [ rs1 ] [fn3] [imm[4:0]] [opcode]
B-type        [imm[12|10:5]] [rs2] [rs1] [fn3] [imm[4:1|11]] [opcode]
U-type        [         imm[31:12]        ] [  rd  ] [opcode]
J-type        [    imm[20|10:1|11|19:12]  ] [  rd  ] [opcode]
```

## R-Type (Register-Register)

Used for arithmetic and logic operations where both operands come from registers.

| Field   | Bits     | Width |
|---------|----------|-------|
| funct7  | [31:25]  | 7 b   |
| rs2     | [24:20]  | 5 b   |
| rs1     | [19:15]  | 5 b   |
| funct3  | [14:12]  | 3 b   |
| rd      | [11:7]   | 5 b   |
| opcode  | [6:0]    | 7 b   |

The `funct7` + `funct3` combination selects the operation. For example, `ADD` has funct7=0000000 and funct3=000; `SUB` shares funct3=000 but uses funct7=0100000.

**Example:** `ADD x3, x1, x2` — adds registers x1 and x2, writes result to x3.

## I-Type (Immediate)

Used for loads, arithmetic-with-immediate, CSR access, and `JALR`.

- Immediate is **12 bits**, sign-extended to XLEN before use.
- The immediate occupies a single contiguous field [31:20], making extraction simple.

```cpp
int32_t imm_i = (int32_t)(instr) >> 20; // arithmetic right-shift sign-extends
```

**Examples:** `ADDI`, `LW`, `LB`, `JALR`, `ECALL`.

## S-Type (Store)

Stores have no destination register, so the 12-bit immediate is **split** across two fields to keep rs1 and rs2 in their standard positions.

| Immediate part | Bits    |
|----------------|---------|
| imm[11:5]      | [31:25] |
| imm[4:0]       | [11:7]  |

```cpp
int32_t imm_s = ((int32_t)(instr) >> 20 & ~0x1F)  // upper 7 bits, sign-extended
              | ((instr >> 7) & 0x1F);              // lower 5 bits
```

**Examples:** `SW`, `SH`, `SB`.

## B-Type (Branch)

Branch instructions encode a **PC-relative offset** pointing to a 16-bit-aligned address. The bits are scrambled to keep rs1 and rs2 in their standard positions and to share hardware with S-type decode:

| Immediate bit | Encoding location |
|---------------|-------------------|
| imm[12]       | bit [31]          |
| imm[10:5]     | bits [30:25]      |
| imm[4:1]      | bits [11:8]       |
| imm[11]       | bit [7]           |
| imm[0]        | always 0 (implicit) |

```cpp
int32_t imm_b = ((int32_t)(instr) >> 19 & ~0xFFF)  // sign bit -> bit[12]
              | ((instr << 4)  & 0x800)              // bit[7]  -> bit[11]
              | ((instr >> 20) & 0x7E0)              // [30:25] -> [10:5]
              | ((instr >> 7)  & 0x1E);              // [11:8]  -> [4:1]
```

**Examples:** `BEQ`, `BNE`, `BLT`, `BGE`, `BLTU`, `BGEU`.

> **Common pitfall:** Bit [0] of a B-type immediate is always zero (branches target even addresses). Do not add it — it is not encoded.

## U-Type (Upper Immediate)

Loads a 20-bit constant into the upper 20 bits of a register. The immediate is **not** sign-extended — it occupies bits [31:12] of the result directly.

```cpp
int32_t imm_u = instr & 0xFFFFF000; // mask out opcode + rd, keep upper 20 bits
```

**Examples:** `LUI` (load upper immediate), `AUIPC` (add upper immediate to PC).

## J-Type (Jump)

`JAL` uses J-type encoding. Like B-type, bits are scrambled to share hardware with U-type:

| Immediate bit | Encoding location |
|---------------|-------------------|
| imm[20]       | bit [31]          |
| imm[10:1]     | bits [30:21]      |
| imm[11]       | bit [20]          |
| imm[19:12]    | bits [19:12]      |
| imm[0]        | always 0          |

The 21-bit signed offset supports a ±1 MB jump range.

## Summary Table

| Format | Immediate width | Sign-extended? | Primary uses |
|--------|----------------|---------------|-------------|
| R | — | — | ALU reg-reg |
| I | 12 bit | Yes | Load, ALU-imm, JALR |
| S | 12 bit | Yes | Store |
| B | 13 bit (bit 0=0) | Yes | Branch |
| U | 20 bit (upper) | No | LUI, AUIPC |
| J | 21 bit (bit 0=0) | Yes | JAL |

> **Interview answer:** "RISC-V has six instruction formats. R has no immediate; I has a 12-bit immediate in one piece; S and B split the immediate to keep register fields aligned; U and J handle 20-bit and 21-bit PC-relative constants respectively."
