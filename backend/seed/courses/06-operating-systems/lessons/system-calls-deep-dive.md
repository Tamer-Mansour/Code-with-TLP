# System Calls: The Kernel API

A **system call** is the programmatic interface through which a user-space program requests a service from the operating system kernel. Think of it as the OS's public API — but instead of a function call within your process, it is a controlled entry point that crosses the user/kernel boundary, validated and audited by the kernel.

## Categories of System Calls

POSIX (the standard most Unix-like OSes follow) groups system calls into categories:

| Category | Examples | What They Do |
|----------|----------|-------------|
| **Process control** | `fork`, `exec`, `exit`, `wait`, `kill` | Create, replace, terminate, signal processes |
| **File management** | `open`, `read`, `write`, `close`, `lseek`, `stat` | Create and manipulate files and directories |
| **Device management** | `ioctl`, `read`/`write` on `/dev/*` | Interact with hardware via device abstraction |
| **Information** | `getpid`, `getuid`, `clock_gettime`, `uname` | Query OS state, process attributes, time |
| **Communication** | `pipe`, `socket`, `sendto`, `recvfrom`, `mmap` | IPC and network I/O |
| **Memory** | `mmap`, `munmap`, `brk`, `mprotect` | Map/unmap virtual memory regions, set protections |

## The Life of a `read()` System Call

Tracing `data = os.read(fd, 1024)` in Python all the way to hardware:

```
Python layer
  os.read(fd, 1024)
       │ (calls CPython's posix_read → C read())
       ▼
C library (glibc)
  read(fd, buf, 1024)
       │ Load syscall number 0 into rax (on Linux x86-64)
       │ Load fd into rdi, buf ptr into rsi, 1024 into rdx
       ▼
  syscall instruction  ← single instruction, hardware traps
       │ CPU: saves rip, rsp; loads kernel entry (MSR_LSTAR)
       │ CPU: CPL 3 → 0
       ▼
Kernel: sys_read()
  1. Look up fd in current process's file descriptor table
  2. Validate: fd is open, process has read permission
  3. Check the VFS inode's f_op->read_iter()
  4a. If data is in the page cache → copy to user buffer, return count
  4b. If data NOT in cache:
       - Add the process to a wait queue on this inode
       - Mark process state = TASK_INTERRUPTIBLE
       - Call schedule() → another process runs
       - (disk I/O completes asynchronously)
       - DMA interrupt → process woken → resume here
       - Copy data from page cache to user buffer
  5. Return byte count in rax (or negative errno)
       │ sysretq: CPL 0 → 3, restore rip/rsp
       ▼
C library: unwraps return value, sets errno if negative
       ▼
Python: returns bytes object
```

This trace shows why I/O system calls can block for milliseconds: step 4b puts the process to sleep until the hardware signals completion.

## System Call Numbers and Calling Conventions

Linux x86-64 syscall numbers are defined in `<asm/unistd_64.h>`:

```
read    = 0
write   = 1
open    = 2
close   = 3
stat    = 4
mmap    = 9
brk     = 12
fork    = 57
execve  = 59
exit    = 60
wait4   = 61
```

Arguments are passed in registers in this order: `rdi`, `rsi`, `rdx`, `r10`, `r8`, `r9`. The return value comes back in `rax`. This is the **System V AMD64 ABI** for syscalls.

**Portability warning:** These numbers are platform-specific. `read` is 3 on x86 (32-bit), 63 on ARM64, 4 on MIPS. Always use libc wrappers — they handle the platform differences.

## strace: Watching System Calls in Real Time

`strace` uses `ptrace()` to intercept every system call a process makes:

```bash
$ strace -e trace=read,write python3 -c "print('hello')"
read(3, "\x7fELF\x02\x01\x01\x00\x00...", 832) = 832
read(3, "\x7fELF...", 4096) = 4096
write(1, "hello\n", 6)                  = 6
```

Format: `syscall_name(args) = return_value`. A negative return means an error; e.g., `-1 ENOENT (No such file or directory)`. The overhead of `strace` is significant (~10× slowdown) because every syscall triggers a `ptrace` trap.

## Measuring System Call Cost

A raw syscall that does almost nothing (like `getpid`) costs approximately:

| Scenario | Latency |
|----------|---------|
| `getpid` with vDSO (no mode switch) | ~4 ns |
| `getpid` without vDSO (full syscall) | ~100–200 ns |
| `read` 1 byte from a pipe (in cache) | ~300–500 ns |
| `read` 4KB from SSD (cache miss) | ~50–200 µs |
| `read` 4KB from HDD (cache miss) | ~5–10 ms |

The fixed overhead (~200 ns) means calling `write()` one byte at a time is catastrophically slow for bulk data. The C library buffers writes internally (via `fwrite`, `stdio`) to amortize syscall cost.

## VDSO: Avoiding the Mode Switch for Hot Syscalls

For very frequent, read-only kernel queries (e.g., `clock_gettime`, `gettimeofday`), Linux maps a special **vDSO** (virtual Dynamic Shared Object) into every process's address space:

```
Process address space:
  ...
  7ffff7ff9000-7ffff7ffb000  r-xp  [vdso]  ← kernel writes time here
  ...
```

The kernel updates a shared memory page with the current time. The vDSO reads it directly — no `syscall` instruction, no ring switch. This is why `clock_gettime(CLOCK_MONOTONIC)` can execute at ~4 ns instead of ~200 ns. The tradeoff: only pure read-only queries without side effects can use this mechanism.

## Windows System Calls

Windows uses the same `syscall`/`sysenter` hardware mechanism but exposes the **Win32 API** (`CreateFile`, `ReadFile`, `WriteFile`, `CreateProcess`) rather than raw syscall numbers. Raw NT syscall numbers (in `ntdll.dll`) change between Windows versions — only the Win32 API is stable across releases. The Win32 API is a documented, stable contract; the NT syscall table is an implementation detail.

On Windows, `ReadFile` → `ntdll!NtReadFile` → `syscall` into `ntoskrnl!NtReadFile`. One extra indirection, same concept.

## Error Handling

Unix syscalls return `-1` and set the global `errno` on failure. The kernel returns a negative error code (e.g., `-2` for `ENOENT`), and glibc negates it and sets `errno`:

```c
// C application
int fd = open("missing.txt", O_RDONLY);
if (fd == -1) {
    perror("open");   // prints "open: No such file or directory"
    // errno == ENOENT == 2
}
```

Common errno values:
- `ENOENT (2)` — file not found
- `EACCES (13)` — permission denied
- `EAGAIN (11)` — would block (non-blocking I/O)
- `EINTR (4)` — interrupted by signal (must retry)

## Key Takeaways

- System calls are the **only** legal way for user programs to request privileged OS services.
- They involve a hardware-enforced transition from ring 3 to ring 0 and back, costing ~100–300 ns for fast calls.
- Linux organizes system calls by number; the libc wrappers hide the raw numbers and handle the calling convention.
- Tools like `strace` let you observe all system calls a program makes in real time.
- The **vDSO** maps kernel data directly into user space to avoid mode switches for read-only hot paths like `clock_gettime`.
- I/O syscalls can block for milliseconds; the kernel puts the calling process to sleep and runs another.
- Always check return values and handle `errno` — system calls fail regularly (permissions, full disks, signals).
