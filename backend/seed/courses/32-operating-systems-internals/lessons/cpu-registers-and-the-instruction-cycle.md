# The CPU, Registers, and Fetch-Decode-Execute Cycle

Understanding what the CPU actually does at a hardware level is the foundation for everything in operating systems — from context switching to interrupt handling. This lesson builds that mental model precisely.

## What Is a CPU?

A CPU (Central Processing Unit) is the chip that executes program instructions. At its core it is a state machine: it reads an instruction, updates its internal state (registers, flags), optionally reads or writes memory, and moves to the next instruction. Modern CPUs do this billions of times per second.

## Registers

Registers are the fastest storage in the entire system — small, fixed-size slots that live inside the CPU itself. Access takes a single clock cycle, unlike memory which may take hundreds.

Common register categories on x86-64:

| Register | Purpose |
|---|---|
| `RAX`, `RBX`, `RCX`, `RDX` | General-purpose: arithmetic, temp values |
| `RSP` | Stack pointer — top of the current stack |
| `RBP` | Base (frame) pointer — stack frame anchor |
| `RIP` | Instruction pointer — address of the *next* instruction |
| `RFLAGS` | Status flags: zero, carry, overflow, sign… |
| `CS`, `DS`, `SS`… | Segment registers (legacy / protected-mode role) |

The OS cares deeply about registers because when it switches between processes (a **context switch**), it must save every register of the outgoing process and restore those of the incoming one. Miss even one and the process resumes with corrupted state.

## The Fetch-Decode-Execute Cycle

Every CPU repeats this loop continuously:

```
while (power_on):
    instruction = memory[RIP]   // FETCH
    RIP += instruction_length   // advance before decode
    op, operands = decode(instruction)  // DECODE
    execute(op, operands)        // EXECUTE (may access memory, update flags)
```

**Fetch** — The CPU reads the bytes at the address stored in `RIP` (x86-64) or `PC` (generic term). This triggers a cache lookup and, on a miss, a RAM access.

**Decode** — The fetched bytes are parsed to determine the opcode (what operation) and operands (registers, immediate values, memory addresses).

**Execute** — The ALU (Arithmetic Logic Unit) or FPU carries out the operation. Results are written to a destination register or memory location, and the `RFLAGS` register is updated.

### A Concrete Example

```asm
; x86-64 AT&T syntax
mov  $5, %rax      ; load immediate 5 into RAX
mov  $3, %rbx      ; load immediate 3 into RBX
add  %rbx, %rax    ; RAX = RAX + RBX  => RAX = 8
```

After `add`, the Zero Flag (ZF) in `RFLAGS` is 0 (result is not zero), the Sign Flag (SF) is 0 (result is positive).

## Why This Matters for the OS

- **Interrupts** hijack `RIP` — the CPU jumps to an OS handler mid-cycle. The OS must preserve the interrupted program's `RIP` and `RFLAGS` on the kernel stack before handling the event.
- **Privilege rings** are enforced per instruction — some instructions (like `HLT` or `IN/OUT`) are only allowed when the CPU is in ring 0 (kernel mode). The OS controls ring transitions.
- **Pipeline stalls** caused by cache misses are why OS schedulers try to keep a process's data hot in cache — a context switch can cold-flush L1/L2.

## Common Pitfalls

- Assuming `RIP` points to the *current* instruction — it actually points to the **next** one (already incremented during fetch).
- Confusing registers with memory — registers have no address; you cannot take the address of `RAX`.
- Overlooking `RFLAGS` during context switch — flags must be saved too, not just the general-purpose registers.

> **Interview answer:** The fetch-decode-execute cycle is the three-step loop a CPU repeats continuously: fetch the instruction bytes from the address in the instruction pointer, decode the opcode and operands, then execute the operation — updating registers, memory, and status flags. The OS leverages this cycle for interrupts (redirecting RIP to a handler) and context switching (saving/restoring all register state).
