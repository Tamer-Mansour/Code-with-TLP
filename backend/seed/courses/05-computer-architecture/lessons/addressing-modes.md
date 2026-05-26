# Addressing Modes

An **addressing mode** specifies how an instruction determines the memory address (or value) it operates on. Different ISAs provide different sets of addressing modes, trading hardware complexity for code density.

## Why Addressing Modes Matter

Consider storing the 5th element of an array `a` starting at address `base` with stride 4 (int array):

- If the CPU only supports absolute addressing: `STORE reg, (base + 4*4)` — the address must be computed and hard-coded at compile time (doesn't work for dynamic indices).
- With base+index addressing: `STORE reg, [base + index*4]` — one instruction, works for any runtime index.

## Common Addressing Modes

### Immediate

The operand value is **embedded in the instruction** itself (a constant).

```asm
addi x1, x0, 42    # x1 = 0 + 42 = 42
```

Fast — no extra memory access needed. Limited range (12 bits in RISC-V = −2048 to 2047).

### Register Direct

The operand is in a **register**.

```asm
add x3, x1, x2    # x3 = x1 + x2
```

Fastest addressing mode; no memory access.

### Register Indirect (Base)

The register holds a **memory address**; the instruction accesses that address.

```asm
lw x5, 0(x6)     # x5 = Memory[ x6 ]
```

Used for pointer dereferences: `*p` in C.

### Base + Offset (Displacement)

Add a signed constant **offset** to a base register to form the address.

```asm
lw x5, 8(x6)     # x5 = Memory[ x6 + 8 ]
```

Used for struct field access and stack frames:

```c
struct Point { int x; int y; };  // x at offset 0, y at offset 4
// p->y in assembly:
lw t0, 4(a0)     # a0 = &p, t0 = p->y
```

### PC-Relative

Address = PC + sign-extended offset. Used for branches and position-independent code.

```asm
beq x1, x2, +20   # if x1==x2, jump to PC+20
```

The offset is measured from the current (or next) PC. Labels in assembly are translated to PC-relative offsets by the assembler.

### Scaled Index (x86 only)

```asm
; x86: mov eax, [rbx + rcx*4]
; address = rbx + rcx * scale (scale ∈ {1,2,4,8})
```

Ideal for array access: `a[i]` where element size is 1, 2, 4, or 8 bytes.

### Absolute (Direct)

The instruction contains the full address. Rare in modern 64-bit ISAs because addresses are 64 bits wide — they would not fit in a 32-bit instruction word.

## Addressing Mode Summary

| Mode | EA Formula | Use Case |
|---|---|---|
| Immediate | value in instruction | Constants |
| Register | reg value | Fast computation |
| Register Indirect | Mem[reg] | Pointer dereference |
| Base + Offset | Mem[reg + imm] | Struct fields, stack |
| PC-Relative | Mem[PC + imm] | Branches, PIC |
| Scaled Index (x86) | Mem[base + idx*s] | Array indexing |

## ISA Design Choices

RISC-V deliberately supports only **base+offset** for memory access. This simplicity means:
- Smaller decoder logic.
- Every load/store has a predictable latency.
- Compilers must emit explicit address-computation instructions.

x86 supports rich addressing modes, which improve code density but complicate the decoder and pipeline.
