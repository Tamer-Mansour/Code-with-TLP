# ABI Register Names: ra, sp, gp, tp, a0-a7

The RISC-V Application Binary Interface (ABI) gives each hardware register a human-readable name and a defined role. These names are a **software contract** — the hardware sees only x0–x31, but every compiler, linker, and operating system agrees on what each register is used for, enabling separately compiled code to interoperate.

## The Full ABI Name Table

| x# | ABI Name | Role | Preserved across calls? |
|----|----------|------|-------------------------|
| x0 | zero | Hardwired 0 | N/A |
| x1 | ra | Return address | No (caller-saved) |
| x2 | sp | Stack pointer | Yes (callee-saved) |
| x3 | gp | Global pointer | — (special) |
| x4 | tp | Thread pointer | — (special) |
| x5 | t0 | Temporary | No |
| x6 | t1 | Temporary | No |
| x7 | t2 | Temporary | No |
| x8 | s0 / fp | Saved reg / frame ptr | Yes |
| x9 | s1 | Saved register | Yes |
| x10 | a0 | Argument 0 / return value 0 | No |
| x11 | a1 | Argument 1 / return value 1 | No |
| x12 | a2 | Argument 2 | No |
| x13 | a3 | Argument 3 | No |
| x14 | a4 | Argument 4 | No |
| x15 | a5 | Argument 5 | No |
| x16 | a6 | Argument 6 | No |
| x17 | a7 | Argument 7 / syscall number | No |
| x18–x27 | s2–s11 | Saved registers | Yes |
| x28 | t3 | Temporary | No |
| x29 | t4 | Temporary | No |
| x30 | t5 | Temporary | No |
| x31 | t6 | Temporary | No |

## Key Registers Explained

### ra — Return Address (x1)

When `jal ra, func` is executed, the processor stores `PC + 4` (the instruction after the call) into `ra`. The callee returns with `ret` (pseudo for `jalr x0, ra, 0`). Because `ra` is caller-saved, a function that itself calls another function **must** save `ra` on the stack first.

### sp — Stack Pointer (x2)

Points to the top (lowest address) of the current stack frame. The stack grows downward. `sp` must be 16-byte aligned at function entry per the ABI. It is callee-saved: a function must restore `sp` to its original value before returning.

```asm
addi sp, sp, -16    # allocate 16 bytes on stack
sw   ra, 12(sp)     # save return address
...
lw   ra, 12(sp)     # restore return address
addi sp, sp, 16     # deallocate frame
ret
```

### gp — Global Pointer (x3)

Holds a base address near the middle of the `.data`/`.bss` section. The linker sets it so that global variables can be accessed with a single `lw x5, offset(gp)` instruction (12-bit signed offset = ±2 KiB reach). **Do not modify gp after startup.** The linker relaxation pass rewrites absolute loads into gp-relative loads automatically.

### tp — Thread Pointer (x4)

Points to the thread-local storage (TLS) block for the current hardware thread. The OS sets `tp` when scheduling a thread and the C runtime uses it for `__thread` / `thread_local` variables. User code should not modify `tp`.

### a0–a7 — Arguments and Return Values (x10–x17)

- The first eight integer arguments to a function are passed in `a0`–`a7`.
- Return values go in `a0` (and `a1` for a 128-bit result).
- Arguments beyond eight are passed on the stack.
- All eight are caller-saved — the callee may freely overwrite them.

```c
// C signature
long add(long a, long b);
// Maps to: a=a0, b=a1, return value in a0
```

```asm
add  a0, a0, a1    # result = a + b, returned in a0
ret
```

### a7 — System Call Number

In Linux on RISC-V, `a7` holds the syscall number. Arguments go in `a0`–`a5`. This is a special secondary role alongside its normal argument role.

```asm
li   a7, 93        # syscall: exit
li   a0, 0         # exit code 0
ecall
```

## Common Pitfalls

- **Forgetting that `ra` is caller-saved.** Any non-leaf function that calls another function will overwrite `ra`. Save it on the stack at function entry.
- **Trusting `gp` in hand-written assembly.** Its value depends on the linker script; without the linker's cooperation, gp-relative loads produce garbage.
- **Passing the 9th argument in a register.** Only 8 integer arguments go in registers; the rest live on the stack, pushed right-to-left before the call.

> **Interview answer:** The RISC-V ABI maps x0–x31 to human-readable roles: `ra` holds the return address, `sp` the stack pointer, `gp` the global pointer, `tp` the thread pointer, and `a0`–`a7` the first eight function arguments (with `a0`/`a1` also carrying return values). These conventions are enforced by software, not hardware.
