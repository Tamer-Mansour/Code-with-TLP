# What Is an Instruction Set Architecture?

An **Instruction Set Architecture (ISA)** is the complete specification of the interface between software and hardware. It defines every operation a CPU can perform, how operands are encoded, the set of programmer-visible registers, the memory model, and the conditions under which exceptions are raised.

Think of the ISA as the CPU's public API: compilers and operating systems program against it, and chip designers implement it—often in radically different ways across product generations.

## The ISA Is Not the Microarchitecture

A common source of confusion is conflating the ISA with the **microarchitecture** (the physical implementation). They are deliberately separated:

| Concept | Definition | Example |
|---|---|---|
| ISA | Abstract machine specification | RISC-V RV32I |
| Microarchitecture | Physical implementation of that spec | In-order 5-stage pipeline |
| Implementation | A specific chip | SiFive FE310 |

The same ISA can be realized by dozens of different microarchitectures. The Intel Core i9 and a classroom educational chip can both implement x86-64 and run identical binaries, yet their internal designs share nothing.

> **Interview answer:** "An ISA defines what the machine can do; the microarchitecture defines how it does it."

## What an ISA Specifies

A complete ISA definition covers:

- **Instruction set** — the full opcode table with precise semantics for each operation.
- **Data types** — supported integer widths (8, 16, 32, 64 bit), floating-point formats (IEEE 754 single/double), and any vector types.
- **Register file** — count, width, and any special-purpose roles (e.g., RISC-V `x0` is hardwired to zero).
- **Memory model** — address space size, alignment requirements, endianness (byte order), and the memory consistency model for multi-core systems.
- **Instruction encoding** — how bits in a 16-, 32-, or variable-length word map to opcode fields, register specifiers, and immediate values.
- **Privilege levels** — machine mode, supervisor mode, user mode in RISC-V; ring 0–3 in x86.
- **Exception and interrupt model** — what faults are defined, how the CPU state is saved, and where control transfers.

## A Short History of ISAs

```
Year  ISA          Key Feature
----  -----------  --------------------------------
1964  IBM System/360  First ISA designed for compatibility across a product line
1978  x86          CISC; variable-length encoding; still dominant on desktops
1985  MIPS         Early commercial RISC; influenced many successors
1990  ARM          Low power RISC; dominant in mobile
2010  RISC-V       Open, royalty-free, modular ISA
```

RISC-V is notable because the base specification is intentionally minimal (47 instructions in RV32I) while optional extensions (M, A, F, D, C, V…) add multiply/divide, atomics, floating-point, compressed encodings, and vectors.

## Why the ISA Matters to Software Engineers

Even when writing high-level code, the ISA affects you:

- **Performance** — knowing that RISC-V has no divide instruction in the base ISA (it lives in the M extension) explains why division is expensive on minimal cores.
- **Portability** — code compiled for x86-64 does not run on ARM without recompilation or emulation.
- **Security** — ISA-level features like memory-protection bits, speculation barriers (`FENCE`, `LFENCE`), and virtual memory are the foundation of OS security.
- **Debugging** — reading disassembly requires knowing the ISA's register names and calling conventions.

## Worked Example: Reading the RISC-V RV32I Add Instruction

```asm
add  x3, x1, x2    # x3 = x1 + x2
```

The ISA specifies:
1. `add` is an R-type instruction (three register operands).
2. The 32-bit encoding is: `funct7 | rs2 | rs1 | funct3 | rd | opcode`.
3. Semantics: `x[rd] = x[rs1] + x[rs2]` (ignoring overflow).

Everything a compiler or debugger needs to produce or interpret this instruction is in the ISA specification — no knowledge of the pipeline depth or cache size is required.
