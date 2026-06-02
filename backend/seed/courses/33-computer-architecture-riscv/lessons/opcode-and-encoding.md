# Opcodes and Instruction Encoding

An **opcode** (operation code) is the bit-field within an instruction word that identifies which operation to perform. Instruction encoding is the complete scheme that maps an instruction and all its operands onto a fixed (or variable) sequence of bits.

Getting encoding right is a critical ISA design decision: it affects instruction fetch bandwidth, decoder complexity, code density, and how many extensions can be added later.

## Anatomy of an Instruction Word

Every instruction word is divided into fields. For RISC-V 32-bit instructions the six field types are:

```
Bit positions (RISC-V RV32 R-type):
31       25 24   20 19   15 14  12 11    7 6       0
+---------+-------+-------+------+--------+---------+
| funct7  |  rs2  |  rs1  |funct3|   rd   | opcode  |
+---------+-------+-------+------+--------+---------+
   7 bits   5 bits  5 bits 3 bits  5 bits    7 bits
```

- **opcode** (bits 6-0): primary operation class (LOAD, STORE, BRANCH, OP, OP-IMM …)
- **funct3** (bits 14-12): discriminates sub-operations within a class (ADD vs. SUB vs. AND …)
- **funct7** (bits 31-25): further discriminates (ADD vs. SUB share the same opcode+funct3; funct7 bit 5 = 0 → ADD, = 1 → SUB)
- **rd, rs1, rs2**: 5-bit register specifiers (0–31)

Together, `opcode + funct3 + funct7` form the logical opcode for R-type instructions.

## RISC-V Instruction Format Types

RISC-V defines six encoding formats to handle different combinations of fields:

| Format | Operands | Immediate bits | Example |
|---|---|---|---|
| R | rd, rs1, rs2 | none | `add x1, x2, x3` |
| I | rd, rs1, imm12 | 12 | `lw x1, 8(x2)`, `addi` |
| S | rs1, rs2, imm12 | 12 (split) | `sw x1, 8(x2)` |
| B | rs1, rs2, imm13 | 13 (split, ×2) | `beq x1, x2, L` |
| U | rd, imm20 | 20 | `lui x1, 0x12345` |
| J | rd, imm21 | 21 (split, ×2) | `jal x1, L` |

The S and B formats split the immediate across two non-contiguous fields to keep `rd` and `rs1` at the same bit positions as R-type and I-type — this simplifies register-file read logic.

> **Interview answer:** "RISC-V keeps `rs1` and `rd` at fixed bit positions across all formats so the decoder can start reading the register file before knowing the exact instruction type."

## Fixed-Width vs Variable-Length Encoding

### Fixed-Width (RISC-V base: 32 bits)

- Decoder always reads exactly 32 bits.
- Simple, fast, pipelineable.
- Less code density — simple operations waste bits.

### Variable-Length (x86: 1–15 bytes)

```
; x86 instruction sizes
90             ; NOP      — 1 byte
89 C3          ; MOV ebx, eax — 2 bytes
48 8B 44 24 08 ; MOV rax, [rsp+8] — 5 bytes
```

- Dense code — common instructions are short.
- Decoder must scan byte by byte to find instruction boundaries.
- x86 has a dedicated pre-decode stage just to split the byte stream into instruction boundaries.

### RISC-V Compressed Extension (RVC)

RISC-V adds optional 16-bit compressed instructions (the C extension) that encode common operations in half the space. The decoder identifies compressed instructions by checking the lowest two bits (`00`, `01`, `10` = 16-bit; `11` = 32-bit):

```asm
c.addi  x1, 4    # 16-bit: x1 += 4  (same as addi x1, x1, 4)
c.lw    x8, 0(x9)# 16-bit load
```

The C extension typically reduces code size by 25–30% for application code.

## Decoding a RISC-V Instruction — Worked Example

Decode the 32-bit hex word `0x004302B3`:

```
Binary: 0000 0000 0100 0011 0000 0010 1011 0011

opcode  = bits[6:0]  = 011 0011 = 0x33 → "OP" (register-register arithmetic)
rd      = bits[11:7] = 0 0101   = 5    → x5
funct3  = bits[14:12]= 000      → ADD/SUB
rs1     = bits[19:15]= 00110    = 6    → x6
rs2     = bits[24:20]= 00100    = 4    → x4
funct7  = bits[31:25]= 000 0000 = 0    → ADD (not SUB)

Instruction: add x5, x6, x4   (x5 = x6 + x4)
```

```python
word = 0x004302B3
opcode = word & 0x7F
rd     = (word >> 7)  & 0x1F
funct3 = (word >> 12) & 0x07
rs1    = (word >> 15) & 0x1F
rs2    = (word >> 20) & 0x1F
funct7 = (word >> 25) & 0x7F
print(f"opcode={opcode:#04x} rd=x{rd} funct3={funct3} rs1=x{rs1} rs2=x{rs2} funct7={funct7:#04x}")
# opcode=0x33 rd=x5 funct3=0 rs1=x6 rs2=x4 funct7=0x00
```

## Common Pitfall: Sign-Extension of Immediates

All RISC-V immediates are **sign-extended** to XLEN before use. A 12-bit field of `0xFFF` is not +4095 — it is −1. This is intentional: it allows negative offsets (stack frames grow downward) and negative branch targets without a separate negative-offset form.
