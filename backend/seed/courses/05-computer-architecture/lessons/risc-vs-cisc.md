# RISC vs CISC Architectures

Two dominant philosophies have shaped processor design since the 1980s: **RISC** (Reduced Instruction Set Computer) and **CISC** (Complex Instruction Set Computer). Understanding them helps explain why ARM processors dominate mobile devices while x86 still rules the desktop and server world.

## CISC Philosophy

**Goal**: make it easier for compilers (and assembly programmers) by providing many powerful, variable-length instructions.

Key characteristics:
- **Variable-length instructions** (x86: 1–15 bytes).
- Instructions can **directly operate on memory** (e.g., `ADD [addr], reg`).
- Many specialized instructions (string copy, BCD arithmetic, etc.).
- Fewer registers (x86-32 has only 8 general-purpose registers).
- Complex decoder hardware; often uses microcode.

Example (x86 add with memory operand):
```asm
; Add the value at memory address [rbp-4] to eax
add eax, DWORD PTR [rbp-4]   ; single instruction, memory access + add
```

## RISC Philosophy

**Goal**: simple, fast instructions that execute in a single cycle on a pipelined datapath.

Key characteristics:
- **Fixed-length instructions** (RISC-V, MIPS, ARM: typically 32 bits).
- **Load/Store architecture**: only dedicated load/store instructions access memory; all arithmetic works on registers.
- Large register file (RISC-V and MIPS: 32 registers).
- Simpler decoder, no microcode needed.
- Compiler must explicitly manage loads and stores.

Equivalent RISC-V sequence:
```asm
lw   t0, -4(sp)      # load word from memory into t0
add  a0, a0, t0      # add t0 to a0
```

## Performance Trade-offs

| Property | CISC (x86) | RISC (RISC-V / ARM) |
|---|---|---|
| Code density | Higher (fewer bytes) | Lower (more instructions) |
| Decode complexity | High | Low |
| Pipeline efficiency | Harder | Easier |
| Register pressure | High (few registers) | Low (many registers) |
| Power consumption | Higher | Lower |

In practice, modern x86 CPUs translate CISC instructions into RISC-like micro-ops internally, blurring the distinction at the microarchitecture level.

## Common ISAs Today

| ISA | Family | Used in |
|---|---|---|
| x86-64 | CISC | PCs, servers (Intel, AMD) |
| ARM64 (AArch64) | RISC | Mobile, Apple Silicon, cloud |
| RISC-V | RISC (open) | Embedded, research, growing HPC |
| MIPS | RISC | Network equipment, older consoles |
| POWER | RISC | IBM servers |

## ARM: The Mobile Dominance

ARM's RISC design enables extremely power-efficient chips — essential for battery-powered devices. Apple's M-series chips (based on ARM) demonstrate that RISC can also achieve top performance when paired with a wide superscalar design.

## Why RISC-V Matters

RISC-V is an **open, royalty-free** ISA with a minimal base and optional extensions. It is increasingly used in:
- Embedded microcontrollers
- Research CPUs
- RISC-V-based server chips (emerging)
- Custom AI accelerators

Its simplicity makes it ideal for learning CPU design.
