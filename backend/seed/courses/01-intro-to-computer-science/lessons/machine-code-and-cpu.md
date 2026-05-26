# Machine Code and the CPU

Every program you run—whether written in Python, Java, or C++—ultimately reaches the CPU as a stream of **machine code**: raw binary numbers that the processor is wired to understand. This lesson digs deep into what machine code is, how the CPU executes it, and how a running program is organised in memory.

## What Is Machine Code?

Machine code is a sequence of **instructions** encoded as fixed-width binary numbers. Each instruction tells the CPU to perform one specific, primitive operation:

- Move a number from memory into a register
- Add two registers together
- Compare two values
- Jump to a different instruction if a condition is met
- Load or store data to/from memory

A typical modern instruction set (e.g., x86-64 or ARM64) defines hundreds of such instructions. Together they form the CPU's **Instruction Set Architecture (ISA)**—the contract between hardware and software.

### A Simplified Assembly Example

Assembly language is the human-readable representation of machine code—each assembly instruction corresponds to one machine instruction.

Suppose we want to compute `5 + 3` and store the result. In simplified assembly:

```asm
MOV  R1, 5        ; Load the value 5 into register R1
MOV  R2, 3        ; Load the value 3 into register R2
ADD  R3, R1, R2   ; R3 = R1 + R2 = 8
STR  R3, 0x1000   ; Store R3's value at memory address 0x1000
```

In actual machine code, each of those lines becomes a fixed-width binary number like:
`0000 0001 0001 0101 0000 0011 1000 0010`

The CPU does not understand `MOV` or `ADD`—it just reads the binary encoding and decodes it into control signals for its internal hardware.

### Real x86-64 Example

The instruction `MOV RAX, 42` (load 42 into the 64-bit register named RAX) encodes as 10 bytes on x86-64:
`48 B8 2A 00 00 00 00 00 00 00`

Breaking this down: `48 B8` is the opcode for "MOV RAX, 64-bit immediate value"; `2A 00 00 00 00 00 00 00` is 42 in little-endian 64-bit format.

Programmers almost never write raw bytes like this—that is the assembler's job. But every instruction in every high-level language ultimately arrives at the CPU as bytes just like these.

## Registers

**Registers** are tiny, ultra-fast storage locations *inside* the CPU die. They hold the values the CPU is currently working with.

A 64-bit x86-64 CPU has 16 general-purpose 64-bit registers (RAX, RBX, RCX, RDX, RSP, RBP, RSI, RDI, R8–R15), plus special-purpose registers for the instruction pointer, flags, floating-point, SIMD, etc.

### Memory Hierarchy Speed Comparison

| Level | Access time | Size (typical) | Technology |
|-------|------------|----------------|-----------|
| Registers | ~0.3 ns (1 cycle at 3 GHz) | 32 × 64-bit = 256 bytes | Flip-flops on CPU die |
| L1 cache | ~1 ns (3–4 cycles) | 32–64 KB per core | SRAM on CPU die |
| L2 cache | ~4 ns (12 cycles) | 256 KB–1 MB per core | SRAM on CPU die |
| L3 cache | ~10 ns (30 cycles) | 4–64 MB shared | SRAM on CPU die |
| RAM (DRAM) | ~100 ns (300 cycles) | 8–64 GB | DRAM chips on motherboard |
| NVMe SSD | ~50 µs (150,000 cycles) | 256 GB–4 TB | Flash memory |

This enormous speed difference means the CPU spends a lot of its time waiting for data. CPUs use **speculative execution** and **out-of-order execution** to keep busy while waiting for slow memory.

## The Fetch-Execute Cycle

The CPU endlessly repeats the **fetch-execute cycle** (also called the instruction cycle) at its clock rate:

```
┌─────────────────────────────────────────────────────────────┐
│  1. FETCH    Read the instruction at the address stored      │
│             in the Program Counter (PC) from memory.        │
│             Increment PC to point to the next instruction.  │
│                         ↓                                   │
│  2. DECODE   The control unit decodes the binary encoding    │
│             to determine: which operation? which operands?  │
│                         ↓                                   │
│  3. FETCH OPERANDS   Load any values from registers or RAM  │
│             needed for the instruction.                     │
│                         ↓                                   │
│  4. EXECUTE  The ALU (or other functional unit) performs    │
│             the operation (add, compare, branch, etc.)      │
│                         ↓                                   │
│  5. WRITE BACK   Store the result in a register or memory.  │
│                         ↓                                   │
│              ← repeat forever (until HALT or power-off) ─── │
└─────────────────────────────────────────────────────────────┘
```

A modern 3 GHz CPU completes about **3 billion of these cycles per second**. With pipelining and multiple execution units, it can start a new instruction every cycle (or even multiple per cycle).

## The Program Counter and Branches

