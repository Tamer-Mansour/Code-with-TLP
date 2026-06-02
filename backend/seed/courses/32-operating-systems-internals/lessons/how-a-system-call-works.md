# How a System Call Works: From libc to the Kernel

Tracing a single `write()` call from the C source line all the way down to device registers illuminates every layer of the operating system. This path is asked about frequently in systems interviews.

## The Full Path

```
User code
  │  write(fd, buf, n)        ← C function call
  ▼
libc write() wrapper
  │  load syscall number, marshal args
  │  syscall instruction       ← hardware trap
  ▼
CPU exception handler (entry_SYSCALL_64)
  │  save user registers to kernel stack
  │  look up handler in sys_call_table[]
  ▼
sys_write() in kernel
  │  validate fd, buf, n
  │  call vfs_write()
  ▼
VFS layer
  │  route to file-system or device driver
  ▼
Driver / page cache
  │  copy data or schedule I/O
  ▼
Return through the same layers
  ▼
libc: check return, set errno if negative
  ▼
User code receives return value
```

## Step 1 — User Code Calls libc

You write `write(1, "hello\n", 6)`. This invokes the glibc wrapper, which is not a system call itself — it is ordinary C code that prepares the transition.

## Step 2 — Argument Marshaling

The wrapper places values into specific registers as defined by the x86-64 Linux syscall ABI:

```c
// Conceptual equivalent of what glibc does
register long rax asm("rax") = 1;   // SYS_write
register long rdi asm("rdi") = fd;
register long rsi asm("rsi") = (long)buf;
register long rdx asm("rdx") = count;
asm volatile ("syscall" : "=a"(ret) : "0"(rax), "r"(rdi), "r"(rsi), "r"(rdx) : "memory");
```

## Step 3 — The syscall Instruction

The `syscall` instruction (x86-64) does all of this atomically:

1. Saves `rip` (return address) into `rcx`.
2. Saves `rflags` into `r11`.
3. Loads the kernel code segment and stack pointer (from MSRs configured at boot).
4. Jumps to `entry_SYSCALL_64` — the kernel's syscall entry point.

The CPU is now in Ring 0. The user-space stack is no longer active; the kernel stack for this thread is used.

## Step 4 — Kernel Entry and Dispatch

```c
// Simplified Linux kernel entry (arch/x86/entry/entry_64.S)
// After swapping to kernel stack and saving registers:
call do_syscall_64

// do_syscall_64 (simplified):
void do_syscall_64(struct pt_regs *regs) {
    unsigned long nr = regs->orig_ax; // syscall number from rax
    if (nr < NR_syscalls)
        regs->ax = sys_call_table[nr](regs); // dispatch
}
```

`sys_call_table` is an array of function pointers indexed by syscall number. For `write`, index 1 maps to `__x64_sys_write`.

## Step 5 — The Kernel Handler

```c
SYSCALL_DEFINE3(write, unsigned int, fd, const char __user *, buf, size_t, count)
{
    struct fd f = fdget_pos(fd);
    if (!f.file)
        return -EBADF;
    ret = vfs_write(f.file, buf, count, &pos);
    fdput_pos(f);
    return ret;
}
```

The `__user` annotation tells the kernel static checker that `buf` is a user-space pointer. The kernel must use `copy_from_user()` to read it safely — direct dereference could fault or be exploited.

## Step 6 — Return to User Space

After `sys_write` returns, the kernel:

1. Stores the return value in `rax` on the saved register frame.
2. Executes `sysretq`, restoring `rip` from `rcx` and `rflags` from `r11`.
3. CPU drops back to Ring 3.

libc checks whether `rax` holds a negative errno-style code, and if so sets the thread-local `errno` and returns `-1`.

## Key Pitfalls

- **Context switch can happen between steps 4 and 6.** If the kernel handler blocks (e.g., waiting for disk), the scheduler may run another thread before this one resumes.
- **Signals can be delivered at the return point.** The kernel checks for pending signals before returning to user space.
- **`errno` is not atomic.** It is thread-local storage; do not read it across threads.

**Interview answer:** A system call marshals arguments into registers, executes the `syscall` instruction to trap into Ring 0, the kernel dispatches via `sys_call_table`, runs the handler (e.g., `sys_write`), then `sysretq` restores user-space execution with the return value in `rax`.
