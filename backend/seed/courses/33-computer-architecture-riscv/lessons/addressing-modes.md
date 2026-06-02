# Addressing Modes Explained

An **addressing mode** specifies how an instruction computes the effective address (EA) — the final memory location — of an operand. The richer an ISA's addressing modes, the more expressive a single instruction can be, but the more complex the hardware decoder becomes.

## Why Addressing Modes Matter

Consider accessing element `i` of an integer array in C:

```c
int a[100];
int val = a[i];   // address = base_of_a + i * 4
```

Without flexible addressing modes a compiler must emit two extra instructions (a multiply and an add) just to compute the address. A **scaled-index** addressing mode folds this into zero extra instructions.

## Mode-by-Mode Reference

### 1. Immediate

The operand **value** is embedded directly in the instruction encoding. No memory access needed.

```asm
addi x1, x0, 42    # x1 = 0 + 42
```

- Fast: the value arrives with the instruction.
- Limited range: RISC-V uses 12-bit sign-extended immediates (−2048 to 2047).
- For 32-bit constants: use `lui` (load upper 20 bits) + `addi` (lower 12 bits).

### 2. Register Direct

The operand is already in a register. No memory access.

```asm
add x3, x1, x2    # EA is irrelevant — value is x1 and x2
```

The fastest mode; the register file is accessed in a single cycle.

### 3. Register Indirect (Base)

The register holds a **memory address**. The instruction reads or writes that address.

```asm
lw x5, 0(x6)     # x5 = Mem[ x6 + 0 ]
```

Equivalent to pointer dereference: `x5 = *ptr` in C, where `x6` holds `ptr`.

### 4. Base + Offset (Displacement)

A **signed constant offset** is added to a base register to form the effective address.

```asm
lw x5, 8(x6)     # EA = x6 + 8
```

This is the **only memory addressing mode in RISC-V**. It covers:

```c
struct Point { int x; int y; };
// p->y compiles to:
lw t0, 4(a0)     # a0 = &p, offset 4 = field y
```

And stack frame access:

```asm
lw a0, -8(fp)    # load local variable from stack frame
```

> **Interview answer:** "RISC-V intentionally supports only base+offset addressing to keep the decoder simple and every load/store latency predictable. Compilers compute complex addresses using separate ALU instructions."

### 5. PC-Relative

Effective address = PC + sign-extended offset. Used for branches and position-independent code.

```asm
beq x1, x2, +20    # if x1 == x2, PC = PC + 20
auipc x1, 0        # x1 = PC (used to build PC-relative data addresses)
```

The assembler converts labels to PC-relative byte offsets at assemble time. This allows shared libraries to load at any virtual address without patching absolute addresses.

### 6. Scaled Index (x86-specific)

```asm
; x86-64
mov eax, [rbx + rcx*4]    ; EA = rbx + rcx * 4
```

Scale factors 1, 2, 4, 8 directly support arrays of byte, short, int, and long. RISC-V has no scaled-index mode; the compiler must emit an explicit `slli` (shift) before the load.

### 7. Absolute (Direct)

The instruction word contains the full memory address. Feasible in 16-bit or 32-bit ISAs; impractical in 64-bit ISAs because 64-bit addresses would not fit in a fixed-width instruction word.

Some ISAs support it as a two-word encoding; RISC-V prefers PC-relative + `auipc`.

## Summary Table

| Mode | Effective Address | Typical Use |
|---|---|---|
| Immediate | value in instruction | Constants, small literals |
| Register | register value | Fast computation |
| Register Indirect | Mem[reg] | Pointer dereference |
| Base + Offset | Mem[reg + imm] | Struct fields, stack frames |
| PC-Relative | PC + imm | Branches, PIC, shared libs |
| Scaled Index (x86) | Mem[base + idx × scale] | Array element access |
| Absolute | Mem[address in instruction] | Legacy/16-bit systems |

## RISC vs CISC Addressing Philosophy

| ISA | Memory Modes Supported | Trade-off |
|---|---|---|
| RISC-V | Base + offset only | Simple decoder; compiler does more work |
| ARM | Base + offset, pre/post-index | Moderate complexity; useful for loops |
| x86 | All of the above + scaled index | Dense code; complex decoder hardware |

## Worked Example: Array Loop in RISC-V

```asm
# int sum = 0; for (int i = 0; i < n; i++) sum += a[i];
# a0 = &a[0], a1 = n, result in a2
    li    a2, 0          # sum = 0
    li    t0, 0          # i = 0
loop:
    bge   t0, a1, done   # if i >= n, exit
    slli  t1, t0, 2      # t1 = i * 4  (byte offset)
    add   t2, a0, t1     # t2 = &a[i]
    lw    t3, 0(t2)      # t3 = a[i]   (base+offset, offset=0)
    add   a2, a2, t3     # sum += a[i]
    addi  t0, t0, 1      # i++
    j     loop
done:
```

The `slli` + `add` pair is the compiler's substitute for a scaled-index mode.
