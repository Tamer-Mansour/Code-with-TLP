# The ISA as the Hardware-Software Contract

The ISA is a **bilateral contract**. Hardware vendors promise that any conforming chip will execute every specified instruction with the documented semantics. Software vendors (compilers, OS kernels, hypervisors) promise they will only rely on those documented behaviors—never on undocumented side-effects of a particular chip revision.

This contract is what makes binary compatibility possible and what allows Moore's Law to benefit users without forcing them to recompile software for each new chip generation.

## The Two Sides of the Contract

### Hardware's Obligations

A processor that implements ISA X must:

- Execute every mandatory instruction and produce the exact result the spec defines.
- Raise the correct exceptions (e.g., illegal instruction, misaligned access, page fault) when the spec says to.
- Expose exactly the registers the spec defines, with the specified reset states.
- Obey the memory consistency model — e.g., if the spec says a `FENCE` instruction drains the store buffer, the hardware must do so.

The hardware is free to optimize *how* it reaches the correct result — out-of-order execution, branch prediction, speculative loads — as long as the observable behavior matches the spec.

### Software's Obligations

A conforming program or OS must:

- Only use instructions defined in the ISA (and extensions it has verified are present).
- Not rely on undefined behavior (e.g., the result of shifting by more than the register width).
- Honor alignment rules: unaligned 64-bit loads are undefined on RISC-V base ISA.
- Use the prescribed mechanism to detect optional feature support (e.g., x86 `CPUID`, RISC-V `misa` CSR).

> **Interview answer:** "The ISA lets hardware teams redesign every transistor for each new process node without breaking old software, as long as the observable machine behavior stays the same."

## Abstraction Layers Enabled by the Contract

```
+-------------------------------+
|  Application code (C, Rust)   |
+-------------------------------+
|  Compiler / standard library  |  relies on ISA calling convention
+-------------------------------+
|  Operating system kernel      |  relies on ISA privilege model
+-------------------------------+
|  ISA  (the contract)          |  <--- stable boundary
+-------------------------------+
|  Microarchitecture            |  changes every 2-3 years
+-------------------------------+
|  Process node (CMOS, FinFET)  |
+-------------------------------+
```

The OS kernel programs directly to the ISA: it uses privileged instructions (`mret`, `sret`, `ecall` in RISC-V) and manages page tables whose format is also defined by the ISA's virtual-memory extension.

## Binary Compatibility Over Time

The most famous example of the ISA contract in action is **x86 backward compatibility**. A DOS `.COM` binary from 1981 can still execute on a 2024 Intel Core processor because Intel has honored the x86 ISA contract for over 40 years—adding new instructions and modes without removing old semantics.

RISC-V takes a different philosophy: the base ISA is frozen (no instruction will ever be removed or changed in meaning), and new capabilities are added only through versioned, opt-in extensions.

```
RISC-V extension bits in misa CSR:
  bit 12 (M) = multiply/divide
  bit  0 (A) = atomics
  bit  5 (F) = single-precision float
  bit  3 (D) = double-precision float
  bit  2 (C) = compressed 16-bit instructions
```

## What Breaks the Contract

Common pitfalls that violate the contract from the software side:

- **Relying on microarchitectural timing** (e.g., counting cycles to detect cache hits) — the spec says nothing about latency.
- **Executing undefined opcodes** — a future chip might handle them differently.
- **Assuming word-tearing atomicity** that the memory model does not guarantee — leads to data races on weakly-ordered ISAs like RISC-V and ARM.
- **Using hardware-specific MSRs/CSRs** not in the base spec — breaks portability across vendors.

## Practical Impact on System Design

| Layer | Benefit from ISA contract |
|---|---|
| Compiler | Can generate code once, run on any conforming chip |
| Hypervisor | Can trap/emulate ISA instructions to run guest VMs |
| Emulator (QEMU) | Precisely simulate the ISA to run ARM binaries on x86 |
| OS | Port to a new CPU by porting to its ISA, not its transistors |
