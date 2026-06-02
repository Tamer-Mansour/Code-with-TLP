# Quiz: OS Concepts for the Interview

**Q1. A process calls `fork()`. What value does the child process receive as the return value of `fork()`?**
- [ ] The parent's PID
- [x] 0
- [ ] -1
- [ ] The child's own PID

The child always receives 0 from `fork()`; the parent receives the child's PID. A return value of -1 indicates an error (in the parent only).

---

**Q2. Given a page size of 4 KB and a virtual address of 0x5A3C, what is the Virtual Page Number (VPN)?**
- [ ] 0x3C
- [ ] 0xA3C
- [x] 5
- [ ] 0x5A

4 KB = 2^12, so offset bits = 12. VPN = 0x5A3C >> 12 = 5. The offset is 0x5A3C & 0xFFF = 0xA3C.

---

**Q3. Three processes with burst times 10, 5, and 8 ms arrive simultaneously. Under FCFS scheduling, what is the average waiting time?**
- [ ] 0 ms
- [ ] 5 ms
- [x] 8.33 ms
- [ ] 11.67 ms

P1 waits 0 ms, P2 waits 10 ms, P3 waits 15 ms. Average = (0 + 10 + 15) / 3 = 8.33 ms. The convoy effect is visible here — P2 and P3 wait behind the long P1 job.

---

**Q4. Which of the following is the PRIMARY hidden cost of a process context switch beyond saving and restoring CPU registers?**
- [ ] Re-reading the executable from disk
- [ ] Resetting the program counter
- [x] TLB invalidation and cache pollution
- [ ] Closing and reopening file descriptors

The largest hidden costs are the TLB flush (virtual address translations from the old process are invalid) and cache eviction (the new process displaces the old process's working set from L1/L2/L3 caches).

---

**Q5. What is the key difference between `exit()` and `_exit()` when called in a child process after `fork()`?**
- [ ] `_exit()` terminates the parent as well
- [ ] `exit()` is not available in child processes
- [x] `exit()` flushes C stdio buffers and runs atexit handlers; `_exit()` does not
- [ ] `_exit()` sends SIGCHLD to the parent while `exit()` does not

Using `exit()` in a child can double-flush the parent's stdio buffers (since the child inherits a copy of them after `fork()`). `_exit()` is preferred in the child because it goes straight to the kernel without any C library cleanup.

---

**Q6. Which scheduling algorithm is proven to minimize average waiting time when all burst times are known in advance?**
- [ ] First-Come, First-Served (FCFS)
- [ ] Round Robin with a small quantum
- [ ] Priority Scheduling
- [x] Shortest Job First (SJF)

SJF minimizes average waiting time by always running the shortest remaining job first. Its practical limitation is that burst times are generally not known in advance; the OS must estimate them using exponential moving average.
