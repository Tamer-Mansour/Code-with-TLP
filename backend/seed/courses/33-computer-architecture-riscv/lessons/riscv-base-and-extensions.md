# Base Integer ISA and Standard Extensions

One of the most deliberate design choices in RISC-V is the split between a minimal, stable **base ISA** and a set of optional, composable **extensions**. This modularity is not an afterthought — it is the core architectural philosophy that enables RISC-V to serve both 32-bit embedded microcontrollers and 64-bit server processors using the same specification framework.

## The Base Integer ISA

RISC-V defines several base integer ISAs, each identified by a letter and a bit-width:

| Name | Width | Description |
|---|---|---|
| RV32I | 32-bit | Base integer, 32-bit address space |
| RV64I | 64-bit | Base integer, 64-bit address space |
| RV128I | 128-bit | Base integer, 128-bit address space (draft) |
| RV32E | 32-bit | Embedded variant with only 16 registers |

**RV32I** is the most minimal complete ISA. It contains exactly 47 instructions covering:
- Integer arithmetic (ADD, SUB, AND, OR, XOR, shifts)
- Loads and stores (byte, halfword, word)
- Branches and jumps
- Upper-immediate instructions (LUI, AUIPC)
- System calls (ECALL, EBREAK)

A processor implementing only RV32I can run a C program, execute a kernel system call, and support a debugger. It is intentionally minimal — everything else is an extension.

> **Interview answer:** "The RISC-V base ISA (e.g., RV32I) defines the minimum set of instructions needed for a general-purpose computer. Extensions add optional capabilities like multiplication, floating point, or atomics, allowing designers to include only what their application needs."

## Standard Extensions

RISC-V defines a set of standard extensions, each identified by a single letter:

| Extension | Letter | Description |
|---|---|---|
| Integer Multiply/Divide | M | MUL, DIV, REM instructions |
| Atomic Operations | A | Load-reserved / store-conditional; AMOs |
| Single-Precision Float | F | 32-bit IEEE 754 floating point |
| Double-Precision Float | D | 64-bit IEEE 754 floating point |
| Compressed Instructions | C | 16-bit encodings for common instructions |
| Quad-Precision Float | Q | 128-bit floating point |
| Vector | V | SIMD-style vector operations |
| Bit Manipulation | B | Bitfield insert/extract, rotate, count |
| Hypervisor | H | Hardware virtualization support |
| Privileged | (spec doc) | Machine, Supervisor, User privilege levels |

Extensions are **composable** — you pick exactly what you need. A small sensor node might implement only RV32IC (base + compressed) to minimize code size. A high-performance compute node might implement RV64GCBV (base + compressed + bit manipulation + vector).

## The "G" Shorthand

The letter **G** is a shorthand for the most common general-purpose combination:

```
G = I + M + A + F + D + Zicsr + Zifencei
```

So `RV64G` means a 64-bit processor with integer, multiply, atomics, single-float, and double-float — the typical baseline for a Linux-capable chip. Most desktop and server RISC-V processors target at least RV64GC (G plus compressed).

## Naming: Standard vs. Non-Standard Extensions

RISC-V extensions fall into categories:

- **Standard ratified** — Reviewed and frozen by RISC-V International (M, A, F, D, C, V, etc.)
- **Standard in development** — Proposed but not yet ratified (some B sub-extensions)
- **Custom / non-standard** — Private extensions in reserved opcode space; not interoperable

Custom extensions use the `X` prefix by convention. For example, `Xmyvendor_accel` names a vendor-specific instruction for a custom accelerator. These are invisible to standard toolchains unless vendor patches are applied.

## Worked Example: Choosing Extensions for a Design

Suppose you are building a microcontroller for a smart home thermostat:

```
Requirements:
  - Run simple control logic (integer math only)
  - Communicate over UART (byte-level I/O)
  - Code fits in 64 KB flash
  - No floating-point sensor math (use fixed-point)

Extension choice: RV32EC
  - RV32E: 16-register variant to save area
  - C: 16-bit compressed instructions to reduce code size by ~25%
  - No M: avoid multiplier hardware cost
  - No F/D: no floating-point unit
```

Contrast with a RISC-V application processor for a Linux smartphone:

```
Extension choice: RV64GCV
  - G: full general-purpose baseline
  - C: compressed instructions
  - V: vector extension for media/ML workloads
```

## Sub-Extensions and Z-Extensions

Newer extensions use a `Z` prefix to name sub-features within a domain:

| Name | Description |
|---|---|
| Zicsr | Control and Status Register (CSR) instructions |
| Zifencei | Instruction-fetch fence |
| Zba, Zbb, Zbc, Zbs | Bit-manipulation sub-groups |
| Zfh | Half-precision (16-bit) floating point |
| Ztso | Total Store Ordering memory model |

This granular naming allows hardware designers to include exactly the features they need without bundling unnecessary logic.

## Common Pitfalls

- **Pitfall:** Assuming "RISC-V" implies a specific set of extensions. Always check the full ISA string (e.g., `RV64GC`) when evaluating software compatibility.
- **Pitfall:** Thinking compressed (C) instructions change the programmer's model. They do not — the assembler/compiler transparently uses 16-bit encodings; the programmer writes normal instructions.
- **Pitfall:** Forgetting that floating-point extensions (F, D) add their own register file (f0–f31) separate from the integer registers (x0–x31).

The base-plus-extension model is what makes RISC-V simultaneously useful for a $0.10 sensor node and a high-end server processor. The ISA scales by composition, not by complexity.
