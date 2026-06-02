# Decoding RISC-V Names like RV64GC

When you read product datasheets, compiler flags, or academic papers about RISC-V, you encounter strings like `RV64GC`, `RV32IMAC`, or `RV64GCBZba`. These are not arbitrary labels — they encode precise, decodable information about a processor's capabilities. Learning to read them is a practical skill for any RISC-V engineer.

## The General Format

A RISC-V ISA string follows this structure:

```
RV<XLEN><extensions>
```

Where:
- `RV` — Fixed prefix; stands for RISC-V.
- `<XLEN>` — Register width: `32`, `64`, or `128`.
- `<extensions>` — An ordered sequence of letters (and Z-prefixed sub-extension names) listing all enabled extensions.

## Step-by-Step Decoding: RV64GC

```
RV  64  G   C
|   |   |   |
|   |   |   +--- Compressed instructions (16-bit encodings)
|   |   +------- G = I + M + A + F + D + Zicsr + Zifencei
|   +----------- 64-bit registers and address space
+--------------- RISC-V prefix
```

Expanding `G`:

```
I   = Base integer ISA (47 instructions)
M   = Integer multiply and divide
A   = Atomic operations (LR/SC, AMOs)
F   = Single-precision floating point (f0–f31)
D   = Double-precision floating point (uses same f0–f31)
Zicsr     = CSR read/write instructions
Zifencei  = Instruction-fetch fence
```

So `RV64GC` is a 64-bit processor with the full general-purpose baseline plus compressed instructions. This is the minimum target for a Linux-capable RISC-V chip.

> **Interview answer:** "In RV64GC, RV means RISC-V, 64 is the register width, G is a shorthand for I+M+A+F+D plus Zicsr and Zifencei, and C is the compressed instruction extension. Together they define a 64-bit general-purpose Linux-capable processor."

## More Examples

**RV32IMAC** — common in embedded microcontrollers:

```
RV  32  I  M  A  C
        |  |  |  |
        |  |  |  +-- Compressed instructions
        |  |  +----- Atomic operations
        |  +-------- Multiply/divide
        +----------- Base integer ISA (explicit, not using G shorthand)
```

Note that `G` includes `I`, so `RV64G` and `RV64IMAFD` (plus Zicsr, Zifencei) are equivalent. Using `G` is preferred for readability.

**RV64GCBZba** — a modern application processor with bit manipulation:

```
RV  64  G  C  B  Zba
              |  |
              |  +--- Address generation bit-manip sub-extension
              +------ Full Bit-manipulation extension (B = Zba+Zbb+Zbs)
```

**RV32E** — ultra-constrained embedded:

```
RV  32  E
        |
        +-- Embedded variant; only x0–x15 (16 registers instead of 32)
```

## Ordering Rules

The RISC-V specification defines a canonical ordering for the ISA string:

1. Single-letter extensions come first, in alphabetical order after the base.
2. Multi-letter Z-extensions follow, sorted alphabetically.
3. X-extensions (vendor-specific) come last.

Canonical example:

```
RV64IMAFDQCBVZicsr_Zifencei_Xvendor_accel
```

The underscore `_` is used as a separator between multi-letter extension names to avoid ambiguity:

```
Zba_Zbb_Zbc    -- Three Z-extensions separated by underscores
```

## Compiler Flags

The ISA string maps directly to compiler flags:

```bash
# GCC for RV64GC
riscv64-linux-gnu-gcc -march=rv64gc -mabi=lp64d

# GCC for RV32IMAC (bare-metal)
riscv64-unknown-elf-gcc -march=rv32imac -mabi=ilp32

# GCC for RV64GCBZba
riscv64-linux-gnu-gcc -march=rv64gc_zba -mabi=lp64d
```

The `-mabi` flag specifies the Application Binary Interface:

| ABI | Description |
|---|---|
| `ilp32` | 32-bit pointers, no FP in registers |
| `ilp32f` | 32-bit pointers, F-extension FP in registers |
| `ilp32d` | 32-bit pointers, D-extension FP in registers |
| `lp64` | 64-bit pointers, no FP in registers |
| `lp64f` | 64-bit pointers, F-extension FP in registers |
| `lp64d` | 64-bit pointers, D-extension FP in registers |

## Worked Example: Reading a Datasheet

You encounter a chip with this specification:

```
Processor: RV64GCV
Max frequency: 1.5 GHz
Cache: 32 KB L1I, 32 KB L1D, 512 KB L2
```

You can immediately decode:
- 64-bit registers and address space (runs Linux).
- Full integer + multiply + atomic + float (single and double).
- Compressed instructions (code size benefit).
- **V extension** — hardware vector unit (suitable for SIMD workloads, ML inference, media processing).

This tells you the chip can run standard Linux applications *and* benefits from vectorized code. You would compile with:

```bash
-march=rv64gcv -mabi=lp64d
```

## Common Pitfalls

- **Pitfall:** Writing `RV64GC` but meaning something different. `G` is a well-defined shorthand; do not use it loosely.
- **Pitfall:** Omitting Z-extensions from the compiler flag when the hardware supports them. If the chip has Zba and you compile without `-march=rv64gc_zba`, the compiler will not emit those instructions.
- **Pitfall:** Mixing RV32 and RV64 binaries. The ISA string is part of the ELF binary metadata; linking the wrong combination fails.
- **Pitfall:** Assuming `RV64I` implies `G`. `G` must be explicitly listed or the shorthand used; `I` alone means only the base integer ISA.

Reading RISC-V ISA strings fluently is a basic competency for RISC-V engineers. It appears in compiler flags, simulator arguments, hardware documentation, and technical discussions.