The **Program Counter (PC)** — also called the Instruction Pointer (IP) on x86 — is a special register that always holds the memory address of the *next* instruction to fetch.

Normally the PC advances by the size of each instruction (4 bytes on ARM, variable 1–15 bytes on x86-64). A **branch instruction** (jump, call, return) changes the PC to a different address, causing the CPU to continue execution from that new location. This is how `if` statements and loops are implemented in machine code.

**Example of branching in assembly:**

```asm
CMP  R1, 0        ; Compare R1 with 0; set condition flags
BEQ  .loop_end    ; Branch to .loop_end if equal (zero flag set)
SUB  R1, R1, 1    ; R1 = R1 - 1
B    .loop_start  ; Branch back to start (unconditional)
.loop_end:
```

This is exactly what a `while x != 0: x -= 1` Python loop becomes in machine code.

### Branch Prediction

Modern CPUs try to **predict** which branch will be taken before they know for sure, speculatively executing instructions down the predicted path. If the prediction is wrong (a branch misprediction), the CPU must discard the speculative work and restart—wasting 15–20 cycles. This is why sorting data before processing it is sometimes faster: sorted data has more predictable branch patterns.

## Memory Layout of a Running Program

When the operating system loads a program into RAM, it organises the address space into distinct regions:

```
High addresses
┌────────────────────┐
│      Stack         │  Local variables, function call frames.
│          ↓         │  Each function call pushes a "frame"; returning pops it.
│      (grows down)  │  Stack overflow occurs if recursion goes too deep.
├────────────────────┤
│       ↕ gap ↕      │  (Unmapped; accessing it causes a segfault)
├────────────────────┤
│       Heap         │  Objects created with `new` (C++) or allocated dynamically.
│          ↑         │  Python objects live here. Grows upward.
│      (grows up)    │  Memory leaks = heap that grows without being freed.
├────────────────────┤
│       BSS          │  Uninitialised global/static variables (zero-filled)
├────────────────────┤
│       Data         │  Initialised global and static variables
├────────────────────┤
│       Text         │  Machine code instructions (read-only, shared)
└────────────────────┘
Low addresses
```

This layout is why:
- **Stack overflow** occurs with deep recursion—the stack grows down and eventually collides with the heap.
- **Null pointer dereferences** crash the program—address 0 is unmapped, and reading/writing it triggers an OS signal (SIGSEGV on Linux).
- **Buffer overflows** are dangerous—writing past the end of a stack buffer can overwrite the return address, hijacking control flow. This is the basis for entire classes of security vulnerabilities.

## From Python to Machine Code

How does `print("hello")` become machine code?

```
Python source code  (.py)
       ↓  CPython compiler (runs once, produces .pyc)
   CPython bytecode  (.pyc)  — a simplified instruction set for the Python VM
       ↓  CPython interpreter (implemented in C)
   C machine code  (the cpython binary on your disk)
       ↓  CPU
   Logic gate operations on transistors
```

Python adds **two translation layers** compared to a compiled language like C:
1. Python → bytecode
2. Bytecode → machine code (the interpreter itself)

This is why Python is typically 10–100× slower than equivalent C code for CPU-intensive tasks. The trade-off: portability (the same .py runs anywhere Python is installed), safety (no buffer overflows, automatic memory management), and development speed.

## Common Misconceptions

**"Faster clock speed always means faster programs."**
Clock speed (GHz) determines how many cycles per second, but a cycle may do little work if the CPU is stalled waiting for cache misses. More GHz with many cache misses can be slower than slightly fewer GHz with great cache performance. Memory access patterns matter enormously.

**"Assembly language and machine code are the same."**
Assembly is a human-readable text format where each mnemonic (`MOV`, `ADD`) represents one machine instruction. Machine code is the binary encoding of those instructions. An *assembler* converts assembly to machine code. They represent the same instructions, but in different forms.

**"Python programs are not converted to machine code—they just 'interpret' the source."**
Python source is compiled to bytecode first (you can see `.pyc` files in `__pycache__`). The CPython interpreter then executes that bytecode. The *interpreter itself* (cpython binary) is compiled machine code that runs the bytecode. So machine code is always involved—it is the interpreter's machine code, not your Python code's machine code.

## Key Takeaways

- **Machine code** is the set of binary-encoded instructions a CPU natively understands; assembly is the human-readable form.
- **Registers** are the fastest, smallest storage directly inside the CPU; RAM is 300× slower.
- The **fetch-execute cycle** is the fundamental loop: fetch, decode, execute, write-back—billions of times per second.
- The **Program Counter** tracks which instruction runs next; branch instructions change it to implement `if` and loops.
- A running program's memory is divided into text (code), data, heap, and stack—confusing these regions causes crashes and security bugs.
- Python runs through two layers of translation before reaching the CPU; this flexibility costs execution speed.
