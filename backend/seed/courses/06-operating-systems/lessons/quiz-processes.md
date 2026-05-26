# Quiz: Processes

**Q1. What is stored in a Process Control Block (PCB)?**

- [ ] Only the process's source code and compiled binary
- [x] CPU registers, program counter, memory maps, open files, and scheduling info
- [ ] The process's compiled binary and all dynamic libraries loaded into memory
- [ ] Only the process ID and the parent process ID

**Q2. After a successful `fork()` call, what is the return value in the child process?**

- [ ] The parent's PID
- [ ] -1 on success, 0 on failure
- [x] 0
- [ ] The child's own PID

**Q3. What does copy-on-write (COW) optimize after fork()?**

- [ ] Disk write batching to avoid redundant file system operations
- [ ] Network packet duplication when the child opens a socket
- [x] Memory copying — pages are shared between parent and child until one of them writes to them
- [ ] File descriptor duplication across subsequent exec() calls

**Q4. A process that has exited but whose parent has not yet called wait() is called:**

- [ ] An orphan process
- [ ] A daemon process
- [x] A zombie process
- [ ] A blocked process

**Q5. Which state transition moves a process from RUNNING to WAITING?**

- [ ] The scheduler selects it for the next time slot
- [ ] The process is first admitted to the system
- [x] The process issues a blocking system call such as read() on an empty pipe
- [ ] The process's time quantum expires and it is preempted

**Q6. What does exec() do to the calling process?**

- [ ] Creates a child and runs the new program in it, like fork() followed by exec()
- [x] Replaces the current process's code, data, heap, and stack with a new program image while keeping the same PID
- [ ] Forks the process and runs the new program in the parent, not the child
- [ ] Loads a shared library into the existing process heap without replacing anything
