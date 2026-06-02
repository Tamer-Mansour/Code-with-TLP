# System Call vs Function Call

Understanding the difference between a system call and a regular function call is foundational to operating systems knowledge. Both look similar from a source-code perspective, but they operate at entirely different privilege levels.

## What is a Function Call?

A regular function call stays entirely in user space. When you call `strlen()` or `malloc()`, the CPU executes instructions within your process's own address space, at the same privilege level. The call-return mechanism is a simple `CALL`/`RET` pair on x86-64: the return address is pushed to the stack, control jumps to the function body, and on return control comes back to the caller.

- No privilege change occurs.
- The kernel is not involved.
- Cost: roughly 1-5 ns on modern hardware (just a branch + stack ops).

## What is a System Call?

A system call is a **controlled gate into the kernel**. User programs cannot read or write arbitrary hardware registers, access other processes' memory, or talk to devices directly. When they need such services (open a file, send bytes over a socket, allocate physical memory), they make a system call.

The key differences:

| Property | Function Call | System Call |
|---|---|---|
| Privilege level | User (Ring 3) | Kernel (Ring 0) |
| Address space switch | No | Yes (kernel maps) |
| Stack used | User stack | Kernel stack (per-thread) |
| Mechanism | `CALL` instruction | `syscall` / `int 0x80` |
| Cost | ~1-5 ns | ~100-1000 ns |
| Can block | Only with busy-wait | Yes (sleep, I/O wait) |
| Arguments | Registers / stack | Registers (ABI-defined) |

## Why the Privilege Boundary Matters

The CPU hardware enforces rings of privilege. User code runs in Ring 3 with a restricted instruction set. The kernel runs in Ring 0. An attempt by user code to execute a privileged instruction (e.g., `cli` to disable interrupts) causes a General Protection Fault — the CPU rejects it.

System calls provide a **safe, audited crossing point**. The kernel validates every argument before acting. This is why buffer overflows in user space cannot directly corrupt kernel memory — the address spaces are separate.

```c
// This is a function call — no kernel involvement
size_t n = strlen(buf);

// This is a system call — crosses into the kernel
ssize_t bytes = write(fd, buf, n);
```

Even though `write()` looks like an ordinary C function, it is a thin libc wrapper that triggers the `syscall` instruction, which causes a hardware trap into kernel mode.

## The libc Wrapper Layer

Most programs never issue raw system calls. The C standard library (glibc on Linux, libc on macOS) provides wrappers that:

1. Place the system call number into the correct register (`rax` on x86-64).
2. Place arguments into `rdi`, `rsi`, `rdx`, `r10`, `r8`, `r9`.
3. Execute the `syscall` instruction.
4. Check the return value; if negative, set `errno` and return `-1`.

```asm
; Simplified glibc write() wrapper (x86-64)
mov rax, 1       ; syscall number for write
mov rdi, fd      ; arg1: file descriptor
mov rsi, buf     ; arg2: buffer pointer
mov rdx, count   ; arg3: byte count
syscall          ; trap into kernel
```

## Common Pitfall

Developers sometimes assume every libc call is a system call. It is not. `printf()` may buffer output in user space and only call `write()` when the buffer is full or `fflush()` is called. Profiling with `strace` reveals which calls actually cross into the kernel.

**Interview answer:** A system call crosses the user–kernel privilege boundary via a hardware trap (`syscall` instruction), switching to Ring 0 and using the kernel stack, while a regular function call stays entirely in Ring 3 user space at a cost roughly 100× lower.
