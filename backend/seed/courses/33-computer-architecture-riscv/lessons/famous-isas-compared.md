# Case Studies: x86, ARM, MIPS, RISC-V

The RISC vs CISC debate is best understood through the lens of real ISAs. x86, ARM, MIPS, and RISC-V represent four distinct points in the design space, each shaped by different constraints, goals, and eras. Knowing their histories and trade-offs is essential for any systems engineer.

## x86: The CISC Survivor

**Origin:** Intel 8086, 1978. Extended continuously to 8086 → 286 → 386 (32-bit) → x86-64 (AMD64, 64-bit, 2003).

**Philosophy:** CISC. Variable-length instructions (1-15 bytes), rich addressing modes, implicit operands, microcode for complex instructions.

**Key facts:**
- Dominant ISA on desktops, laptops, and servers.
- Backward-compatible with software from 1978.
- Modern implementations (Intel Core, AMD Zen) translate to RISC micro-ops internally.
- 3,000+ documented instructions in the full x86-64 ISA.

```asm
; x86-64: complex addressing in one instruction
movq  %rax, -8(%rbp, %rcx, 8)   ; [rbp + rcx*8 - 8] = rax
```

**Strengths:** Ecosystem maturity, software compatibility, competitive performance through micro-op translation.
**Weaknesses:** Power-hungry front-end, complex verification, limited registers in 32-bit mode.

## ARM: The RISC Pragmatist

**Origin:** Acorn RISC Machine (later Advanced RISC Machines), 1985. Evolved through ARMv4 (ARM7TDMI, GameBoy Advance) → ARMv7 (Cortex-A series) → ARMv8 (64-bit AArch64, 2011) → ARMv9 (2021).

**Philosophy:** RISC, with pragmatic complexity added over time (NEON SIMD, SVE, Thumb-2 mixed-width encoding, pointer authentication).

**Key facts:**
- Dominant ISA in mobile (every smartphone), embedded, and increasingly in servers (AWS Graviton, Ampere Altra).
- Apple M-series chips (ARM) outperform x86 on performance-per-watt benchmarks.
- AArch64 has 31 general-purpose 64-bit registers (x0-x30).
- Licensed architecture — ARM Holdings licenses the ISA and processor designs.

```asm
; AArch64 (ARM64): clean, fixed 32-bit instructions
ldr  x0, [x1, x2, lsl #3]   ; load from x1 + x2*8
add  x3, x0, x4             ; x3 = x0 + x4
```

**Strengths:** Power efficiency, large register file, strong ecosystem, Apple Silicon dominance.
**Weaknesses:** Commercial licensing fees, ISA complexity has grown significantly, fragmented 32-bit ecosystem.

## MIPS: The Textbook RISC

**Origin:** MIPS (Microprocessor without Interlocked Pipeline Stages), Stanford, John Hennessy, 1981. Commercial chips from 1985.

**Philosophy:** Pure RISC. Fixed 32-bit instructions, 32 registers, load-store model, originally no interlocks (the programmer/compiler was responsible for filling branch delay slots).

**Key facts:**
- Historically dominant in embedded and networking (routers, game consoles: PlayStation 1/2, N64).
- Standard teaching ISA — Patterson & Hennessy's "Computer Organization and Design" uses MIPS.
- The architecture that proved RISC worked commercially.
- Market position has declined sharply; MIPS Technologies was acquired and went through multiple ownership changes.

```asm
# MIPS: branch delay slot — the instruction after a branch always executes
beq  $t0, $t1, target   # branch if t0 == t1
nop                      # this instruction executes regardless (delay slot)
# execution jumps to target here
```

The branch delay slot is a direct artifact of RISC's pipeline philosophy: the branch result is not known until late in the pipeline, so the next instruction is always fetched and executed. Modern ISAs (RISC-V, ARM) eliminate delay slots, relying on the compiler or branch predictor instead.

**Strengths:** Clean design, excellent teaching vehicle, simple pipeline.
**Weaknesses:** Commercial decline, delay slots are a compiler burden, no open implementation.

## RISC-V: The Open-Source RISC

**Origin:** UC Berkeley, Krste Asanovic and team, 2010. Ratified base ISA in 2019.

**Philosophy:** RISC, designed from scratch with modern knowledge, open and royalty-free.

**Key facts:**
- Modular ISA: a frozen base (RV32I, RV64I) plus standard extensions (M=multiply, A=atomic, F=float, D=double, C=compressed, V=vector).
- No delay slots, no implicit registers, no complex addressing modes in the base ISA.
- 32 general-purpose registers (x0 always reads zero — a clever simplification).
- Royalty-free: anyone can implement it without paying license fees.
- Growing adoption: SiFive, Western Digital, ESP32-C3/C6, NVIDIA GPU microcontrollers.

```asm
# RISC-V: clean, orthogonal instruction set
# x0 is hardwired to zero — used for no-ops, unconditional branches, discarding results
add  x0, x0, x0       # NOP (writes to x0, which is discarded)
jal  x0, label        # unconditional jump (return address discarded)
mv   x1, x2           # pseudo-instruction: addi x1, x2, 0
```

**Strengths:** Open, royalty-free, clean modern design, modular extensions, growing ecosystem.
**Weaknesses:** Younger ecosystem than x86/ARM, fewer mature commercial implementations for highest-performance workloads.

## ISA Comparison Table

| Property | x86-64 | AArch64 | MIPS32 | RV64GC |
|---|---|---|---|---|
| Type | CISC | RISC | RISC | RISC |
| Instruction width | 1-15 bytes | 32 bits | 32 bits | 16/32 bits |
| GP registers | 16 | 31 | 32 | 32 |
| Load-store only | No | Yes | Yes | Yes |
| License | Intel/AMD | ARM Ltd | MIPS/Wave | Open (BSD) |
| Primary domain | Desktop/Server | Mobile/Server | Embedded (legacy) | Embedded/Research |
| Memory model | TSO (strong) | Weak + barriers | Weak + barriers | Weak + FENCE |

## A Common Interview Question

*"Why does ARM dominate mobile but x86 dominates the server market?"*

ARM's simpler front-end and energy-efficient pipeline excel at battery-powered, thermally constrained mobile devices. x86's decades of software investment, JIT compilers tuned for it, and high single-threaded performance (aided by high clock frequencies and large caches) suit server workloads. The gap is closing — AWS Graviton4 (ARM) competes with x86 on server benchmarks — but the installed software base gives x86 inertia.

**Interview answer:** x86 is CISC with variable-length instructions used on servers/desktops; ARM is RISC with fixed 32-bit instructions dominant in mobile and increasingly servers; MIPS is the classical textbook RISC now in decline; RISC-V is a modern open RISC ISA gaining traction in embedded and custom silicon — all reflect different trade-offs between complexity, performance, power, and ecosystem investment.
