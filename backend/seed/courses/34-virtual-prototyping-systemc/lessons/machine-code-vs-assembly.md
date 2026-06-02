# Machine Code vs Assembly Language

Every program a CPU runs is ultimately a sequence of binary numbers stored in memory. Understanding the distinction between machine code and assembly language is the first step toward building an accurate CPU model in SystemC.

## What Is Machine Code?

Machine code is the native binary encoding of instructions that a processor's hardware decodes and executes directly. Each instruction is a fixed-width or variable-width bit pattern where specific fields encode the operation, source registers, destination registers, and immediate values.

Example — a 32-bit RISC instruction word (little-endian hex):

```
0x00430293
```

Broken into fields (RISC-V RV32I `addi x5, x6, 4`):

| Bits [31:20] | Bits [19:15] | Bits [14:12] | Bits [11:7] | Bits [6:0] |
|---|---|---|---|---|
| 000000000100 | 00110 | 000 | 00101 | 0010011 |
| imm=4 | rs1=x6 | funct3=ADD | rd=x5 | opcode=OP-IMM |

The processor's decode stage reads these bit fields in hardware — there is no string parsing, no symbol lookup.

## What Is Assembly Language?

Assembly is a human-readable text representation of machine code, with a strict one-to-one (or near one-to-one) correspondence to machine instructions.

```asm
; RISC-V assembly — add immediate
addi x5, x6, 4      ; x5 = x6 + 4
lw   x7, 0(x5)      ; x7 = Memory[x5 + 0]
sw   x7, 8(x6)      ; Memory[x6 + 8] = x7
```

An **assembler** translates each mnemonic line into its binary encoding. A **disassembler** does the reverse — it reads machine code bytes and prints the mnemonic form.

## Key Differences at a Glance

| Property | Machine Code | Assembly |
|---|---|---|
| Format | Binary / hex bytes | Text mnemonics |
| Readable by | CPU hardware | Humans |
| Processed by | CPU decode stage | Assembler tool |
| Abstraction level | Zero | Minimal |
| Portability | Architecture-specific | Architecture-specific |

Both are architecture-specific. An x86 binary cannot run on an ARM core without translation.

## Why It Matters for CPU Modeling

When you build a CPU model in SystemC/TLM you replicate the decode stage in C++. Your model receives a 32-bit (or 64-bit) instruction word from a fetch buffer and must extract fields exactly as hardware does.

```cpp
// SystemC CPU model — minimal RISC-V decode sketch
uint32_t instr = fetch_from_memory(pc);
uint32_t opcode  = instr & 0x7F;          // bits [6:0]
uint32_t rd      = (instr >> 7)  & 0x1F;  // bits [11:7]
uint32_t funct3  = (instr >> 12) & 0x07;  // bits [14:12]
uint32_t rs1     = (instr >> 15) & 0x1F;  // bits [19:15]
int32_t  imm_i   = (int32_t)instr >> 20;  // bits [31:20], sign-extended
```

Getting these bit masks wrong is a classic source of functional bugs in RTL and simulation models alike.

## Common Pitfalls

- **Sign extension errors** — immediate fields are often sign-extended from a sub-word width. Forgetting the cast to `int32_t` before shifting produces incorrect values for negative immediates.
- **Endianness confusion** — machine code bytes may be stored little-endian in memory but shown big-endian in documentation. Always clarify byte order when loading instruction words.
- **Pseudo-instructions** — assembly mnemonics like `li`, `mv`, or `nop` in RISC-V expand to one or more real machine instructions. They exist only in the assembler, not in machine code.

## Interview Answer

> "Machine code is the raw binary encoding the CPU executes; assembly is its human-readable mnemonic form. An assembler translates assembly to machine code one instruction at a time, with no runtime overhead. A CPU model in SystemC must decode the machine code bit-fields, not the text."
