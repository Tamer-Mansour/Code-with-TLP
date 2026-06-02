# RV32, RV64, and RV128

RISC-V is defined for multiple address-space widths. The number in the name — 32, 64, or 128 — refers to the width of the integer registers and the memory address space, not to the data bus or the word size of every instruction. Understanding what changes and what stays the same across these variants is essential for writing portable code and selecting the right target.

## What the Number Means

The bit-width prefix defines:

1. **XLEN** — The width of the integer general-purpose registers (x0–x31).
2. **Address space size** — The number of addressable bytes: 2^32, 2^64, or 2^128.
3. **Width of PC** — The program counter is XLEN bits wide.

It does **not** change the number of instructions, the structure of the register file, or the memory model in any fundamental way. A program written in C and compiled for RV32I versus RV64I will produce different machine code, but the C source itself is (usually) portable if you avoid pointer-size assumptions.

| Variant | XLEN | Address Space | Typical Use |
|---|---|---|---|
| RV32I | 32-bit | 4 GB | Microcontrollers, embedded, IoT |
| RV64I | 64-bit | 16 EB | Linux servers, desktops, phones |
| RV128I | 128-bit | 40 ZB | Future research (draft only) |

> **Interview answer:** "RV32 and RV64 differ in register width and address space. RV32 has 32-bit registers and can address up to 4 GB; RV64 has 64-bit registers with a vastly larger address space. The instruction encoding and base ISA structure are otherwise identical."

## RV32I: The Embedded Workhorse

RV32I is the baseline for embedded and microcontroller applications:

- 32 general-purpose registers, each 32 bits wide.
- Maximum addressable memory: 4 GB (rarely fully used in embedded).
- Very small instruction decoder area.
- Can run C programs, RTOS kernels (FreeRTOS, Zephyr), and bare-metal firmware.

The `RV32E` variant reduces the register file to 16 registers (x0–x15) for even smaller silicon area, targeting ultra-constrained MCUs.

## RV64I: The General-Purpose Standard

RV64I is the standard for operating-system-capable processors:

- 32 general-purpose registers, each 64 bits wide.
- Maximum addressable memory: 16 exabytes (theoretical; practical implementations are more limited).
- Linux, FreeBSD, and other OSes run natively on RV64.
- Required for servers, workstations, smartphones.

RV64 adds **word-width instruction variants** for 32-bit operations on 64-bit hardware:

```asm
# RV64 instructions operating on 32-bit values (results sign-extended to 64 bits)
addw   x1, x2, x3     # 32-bit add, result sign-extended to 64 bits
sllw   x1, x2, x3     # 32-bit shift left logical
mulw   x1, x2, x3     # 32-bit multiply (with M extension)
```

The `W`-suffix instructions are only present in RV64; they do not exist in RV32.

## Key Differences in Detail

### Integer Division and Multiplication

With the M extension:

```asm
# RV32I + M:
mul    x1, x2, x3     # x1 = lower 32 bits of x2 * x3
mulh   x1, x2, x3     # x1 = upper 32 bits (signed * signed)

# RV64I + M:
mul    x1, x2, x3     # x1 = lower 64 bits of x2 * x3
mulw   x1, x2, x3     # x1 = lower 32 bits, sign-extended to 64
```

### Load and Store Width

Both RV32 and RV64 support byte (8-bit), halfword (16-bit), and word (32-bit) loads and stores. RV64 adds **doubleword** (64-bit) loads and stores:

```asm
lb   x1, 0(x2)    # Load byte (sign-extend) — both RV32 and RV64
lh   x1, 0(x2)    # Load halfword — both
lw   x1, 0(x2)    # Load word — both
ld   x1, 0(x2)    # Load doubleword — RV64 only
```

### C Pointer Size

In C code compiled for RISC-V:

```c
// On RV32:
sizeof(void*) == 4    // 4 bytes, 32-bit pointer
sizeof(long)  == 4    // long is 32-bit

// On RV64:
sizeof(void*) == 8    // 8 bytes, 64-bit pointer
sizeof(long)  == 8    // long is 64-bit (LP64 model)
```

This is the most common source of portability bugs when moving code between RV32 and RV64.

## RV128I: Future Research

RV128I is defined in the specification as a draft standard. Its use cases include:

- Extremely large in-memory databases
- Future memory technologies with 128-bit address needs
- Research into memory-safe architectures

No commercial RV128 processor exists as of 2025. The specification includes it to future-proof the ISA design.

## Choosing Between RV32 and RV64

| Factor | Choose RV32 | Choose RV64 |
|---|---|---|
| Memory needs | Less than 4 GB | More than 4 GB |
| OS support needed | Bare-metal / RTOS | Linux / full OS |
| Power/area budget | Tight | Flexible |
| Compiler ecosystem | Good | Excellent |

## Common Pitfalls

- **Pitfall:** Assuming RV64 software runs on RV32 hardware. It does not — they are different ABIs and binary formats.
- **Pitfall:** Forgetting that `long` is 64-bit on RV64 but 32-bit on RV32. Mixing `int` and `long` arithmetic carelessly causes bugs.
- **Pitfall:** Expecting `W`-suffix instructions on RV32. They are RV64-only and will cause an illegal instruction exception if executed on RV32.

The XLEN distinction is simple in concept but has pervasive implications for the ABI, compiler output, and any code that makes assumptions about pointer or integer sizes.
