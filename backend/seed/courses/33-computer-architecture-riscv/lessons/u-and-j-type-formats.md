# U-Type and J-Type Formats

U-type and J-type are the two formats that carry **20-bit immediates** — the largest constants a single RISC-V instruction can express. U-type places the constant in the upper 20 bits of the result. J-type encodes a 21-bit PC-relative jump offset (20 bits explicit, bit 0 implied zero).

## U-Type

### Bit Layout

```
 31                        12 11      7 6       0
+----------------------------+---------+---------+
|        imm[31:12]          |   rd    | opcode  |
|          20 bits           |  5 bits |  7 bits |
+----------------------------+---------+---------+
```

The 20-bit immediate occupies bits [31:12] **exactly as written**. The processor places them into the upper 20 bits of the destination register and zeros the lower 12 bits.

### U-Type Instructions

| Mnemonic | opcode   | Operation |
|----------|----------|-----------|
| `lui`    | 0110111  | rd = imm[31:12] << 12 |
| `auipc`  | 0010111  | rd = PC + (imm[31:12] << 12) |

```asm
lui   x5, 0x12345   # x5 = 0x12345000
auipc x5, 4         # x5 = PC + 0x4000 (4 pages up)
```

`lui` followed by `addi` is the standard two-instruction sequence to load an arbitrary 32-bit constant:

```asm
lui   x5, 0xDEADB   # x5 = 0xDEADB000
addi  x5, x5, 0xEEF # x5 = 0xDEADBEEF
```

**Caution**: if the lower 12 bits of the target are >= 0x800 (i.e., the `addi` immediate is negative when sign-extended), you must add 1 to the `lui` immediate to compensate. Assemblers handle this automatically; hand-encoders often forget.

### Worked Example: Encoding `lui x3, 0xABCDE`

- **opcode** = 0110111
- **rd** = x3 = 00011
- **imm[31:12]** = 0xABCDE = 1010 1011 1100 1101 1110

```
10101011110011011110  00011  0110111
   imm[31:12]          rd    opcode
```

Hex: `0xABCDE1B7`

## J-Type

### Bit Layout

```
 31      30      21 20 19        12 11      7 6       0
+-------+---------+--+------------+---------+---------+
|imm[20]|imm[10:1]|imm[11]|imm[19:12]|  rd  | opcode |
| 1 bit | 10 bits |1 bit  |  8 bits  | 5 bits| 7 bits |
+-------+---------+-------+----------+-------+--------+
```

Like B-type, the immediate bits are scrambled. The 21-bit offset (bit 0 is always 0, so 20 bits are stored) is split as:

| Instruction bits | Immediate bits |
|------------------|----------------|
| [31]             | imm[20] (sign) |
| [30:21]          | imm[10:1] |
| [20]             | imm[11] |
| [19:12]          | imm[19:12] |

Reconstruction:

```c
int32_t imm =
    ((inst >> 31) & 1)    << 20 |
    ((inst >> 12) & 0xFF) << 12 |
    ((inst >> 20) & 1)    << 11 |
    ((inst >> 21) & 0x3FF)<< 1;
imm = (imm << 11) >> 11;  // sign-extend from bit 20
```

Range: -1 MB to +1 MB (±1,048,576 bytes), in steps of 2.

### J-Type Instruction

Only one base instruction uses J-type: **JAL** (Jump and Link), opcode `1101111`.

```asm
jal  x1, 64     # x1 = PC+4 (return address); PC += 64
jal  x0, -8     # unconditional jump back 8 bytes (x0 discards link)
```

`jal x0, offset` is the standard unconditional jump (the link register x0 silently discards the return address).

### Worked Example: Encoding `jal x1, 100`

- offset = 100 = 0b0_0000_0110_0100; imm[20]=0, imm[19:12]=00000000, imm[11]=0, imm[10:1]=0001100100
- **opcode** = 1101111, **rd** = x1 = 00001

```
0  0001100100  0  00000000  00001  1101111
imm[20] imm[10:1] imm[11] imm[19:12] rd opcode
```

Hex: `0x064000EF`

## Key Differences Between U-Type and J-Type

| Property | U-type | J-type |
|----------|--------|--------|
| Immediate width | 20 bits (contiguous in instruction) | 20 bits stored (21 with implied 0) |
| Bit scrambling | None — bits [31:12] go directly | Heavily scrambled |
| PC-relative? | auipc yes, lui no | Always (JAL only) |
| Instructions | lui, auipc | jal |

## Interview Answer

> "U-type stores a clean 20-bit immediate in bits [31:12] — no scrambling — for `lui` and `auipc`. J-type encodes a 21-bit PC-relative offset for `jal` with the same scrambling rationale as B-type: sign bit at bit 31, and adjacent output bits kept adjacent in the instruction word to minimize routing."
