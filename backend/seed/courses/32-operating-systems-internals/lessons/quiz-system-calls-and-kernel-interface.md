# Quiz: System Calls and the Kernel Interface

**Q1. On x86-64 Linux, which register holds the system call number when the `syscall` instruction is executed?**

- [ ] `rdi`
- [x] `rax`
- [ ] `r10`
- [ ] `rcx`

The syscall number is always placed in `rax` before executing the `syscall` instruction. `rdi` holds the first argument, `r10` holds the fourth argument, and `rcx` is clobbered by the `syscall` instruction to save the return address.

---

**Q2. Why does the x86-64 Linux syscall ABI use `r10` for the fourth argument instead of `rcx` (which the C ABI uses)?**

- [ ] `rcx` is reserved for the kernel stack pointer
- [ ] `rcx` does not exist in 64-bit mode
- [x] The `syscall` instruction clobbers `rcx` to store the return address (`rip`)
- [ ] `r10` is faster to access than `rcx`

The `syscall` instruction saves `rip` (the return address) into `rcx` and saves `rflags` into `r11` automatically. This means `rcx` cannot be used to hold an argument — the kernel would see whatever value the CPU stored there, not the original argument.

---

**Q3. A process calls `write(fd, buf, 4096)` and receives the return value `2048`. What does this mean?**

- [ ] An error occurred and errno is set to 2048
- [ ] The kernel wrote 2048 bytes and silently discarded the rest
- [x] Only 2048 bytes were written; the caller must call `write` again for the remaining bytes
- [ ] The file descriptor was closed after 2048 bytes

A return value between 1 and the requested count is a "short write" — partial success, not an error. The caller is responsible for retrying with the remaining data. This commonly happens on non-blocking sockets or pipes.

---

**Q4. What mechanism does the Linux vDSO use to implement `clock_gettime()` without entering the kernel?**

- [ ] It uses a privileged CPU instruction only available in Ring 3
- [ ] It makes a very fast `int 0x80` call that bypasses scheduling
- [x] It reads from a shared memory page that the kernel updates on each timer tick
- [ ] It caches the last known time and adds a CPU cycle counter offset through a kernel module

The kernel maintains a `vsyscall_gtod_data` structure in a page that is mapped readable into every process's address space. The vDSO reads this page directly without any privilege switch. If the data changes concurrently, a sequence counter ensures consistency.

---

**Q5. A process in state `D` (TASK_UNINTERRUPTIBLE) is sent `SIGKILL`. What happens?**

- [ ] The process is immediately terminated
- [ ] The process is terminated after a 5-second timeout
- [x] The signal is pending; the process cannot be killed until it leaves the uninterruptible sleep
- [ ] The kernel raises a kernel oops

`TASK_UNINTERRUPTIBLE` means the thread will not wake up for signals, including `SIGKILL`. The signal becomes pending and is delivered once the kernel wakes the thread (when the I/O or resource is available). This is why `D`-state processes cannot be killed without completing or removing the waited-upon resource.

---

**Q6. Which of the following calls goes through the vDSO fast path and does NOT require a kernel privilege switch on a standard Linux x86-64 system?**

- [ ] `getpid()`
- [ ] `open()`
- [x] `clock_gettime(CLOCK_MONOTONIC, &ts)`
- [ ] `read(fd, buf, n)`

`clock_gettime(CLOCK_MONOTONIC)` is one of the primary vDSO-accelerated calls on x86-64 Linux. `getpid()`, `open()`, and `read()` all require a full kernel entry via the `syscall` instruction.
