# Why RISC-V Is Popular for Virtual Prototypes

Virtual prototyping means building a software model of a chip before the silicon exists. The choice of instruction-set architecture (ISA) shapes every layer of that model. RISC-V has become the default ISA for new virtual prototypes, and understanding why helps you make better design decisions.

## RISC-V in One Sentence

RISC-V (pronounced "risk five") is a free, open-standard, modular ISA released by UC Berkeley in 2010. Unlike ARM or x86, no license fee is required, and the specification is a public document anyone can download, study, and implement.

## Key Reasons for Popularity in Virtual Prototyping

**Open specification, no NDA.**
The full ISA specification is a freely downloadable PDF. When you write a decoder, an interpreter, or a cycle-accurate pipeline model you can cross-reference every field of every instruction without signing a license agreement. This dramatically speeds up research and educational projects.

**Modular base + extension design.**
The base integer ISA (RV32I or RV64I) contains only 47 instructions. Optional standard extensions add:

| Extension | Adds |
|-----------|------|
| M | Integer multiply/divide |
| A | Atomic operations |
| F | Single-precision float |
| D | Double-precision float |
| C | Compressed (16-bit) instructions |
| V | Vector |

A VP only needs to implement the extensions present in the target SoC. Simulating an IoT microcontroller? Implement RV32I + M + C and stop. No dead-weight silicon to model.

**Clean, regular encoding.**
All base instructions are exactly 32 bits wide. The opcode always occupies bits [6:0], the destination register always occupies bits [11:7], and the two source registers always occupy bits [19:15] and [24:20]. This regularity means a decode function is a handful of bit-mask operations, not a giant lookup table with exceptions.

**Exploding toolchain and ecosystem.**
GCC, Clang/LLVM, Binutils, QEMU, Spike (the official ISA simulator), and Linux all support RISC-V. You can compile a real Linux kernel, boot it on your VP, and run unmodified applications — a critical requirement for software-hardware co-design.

**Academic and industry momentum.**
Western Digital, SiFive, Google, and dozens of others have shipped or are developing RISC-V silicon. Universities standardize on RISC-V for computer-architecture courses. This means trained engineers and documented implementations are easy to find.

## Comparison with Alternatives

| ISA | Open spec? | Modular? | Common in VPs? |
|-----|-----------|---------|----------------|
| x86-64 | No | No | Legacy only |
| ARMv8 | Licensed | Somewhat | Commercial tools |
| RISC-V | Yes, free | Yes | Growing fast |
| MIPS | Limited | No | Declining |

## How This Maps to Virtual Prototyping

In a SystemC/TLM virtual prototype the CPU is modeled as a `sc_module` that:

1. Fetches a 32-bit word via a TLM initiator socket.
2. **Decodes** it — the topic of this module.
3. Executes the operation on a 32-register file.
4. Writes results back and updates the program counter.

RISC-V's regular encoding means step 2 is a series of cheap bit extractions — ideal for a fast functional model running millions of instructions per second.

```cpp
// Minimal opcode extraction — works for every RISC-V instruction
uint32_t opcode = instr & 0x7F;         // bits [6:0]
uint32_t rd     = (instr >> 7)  & 0x1F; // bits [11:7]
uint32_t funct3 = (instr >> 12) & 0x07; // bits [14:12]
uint32_t rs1    = (instr >> 15) & 0x1F; // bits [19:15]
uint32_t rs2    = (instr >> 20) & 0x1F; // bits [24:20]
uint32_t funct7 = (instr >> 25) & 0x7F; // bits [31:25]
```

> **Interview answer:** "RISC-V is popular for virtual prototypes because it is a free, open, modular ISA with a clean regular encoding — making decode logic simple — and a mature toolchain that lets you boot real software on your model."

## Common Pitfall

Do not confuse the base ISA with the full profile. When someone says "RISC-V" they often mean RV64GC (G = IMAFD, C = compressed). Your VP must declare exactly which extensions it supports, or applications compiled for missing extensions will execute illegal-instruction traps.
