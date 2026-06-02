# RISC-V vs ARM: Licensing and Design

ARM and RISC-V are both RISC-style ISAs that target overlapping markets — from tiny microcontrollers to powerful application processors. But their licensing models, governance, and design philosophies differ fundamentally. Understanding those differences is essential for engineers choosing a platform and for engineers who will be asked about this in technical interviews.

## At a Glance

| Dimension | ARM | RISC-V |
|---|---|---|
| ISA ownership | Arm Holdings (private company) | RISC-V International (Swiss non-profit) |
| Licensing model | Commercial license, royalties | Royalty-free, open specification |
| Specification access | Under NDA or paid agreement | Free public download |
| Custom extensions | Restricted; requires Arm approval | Explicitly allowed in reserved space |
| ISA age | 1985 (ARM1) | 2010 (RISC-V) |
| Instruction count | Large (hundreds with Thumb, SVE) | Modular; base has 47 instructions |
| Silicon ecosystem | Mature; billions of cores shipped | Fast-growing; >10 billion shipped |
| Toolchain maturity | Excellent | Excellent (GCC, LLVM, QEMU, Linux) |

## Licensing: The Fundamental Difference

ARM's business model is IP licensing. Arm Holdings (owned by SoftBank, with SoftBank and others holding interests post-IPO) licenses:

1. **Architecture licenses** — Permission to design your own microarchitecture implementing the ARM ISA (Apple M-series, Qualcomm Oryon).
2. **Core licenses** — Permission to use Arm's pre-designed cores (Cortex-A76, Cortex-M4) in your chip.

Both license types involve:
- **Upfront fees** (tens of thousands to millions of dollars depending on tier).
- **Per-unit royalties** (typically 1–2% of chip ASP for core licenses).
- **NDA requirements** for detailed specifications.
- **Usage restrictions** on markets, geographies, and application types.
- **Audit rights** — Arm can inspect your books to verify royalty compliance.

RISC-V, by contrast, has no licensing process. You download the specification, implement it, and ship your chip. No fees, no NDAs, no audits.

> **Interview answer:** "The key difference between ARM and RISC-V is licensing. ARM requires a paid commercial license with royalties and usage restrictions. RISC-V is an open specification you can implement royalty-free. Both are RISC ISAs, but RISC-V removes the institutional gatekeeping."

## Design Philosophy Differences

### ARM: Accumulated Complexity

ARM has evolved over 40 years. The ISA includes:

- **A64** (AArch64, 64-bit) — The modern instruction set.
- **A32** (AArch32, legacy 32-bit ARM) — Backward compatibility with ARMv7.
- **T32** (Thumb2) — Variable-width 16/32-bit encoding for code density.
- **SVE / SVE2** — Scalable Vector Extension for HPC.
- **Neon** — SIMD instructions.
- Numerous architecture profiles (A, R, M) with different privilege models.

The result is a large, complex ISA. A complete ARM architecture reference manual runs thousands of pages. This complexity is manageable because Arm provides polished implementations, but it makes clean-room reimplementation difficult.

### RISC-V: Designed for Modularity

RISC-V was designed with hindsight. Its base ISA fits in a small document. Instruction encodings are regular and easy to decode:

```
R-type: funct7 | rs2 | rs1 | funct3 | rd | opcode
I-type: imm[11:0] | rs1 | funct3 | rd | opcode
S-type: imm[11:5] | rs2 | rs1 | funct3 | imm[4:0] | opcode
```

The regularity makes hardware decoder design straightforward and formal verification tractable.

## Ecosystem Comparison

ARM's ecosystem advantage is real but narrowing:

- **ARM toolchain:** GCC, LLVM, IAR, Keil, Arm Compiler. Decades of optimization.
- **RISC-V toolchain:** GCC, LLVM (both with excellent support). QEMU, Spike simulator. OpenOCD debugger.

For embedded use, ARM's **Mbed OS** and **CMSIS** libraries are more mature. For Linux-based systems, RISC-V parity is essentially complete — the Linux kernel, glibc, systemd, and most major software stacks run on RISC-V.

## Where ARM Still Leads

- **Performance-per-watt** at the high end: Apple M-series chips are ARM and unmatched.
- **Ecosystem breadth:** Decades of ARM-specific optimizations in firmware, RTOS, and middleware.
- **Vendor support:** Hundreds of ARM Cortex-M devices from STMicroelectronics, NXP, Nordic, etc.

## Where RISC-V Wins

- **No licensing cost:** Critical for startups, academia, and sovereign chip programs.
- **Custom extensions:** RISC-V explicitly permits and supports them; ARM architecture licenses are needed to add custom instructions.
- **Geopolitical neutrality:** Swiss governance reduces export control risk.
- **Education:** The clean ISA design is superior for teaching.

## A Concrete Scenario

A company building a dedicated AI inference chip for smart cameras:

```
ARM approach:
  - License Cortex-M55 + Arm Ethos NPU IP
  - Pay upfront + royalties per shipped unit
  - Custom acceleration constrained by ARM's terms
  - Fast time-to-market with mature tools

RISC-V approach:
  - Implement RV32IMAC + custom Xai_accel extension
  - Zero licensing cost
  - Full control over custom instruction encoding
  - Slightly longer time-to-market for toolchain bring-up
```

Neither answer is universally correct. The right choice depends on budget, timeline, required customization, and strategic IP considerations.

## Common Pitfalls

- **Pitfall:** Assuming RISC-V performance is inferior to ARM. Performance depends on microarchitecture, not ISA. A well-designed RISC-V core competes with comparable ARM cores.
- **Pitfall:** Treating ARM as monolithic. ARM has multiple architecture profiles and versions; "ARM" is as broad a category as "RISC-V."
- **Pitfall:** Ignoring total cost of ownership. ARM licensing is a known cost; RISC-V's cost shows up in engineering time for toolchain bring-up and ecosystem development.

RISC-V and ARM will coexist for the foreseeable future. Understanding their trade-offs positions you to make informed architectural decisions.
