# General-Purpose vs Special-Purpose Registers

Not all registers are created equal. Some hold arbitrary programmer data (general-purpose); others have a fixed, hardware-defined role (special-purpose). Knowing the difference is essential for writing correct assembly and understanding how the CPU works at the hardware level.

## General-Purpose Registers (GPRs)

GPRs can, in principle, hold any integer value — an address, a counter, a boolean flag, a pointer. The ISA does not dictate what data goes in them; that is the programmer's (or compiler's) choice.

RISC-V has 32 integer GPRs: **x0–x31**. By convention (the ABI), each register has a name and a calling-convention role:

| Register | ABI Name | Role |
|---|---|---|
| x0 | zero | Hardwired 0 — always reads 0, writes discarded |
| x1 | ra | Return address |
| x2 | sp | Stack pointer |
| x3 | gp | Global pointer |
| x4 | tp | Thread pointer |
| x5–x7 | t0–t2 | Temporary (caller-saved) |
| x8 | s0/fp | Saved register / frame pointer |
| x9 | s1 | Saved register (callee-saved) |
| x10–x11 | a0–a1 | Function args / return values |
| x12–x17 | a2–a7 | Function arguments |
| x18–x27 | s2–s11 | Saved registers (callee-saved) |
| x28–x31 | t3–t6 | Temporaries (caller-saved) |

Even though hardware does not enforce these roles, violating them breaks inter-operability with libraries and the OS.

## Special-Purpose Registers (SPRs)

Special-purpose registers are wired into specific CPU logic. You cannot re-purpose them; the hardware reads or writes them automatically during specific operations.

### Program Counter (PC)

Holds the address of the currently executing instruction. Automatically incremented by 4 each cycle (for 32-bit RISC-V). Modified by branch/jump instructions. Programmers cannot write the PC directly with a normal `add` — you must use `jal`, `jalr`, or `auipc`.

### Control and Status Registers (CSRs) in RISC-V

RISC-V defines a 12-bit CSR address space (4096 possible CSRs) accessed via special instructions (`csrrw`, `csrrs`, `csrrc`). Key CSRs:

| CSR | Name | Purpose |
|---|---|---|
| 0xF11 | mvendorid | Vendor ID (read-only) |
| 0x300 | mstatus | Machine status (interrupt enable, privilege bits) |
| 0x304 | mie | Machine interrupt enable |
| 0x305 | mtvec | Trap/interrupt vector base address |
| 0x341 | mepc | Exception Program Counter (return address after trap) |
| 0x342 | mcause | Cause of the most recent trap |
| 0xC00 | cycle | Cycle counter (user-mode readable) |
| 0xC02 | instret | Instructions-retired counter |

### Floating-Point Registers

RISC-V's F/D extensions add 32 floating-point registers (**f0–f31**) and a dedicated **fcsr** (floating-point control/status register) holding rounding mode and exception flags. These are entirely separate from the integer register file.

## Caller-Saved vs Callee-Saved: Why It Matters

```asm
# Caller must save t0 if it needs it after the call
call  some_function     # t0 may be clobbered
# t0 is undefined here unless caller saved it

# Callee must preserve s0 if it uses it
some_function:
    addi  sp, sp, -8
    sd    s0, 0(sp)    # save s0
    # ... use s0 freely ...
    ld    s0, 0(sp)    # restore s0
    addi  sp, sp, 8
    ret
```

Failing to honor these conventions corrupts the caller's state — a common source of hard-to-debug bugs in hand-written assembly.

## x86 Comparison (for context)

x86-64 has 16 GPRs (rax, rbx, rcx, rdx, rsi, rdi, rbp, rsp, r8–r15) plus many special registers: `rip` (instruction pointer), `rflags` (condition codes), segment registers (cs, ds, ss, etc.), and dozens of model-specific registers (MSRs) accessible only via `rdmsr`/`wrmsr` in kernel mode.

The RISC-V CSR design is cleaner: every privileged register is accessed through a single, uniform mechanism rather than scattered special instructions.

## Common Pitfalls

- **Assuming x0 can be written.** Writing to x0 always silently discards the value. `addi x0, x1, 0` is a no-op — used intentionally as a NOP alternative in RISC-V.
- **Mixing up `ra` after nested calls.** If a function calls another function without saving `ra` first, the return address is overwritten and the outer function cannot return correctly.
- **Reading CSRs without the right privilege level.** Accessing machine-mode CSRs from user mode causes an illegal-instruction exception.

## Interview Answer

> "General-purpose registers hold arbitrary programmer data and are managed by software conventions (the ABI); special-purpose registers like the PC, stack pointer, or CSRs are wired into specific hardware logic and updated automatically by the CPU during defined operations."
