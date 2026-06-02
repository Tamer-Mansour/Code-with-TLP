# Register, Memory, and Stack Machines

Beyond operand count, ISAs differ in **where operands live** during computation. The three classical machine models are register machines, memory machines, and stack machines. Real ISAs are hybrids, but understanding the pure models clarifies design trade-offs.

## The Fundamental Question

Every ALU instruction must fetch its operands from somewhere. The ISA decides which storage locations are first-class citizens that instructions can reference directly:

| Machine Model | Operand Sources | Result Destination |
|---|---|---|
| Register machine | Registers (fast) | Register |
| Memory machine | Registers or memory | Register or memory |
| Stack machine | Implicit stack | Stack top |

## Register Machine (Load-Store Architecture)

In a pure **register machine** (also called a load-store architecture), ALL computation operands must be in registers. Memory is accessed only through explicit load and store instructions.

```asm
# RISC-V: compute c = a + b  where a, b, c are in memory
lw   t0, 0(a0)    # load a into t0
lw   t1, 4(a0)    # load b into t1
add  t2, t0, t1   # compute a + b in registers
sw   t2, 8(a0)    # store result to c
```

Four instructions versus one conceptual step. However:

- Each instruction is simple and predictable (1 cycle each in a pipelined CPU).
- Register values can be forwarded directly to dependent instructions.
- Out-of-order execution is straightforward.

RISC-V, MIPS, ARM (AArch64), and SPARC are load-store architectures.

> **Interview answer:** "A load-store ISA separates memory access from computation. This makes pipelining easier and register allocation for the compiler more straightforward."

## Memory-to-Memory Architecture (Register-Memory or Mem-Mem)

A **register-memory** ISA (like x86) allows at least one operand of an arithmetic instruction to come directly from a memory address. True **memory-to-memory** ISAs (like the VAX) allow both operands to be memory references.

```asm
; x86: register-memory form
add  eax, [rbx+4]    ; eax = eax + Mem[rbx+4]  — one memory operand

; VAX: memory-to-memory form (historical)
ADDL2  A, B          ; B = B + A, where A and B can both be memory locations
```

Advantages:
- Denser code — fewer explicit load/store instructions.
- Familiar for programmers who think in terms of variables in memory.

Disadvantages:
- A single instruction has variable latency depending on whether a cache miss occurs.
- Much harder to pipeline: the pipeline cannot start the next instruction until it knows the memory-access latency of the current one.
- VAX-style mem-mem ISAs became obsolete precisely because they were too hard to make fast.

## Stack Machine

In a **stack machine**, all operands are implicitly on an evaluation stack. Instructions pop inputs and push results.

```
; Evaluate (3 + 4) * 2  on a stack machine
PUSH 3       # stack: [3]
PUSH 4       # stack: [3, 4]
ADD          # stack: [7]
PUSH 2       # stack: [7, 2]
MUL          # stack: [14]
POP result
```

Real-world stack machine examples:
- **JVM bytecode** — stack-based for portability and simplicity of the spec.
- **WebAssembly (Wasm)** — stack-based in its binary format.
- **x87 FPU** — the classic x86 floating-point unit used a stack of 8 80-bit registers (ST(0)–ST(7)).
- **Forth** — entire language built on a software stack machine model.

### x87 FPU Stack Example

```asm
; double result = a * b + c;
fldl  a        ; push a onto FPU stack — ST(0)=a
fldl  b        ; push b — ST(0)=b, ST(1)=a
fmulp          ; ST(1) = ST(1)*ST(0), pop — ST(0)=a*b
fldl  c        ; push c — ST(0)=c, ST(1)=a*b
faddp          ; ST(1) = ST(1)+ST(0), pop — ST(0)=a*b+c
fstpl result   ; pop result into memory
```

The x87 stack is why compiler writers hated it: register allocation on a stack requires careful bookkeeping of stack depth, and the `FXCH` instruction (swap top two stack elements) exists mainly to paper over this awkwardness.

## Hybrid Reality

Modern ISAs blend all three models:

| ISA | Scalar computation | SIMD/Float | Memory |
|---|---|---|---|
| RISC-V | Register (RV32I/64I) | Register (F/D/V ext) | Load-store only |
| x86-64 | Register-memory | Register (XMM/YMM/ZMM) | Register-memory |
| ARM64 | Register (load-store) | Register (NEON/SVE) | Load-store only |

## Why Register Machines Won

The shift from memory-rich to load-store architectures happened because:

1. **Compiler sophistication** — modern compilers are excellent at register allocation. The manual memory management advantage of mem-mem faded.
2. **Cache complexity** — a single instruction that touches memory is hard to pipeline when cache latency is variable (1–200 cycles depending on level).
3. **Out-of-order execution** — OoO engines need to know the latency of each micro-operation upfront; a merged load+compute instruction complicates this.
4. **Register renaming** — renaming 32 architectural registers to 200 physical registers (as Skylake does) is tractable; renaming all of memory is not.
