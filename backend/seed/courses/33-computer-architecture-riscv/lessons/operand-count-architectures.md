# Zero-, One-, Two-, and Three-Operand Architectures

The number of explicit operand fields in an instruction — its **operand count** — is one of the most visible dimensions of ISA design. It determines how much state the programmer must manage explicitly and how dense the resulting code is.

## Why Operand Count Matters

Every arithmetic instruction needs to express: *where are the inputs, where does the result go?* The ISA designer must decide how many of those locations are named explicitly in the instruction word and how many are implied by convention.

## Three-Operand Architecture

In a **three-operand** ISA, every instruction names two source registers and a distinct destination register:

```asm
# RISC-V (three-operand)
add  x3, x1, x2    # x3 = x1 + x2  — x1 and x2 are UNCHANGED
```

Advantages:
- Non-destructive: source operands survive.
- Easy to rename registers in an out-of-order pipeline.
- Compiler can keep more live values in registers simultaneously.

RISC-V, ARM (AArch64), MIPS, and most modern RISC ISAs are three-operand.

> **Interview answer:** "Three-operand instructions are non-destructive and map cleanly onto SSA form in compilers, making register allocation simpler."

## Two-Operand Architecture

In a **two-operand** ISA, one source register also serves as the destination. The instruction names two registers; the result overwrites one of them.

```asm
; x86 (two-operand)
add  eax, ebx    ; eax = eax + ebx  — ebx unchanged, eax overwritten
```

The programmer must `mov` a register to save its value before an operation overwrites it. x86-32/64 (without AVX) is the canonical two-operand ISA.

Disadvantages:
- Forces extra `mov` instructions to preserve values.
- Creates false dependencies: `add eax, ebx` depends on the old value of `eax`.
- Complicates out-of-order execution (hardware renames registers to remove false deps).

## One-Operand Architecture (Accumulator Machine)

An **accumulator architecture** has a single implied register — the **accumulator** — that holds one operand and receives the result. Only one explicit operand (a register or memory address) appears in the instruction.

```asm
; Classic 8-bit accumulator (like 6502 / early Intel 8080)
LDA  100    ; accumulator = Mem[100]
ADD  104    ; accumulator = accumulator + Mem[104]
STA  108    ; Mem[108] = accumulator
```

- Code density is high (small instructions).
- The accumulator is a constant bottleneck — no parallelism.
- Common in early 8-bit microprocessors (6502, Z80, 8080) and still found in embedded microcontrollers.

## Zero-Operand Architecture (Stack Machine)

A **stack machine** uses an implicit operand stack. Instructions pop their inputs from the stack and push their result back. No register names appear in arithmetic instructions.

```
; Stack machine pseudocode for: (a + b) * c
PUSH a      # stack: [a]
PUSH b      # stack: [a, b]
ADD         # pop a and b, push a+b    → stack: [a+b]
PUSH c      # stack: [a+b, c]
MUL         # pop a+b and c, push result → stack: [(a+b)*c]
```

The Java Virtual Machine (JVM) bytecode is a zero-operand stack machine:

```
iload_0    # push local 0
iload_1    # push local 1
iadd       # pop two, push sum
iload_2    # push local 2
imul       # pop two, push product
```

Advantages of stack machines:
- Very compact encoding (no register field needed).
- Simple interpreter implementation.

Disadvantages:
- Limited instruction-level parallelism (strict sequential stack usage).
- Poor fit for modern superscalar hardware.

## Comparison Table

| Architecture | Operands Named | Destination | Example ISA |
|---|---|---|---|
| Three-operand | src1, src2, dst | Separate register | RISC-V, ARM64, MIPS |
| Two-operand | src, dst (= src1) | Overwrites an input | x86-32/64 |
| One-operand | src | Implicit accumulator | 6502, 8080, early x86 |
| Zero-operand | none | Top of stack | JVM, Forth, x87 FPU |

## Note on x86 AVX

Starting with AVX (256-bit SIMD), x86 adopted a **three-operand** VEX encoding:

```asm
vaddps ymm0, ymm1, ymm2   ; ymm0 = ymm1 + ymm2 (non-destructive)
```

This shows ISAs can evolve: x86 added a three-operand variant for performance-critical SIMD code while keeping the two-operand encoding for legacy scalar instructions.

## Interview Pitfall

Students sometimes say "RISC-V has two operands because instructions are 32 bits." In fact, RISC-V R-type instructions have five fields including two source registers **and** a separate destination register — it is firmly three-operand. The 32-bit width limits the number of bits per field, but not the operand count.
