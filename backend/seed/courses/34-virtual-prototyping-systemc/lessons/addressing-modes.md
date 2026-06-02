# Addressing Modes

An **addressing mode** specifies how the effective address (or the value itself) of an operand is computed. ISA designers balance expressiveness — richer addressing modes reduce instruction count — against decode complexity and cycle cost. Understanding addressing modes is essential when modeling the address-computation stage of a CPU.

## Common Addressing Modes

### 1. Immediate (Literal)

The operand value is encoded directly inside the instruction word. No memory access is needed.

```asm
addi x5, x0, 42     ; x5 = 42  (immediate)
li   x6, 0xFF       ; x6 = 255 (pseudo, expands to addi)
```

**Constraint**: the value is limited to the field width (12 bits in RISC-V I-type, sign-extended).

### 2. Register Direct

The operand is the value currently held in a register. This is the fastest mode — no memory involved.

```asm
add x1, x2, x3      ; x1 = x2 + x3  (all register operands)
```

### 3. Base + Displacement (Register Indirect with Offset)

Effective address = `base_register + signed_immediate`. The dominant load/store mode in RISC-V and ARM.

```asm
lw  x5, 8(x6)       ; EA = x6 + 8;  x5 = Memory[EA]
sw  x7, -4(x8)      ; EA = x8 - 4;  Memory[EA] = x7
```

This mode supports stack operations (`sp` as base), struct field access (offset = field offset), and array indexing (base = array start + element*size).

### 4. PC-Relative

Effective address = `PC + signed_immediate`. Used for branch targets and position-independent data loads (RISC-V `AUIPC`).

```asm
beq  x1, x2, +16    ; EA = PC + 16 (branch target)
auipc x3, 0         ; x3 = PC + (0 << 12)  — read current PC
```

### 5. Register Indirect (Base Only, Offset = 0)

A degenerate case of base+displacement with offset zero. Used for indirect function calls and computed jumps.

```asm
jalr x0, x1, 0      ; PC = x1 + 0  (return from function)
```

### 6. Scaled Indexed (x86 / ARM Only)

Effective address = `base + index * scale + displacement`. Powerful for array access — no explicit multiply instruction needed.

```asm
; x86-64: load array element (4-byte ints)
mov eax, [rbx + rcx*4 + 8]   ; EA = rbx + rcx*4 + 8
```

RISC-V does **not** have this mode; the programmer must compute the scaled index explicitly.

### 7. Absolute / Direct

The instruction encodes the full memory address. Rare in modern 64-bit ISAs (address too large to embed), but common in microcontrollers.

```asm
; 8051
MOV A, 0x30     ; load accumulator from address 0x30
```

## Comparison Table

| Mode | Formula | ISA Support |
|---|---|---|
| Immediate | value from instruction | Universal |
| Register | Reg[rs] | Universal |
| Base + Disp | Reg[base] + imm | RISC-V, ARM, x86 |
| PC-Relative | PC + imm | RISC-V, ARM, x86 |
| Register Indirect | Reg[base] | RISC-V (offset=0), x86 |
| Scaled Indexed | base + idx*scale + disp | x86, ARM |
| Absolute | imm | Microcontrollers, x86 |

## Modeling Address Computation in SystemC

```cpp
// Decode and compute effective address for load/store
uint32_t compute_ea(const CpuState& s, uint32_t instr, bool is_store) {
    uint32_t rs1 = (instr >> 15) & 0x1F;
    int32_t  imm;
    if (is_store) {
        // S-type immediate: bits [11:5] = instr[31:25], bits [4:0] = instr[11:7]
        imm = ((int32_t)(instr & 0xFE000000) >> 20)
            | ((instr >> 7) & 0x1F);
    } else {
        // I-type immediate: bits [11:0] = instr[31:20], sign-extended
        imm = (int32_t)instr >> 20;
    }
    return s.rf[rs1] + imm;
}
```

## Common Pitfalls

- **S-type vs I-type immediates** — RISC-V stores use a split immediate (S-type) that is assembled differently from load immediates (I-type). Using I-type decoding for stores produces wrong effective addresses.
- **Scale factor for indexed modes** — in x86 the scale is part of the ModRM/SIB byte, not a register. Forgetting to multiply the index by the element size is a classic bug.
- **Position-dependent code** — using absolute addressing instead of PC-relative breaks position-independent code and shared libraries.

## Interview Answer

> "Addressing modes define how an operand's effective address is calculated. The most common in RISC ISAs is base+displacement — a register plus a signed immediate offset — which covers stack frames, struct fields, and array elements. x86 adds scaled-indexed mode, eliminating explicit multiply for array access at the cost of more complex decode logic."
