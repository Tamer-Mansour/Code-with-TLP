# ISA Compatibility and Evolution

An ISA's longevity depends on how well it balances two conflicting goals: **stability** (old binaries keep running) and **progress** (new instructions for new workloads). This lesson examines the strategies ISA designers use and the real-world consequences of their choices.

## Why Compatibility Is Hard to Break

Once an ISA ships with software running on it, changing semantics is economically painful:

- Millions of compiled binaries may exist.
- Operating system kernels use privileged instructions that are especially hard to replace.
- Security libraries depend on exact ISA-level atomicity guarantees.

Breaking backward compatibility forces every binary to be recompiled — a realistic option only when an ecosystem is small (early life of a new ISA) or when the platform owner controls the entire stack.

> **Interview answer:** "Breaking ISA backward compatibility requires recompiling all software, which is infeasible at scale unless the platform owner controls the full stack, as Apple did in the M1 transition."

## Extension Strategy

The most common way to evolve an ISA without breaking compatibility is to add optional **extensions** that old processors ignore but new processors implement.

### RISC-V Modular Extensions

RISC-V was explicitly designed for modular extension. The base integer ISA (RV32I or RV64I) is frozen. Each optional extension is a single letter:

```
I  — base integer (mandatory)
M  — integer multiply / divide
A  — atomic memory operations
F  — single-precision floating-point (IEEE 754)
D  — double-precision floating-point
C  — compressed 16-bit instructions
V  — vector processing
H  — hypervisor support
Zicsr — CSR access instructions
```

The common profile `RV64GC` = `I + M + A + F + D + C` for 64-bit general-purpose cores.

Software detects available extensions at runtime via the `misa` CSR (machine ISA register):

```asm
csrr a0, misa    # read misa into a0
# bit 12 = 1 → M extension present
# bit  0 = 1 → A extension present
```

### x86 CPUID

x86 uses the `CPUID` instruction to enumerate supported features. Compilers and runtimes check these bits before using newer instructions:

```c
// Check for SSE4.2 support (bit 20 of ECX from CPUID leaf 1)
uint32_t ecx;
__asm__("cpuid" : "=c"(ecx) : "a"(1) : "ebx", "edx");
bool has_sse42 = (ecx >> 20) & 1;
```

Linux's `ifunc` mechanism uses `CPUID` at dynamic link time to choose between multiple implementations of a function (e.g., a memcpy optimized for AVX-512 vs. SSE4.2 vs. scalar).

## Famous ISA Transitions

### x86 → x86-64 (EM64T / AMD64, 2003)

AMD extended 32-bit x86 to 64-bit (AMD64) by:
- Doubling register count (8 → 16 general-purpose registers).
- Extending registers to 64 bits.
- Adding a new 64-bit operating mode.
- Making the 16-bit real mode and some legacy instructions unavailable in 64-bit mode.

Old 32-bit user binaries still run in a compatibility sub-mode inside 64-bit long mode. The OS chooses per-process mode.

### PowerPC → Apple Silicon (ARM, 2020)

Apple migrated macOS from Intel x86-64 to ARM64 (Apple M-series). Binary compatibility was bridged by:
- **Rosetta 2**: an ahead-of-time translator that recompiles x86-64 binaries to ARM64 on first run.
- **Universal Binaries**: fat Mach-O binaries that contain both x86-64 and ARM64 slices.

This is a complete ISA break — Rosetta 2 provides emulation, not true compatibility.

### RISC-V Stability Guarantee

The RISC-V International organization ratified a policy: once an extension is frozen (marked "ratified"), its instruction semantics are **permanent**. Future versions can only add new extensions, never change existing ones.

## Versioning and Profiles

Managing a large ISA requires versioning:

```
RISC-V ISA specification version 20191213
  Base ISA: rv64i v2.1
  M extension: v2.0
  A extension: v2.1
  F extension: v2.2
```

**Profiles** are named subsets that a market segment should implement. For example, the `RVA22` profile defines what a 2022-vintage application processor must implement, giving OS vendors a stable target.

## Deprecation Without Removal

A softer approach than removal is **deprecation**: marking instructions as discouraged without removing them. Future compilers stop generating them; documentation warns against them; but old binaries still execute correctly.

x86 has deprecated (but not removed):
- Segment registers (mostly vestigial in 64-bit mode).
- BCD arithmetic instructions (`DAA`, `DAS`).
- The `ENTER` and `LEAVE` instructions (still valid but slower than equivalent sequences).

## Pitfall: Assuming Extensions Are Present

A common embedded systems bug:

```c
// Fails silently on RV32I cores without M extension
int quotient = a / b;  // compiler emits 'div' — illegal instruction trap!
```

The fix: configure the compiler with the correct `-march` flag:

```bash
# RV32I only — compiler will call __divsi3 software library instead of 'div'
riscv32-unknown-elf-gcc -march=rv32i ...

# RV32IM — 'div' instruction is legal
riscv32-unknown-elf-gcc -march=rv32im ...
```
