# Interview Drill: System Call Questions

These are the system call questions that appear most frequently in operating systems and systems-design interviews at top-tier companies. Each answer is crafted to be concise, accurate, and deployable in 30 seconds.

---

## Q1: What is the difference between a system call and a library call?

**One-line answer:** A system call crosses the CPU privilege boundary from Ring 3 to Ring 0 via the `syscall` instruction; a library call stays in user space.

**Deeper detail:** Library calls like `printf` may internally invoke system calls like `write`, but they are not system calls themselves. `printf` buffers output in user space; only when the buffer is flushed does a `write` syscall occur. Tools like `strace` reveal the actual syscall boundary.

---

## Q2: What happens, step by step, when a process calls `read(fd, buf, n)`?

1. libc wrapper loads syscall number 0 into `rax`, args into `rdi`/`rsi`/`rdx`.
2. `syscall` instruction traps into Ring 0, saves user registers, jumps to `entry_SYSCALL_64`.
3. Kernel dispatches to `sys_read` via `sys_call_table[0]`.
4. VFS validates the fd, checks permissions.
5. If data is in the page cache: `copy_to_user` and return.
6. If not: submit block I/O, set thread state to `TASK_INTERRUPTIBLE`, call `schedule()`.
7. When I/O completes, wake up the thread, copy data, return byte count in `rax`.
8. `sysretq` restores user registers; libc checks `rax` for error.

---

## Q3: Why is `rcx` not used for syscall argument 4 on x86-64?

The `syscall` instruction clobbers `rcx` (saving `rip` there as the return address) and `r11` (saving `rflags`). So the Linux syscall ABI uses `r10` as argument 4, while the C ABI uses `rcx`. The libc wrapper explicitly moves `rcx` to `r10` before issuing `syscall`.

---

## Q4: What is `EBADF` and when does `write()` return it?

`EBADF` (errno 9) means "bad file descriptor." `write()` returns it when:
- `fd` is negative or greater than the per-process fd limit.
- `fd` is a valid number but not open in this process.
- `fd` is open but not in write mode (e.g., opened with `O_RDONLY`).

---

## Q5: What is the vDSO and which calls benefit from it?

The Virtual Dynamic Shared Object is a kernel-provided shared library mapped into every process. It contains implementations of `clock_gettime`, `gettimeofday`, `time`, and `getcpu` that read from a kernel-maintained shared memory page without entering the kernel. This reduces `clock_gettime(CLOCK_MONOTONIC)` from ~200 ns to ~3–10 ns.

---

## Q6: What is `EINTR` and how should programs handle it?

When a blocking syscall (e.g., `read`, `write`, `accept`) is interrupted by a signal before completion, the kernel returns `-EINTR` (errno 4). The correct response is to **retry the syscall in a loop**:

```c
ssize_t safe_read(int fd, void *buf, size_t n) {
    ssize_t ret;
    do {
        ret = read(fd, buf, n);
    } while (ret < 0 && errno == EINTR);
    return ret;
}
```

SA_RESTART (set in `sigaction`) causes the kernel to auto-restart certain syscalls on EINTR, but not all (notably `poll`, `select`, `epoll_wait`).

---

## Q7: What does `strace` do, and how is it implemented?

`strace` traces syscalls made by a process. It uses the `ptrace` syscall with `PTRACE_SYSCALL` to ask the kernel to pause the traced process at every syscall entry and exit. `strace` then reads the register state from the traced process to extract the syscall number and arguments.

```bash
strace -e trace=read,write ./myprogram
strace -c ./myprogram    # summary: count, time per syscall
```

---

## Q8: What is a "short write" and why does it happen?

`write(fd, buf, n)` may return a positive value less than `n`. This is a valid return, not an error. It happens:
- On non-blocking sockets when the send buffer is partially full.
- On pipes when the remaining pipe buffer capacity is smaller than `n`.
- On regular files if a signal interrupted mid-write.

Always loop until all bytes are written:

```c
size_t write_all(int fd, const void *buf, size_t n) {
    size_t sent = 0;
    while (sent < n) {
        ssize_t r = write(fd, (char*)buf + sent, n - sent);
        if (r <= 0) return sent;
        sent += r;
    }
    return sent;
}
```

---

## Q9: What is the difference between `TASK_INTERRUPTIBLE` and `TASK_UNINTERRUPTIBLE`?

| State | Signal Interrupts? | `ps` code |
|---|---|---|
| `TASK_INTERRUPTIBLE` | Yes → returns `EINTR` | `S` |
| `TASK_UNINTERRUPTIBLE` | No | `D` |

Disk I/O typically uses `TASK_UNINTERRUPTIBLE` to prevent a half-completed I/O from being abandoned, which could corrupt filesystem structures. A process in `D` state cannot be killed until the I/O completes or the device is detached.

---

## Q10: What happens if you pass a kernel-space pointer to `write()`?

The kernel uses `copy_from_user()`, which validates that the pointer falls within the user-space address range. Passing a kernel pointer causes `copy_from_user` to return an error, and `write()` returns `-EFAULT`. This is a fundamental security boundary — user code cannot trick the kernel into reading or writing arbitrary kernel memory via syscall arguments.
