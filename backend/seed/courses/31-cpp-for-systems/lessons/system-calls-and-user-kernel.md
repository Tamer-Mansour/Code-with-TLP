# System Calls and the User/Kernel Boundary

Every time a C++ program reads a file, allocates memory, or creates a thread, it crosses from user space into the kernel. Understanding this boundary — how it works, why it exists, and what it costs — is foundational OS knowledge.

## Why Two Privilege Levels?

Modern CPUs implement at least two privilege rings:

| Ring | Name | What Runs Here |
|---|---|---|
| 0 | Kernel mode | OS kernel, device drivers |
| 3 | User mode | Applications, libraries |

In **user mode**, the CPU enforces restrictions: no direct access to hardware ports, no modifying page tables, no disabling interrupts. This prevents buggy or malicious programs from corrupting the system.

In **kernel mode**, all instructions are permitted. The OS earns this privilege by being the first thing that runs after boot.

> **Interview answer:** User mode restricts hardware access to protect the system; a system call is a controlled gate into kernel mode with full privilege.

## The System Call Mechanism

A system call is an intentional, hardware-mediated transition from ring 3 to ring 0:

1. User code loads syscall number and arguments into registers.
2. User code executes the `syscall` instruction (x86-64) or `svc` (ARM64).
3. The CPU atomically:
   - Switches to ring 0.
   - Jumps to the kernel's syscall entry point (stored in `MSR_LSTAR` on x86-64).
   - Saves user registers on the kernel stack.
4. Kernel validates arguments, performs the operation, stores the result.
5. Kernel executes `sysret`, restoring ring 3 and user registers.

```asm
; x86-64 raw syscall example: write(1, "hi\n", 3)
mov rax, 1          ; syscall number for write
mov rdi, 1          ; fd = stdout
lea rsi, [msg]      ; buffer
mov rdx, 3          ; length
syscall             ; trap into kernel
```

In C++, you rarely use raw `syscall`; the C library wraps syscalls in functions like `write()`, `read()`, `open()`.

## Anatomy of a System Call in C++

```cpp
#include <unistd.h>
#include <fcntl.h>

int main() {
    // open() → syscall open (no. 2 on x86-64 Linux)
    int fd = open("/etc/hostname", O_RDONLY);

    char buf[64];
    // read() → syscall read (no. 0)
    ssize_t n = read(fd, buf, sizeof(buf) - 1);
    buf[n] = '\0';

    // write() → syscall write (no. 1)
    write(1, buf, n);

    // close() → syscall close (no. 3)
    close(fd);
    return 0;
}
```

Each library function is a thin wrapper: marshal arguments into registers, execute `syscall`, check for errors (negative return → set `errno`), return the result.

## Cost of a System Call

A syscall is far more expensive than a regular function call:

| Operation | Approximate Cost |
|---|---|
| Function call (same stack) | ~1–5 ns |
| System call (with Spectre mitigations) | ~100–300 ns |
| System call + kernel work (e.g., `read` from disk cache) | ~1–5 µs |

Sources of cost:

- CPU privilege switch and register save/restore.
- Kernel stack setup and teardown.
- **Spectre/Meltdown mitigations** (KPTI on x86-64) require flushing TLB on entry and exit — adds ~100 ns.
- Potential cache miss on first access to kernel data.

## Reducing System Call Overhead

- **Batch I/O:** `writev()` / `readv()` combine multiple buffers into one syscall.
- **`io_uring`** (Linux 5.1+): submits a ring of I/O requests and completions; many operations require zero syscalls after setup.
- **`vDSO`** (virtual Dynamic Shared Object): maps certain kernel functions (e.g., `clock_gettime`, `gettimeofday`) into user space so they run without a privilege switch.
- **Memory-mapped I/O (`mmap`):** access file data as memory reads/writes with no syscall per access.

## Common System Call Categories

| Category | Examples |
|---|---|
| Process control | `fork`, `exec`, `exit`, `wait`, `getpid` |
| File I/O | `open`, `read`, `write`, `close`, `lseek`, `stat` |
| Memory | `mmap`, `munmap`, `brk` |
| Networking | `socket`, `bind`, `connect`, `send`, `recv` |
| Synchronization | `futex`, `semop` |
| Signals | `kill`, `sigaction`, `pause` |

## Tracing System Calls

```bash
# Linux: trace all syscalls of a program
strace ./my_program

# Show only file-related syscalls
strace -e trace=file ./my_program

# Count calls and timing
strace -c ./my_program
```

`strace` is invaluable for debugging unexpected file accesses, permission errors, and performance bottlenecks at the syscall layer.

## Common Pitfalls

- Calling `fflush(stdout)` in a tight loop — triggers a syscall every call; buffer instead.
- Checking `errno` without verifying the return value first — `errno` is only meaningful when the function signals an error.
- Forgetting that `errno` is thread-local — safe to read per-thread, but must be read immediately after the failing call.
