# Quiz: Processes and the Process Control Block

**Q1. Which of the following best describes the difference between a program and a process?**

- [ ] A program is running in memory; a process is stored on disk.
- [x] A program is a static binary on disk; a process is a running instance of that program with its own address space and kernel-managed state.
- [ ] A process can only run one program; a program can be shared between multiple processes without any differences.
- [ ] A process and a program are the same thing; the terms are interchangeable.

_A program is passive (a file); a process is active — the OS allocates a PCB, virtual address space, and scheduling slot when it starts running._

---

**Q2. In the five-state process model, which transition is NOT directly possible?**

- [ ] READY → RUNNING (via scheduler dispatch)
- [ ] RUNNING → WAITING (via a blocking I/O call)
- [x] WAITING → RUNNING (directly, without passing through READY)
- [ ] RUNNING → READY (via preemption)

_When an I/O operation completes, the process moves from WAITING back to the READY queue. The scheduler must then dispatch it before it can enter RUNNING. A direct WAITING → RUNNING transition does not exist in the standard model._

---

**Q3. What is stored in the CPU context portion of the Process Control Block (PCB)?**

- [ ] The process's heap contents and malloc bookkeeping structures.
- [ ] Open file descriptors and the current working directory.
- [x] The values of CPU registers (program counter, stack pointer, general-purpose registers, and flags) at the point the process was last preempted or blocked.
- [ ] The process's page tables and physical memory frame allocation.

_The PCB's CPU context is the exact register snapshot that lets the OS resume the process on a context switch — it is the "bookmark" into the instruction stream._

---

**Q4. A child process calls exit() but the parent never calls wait(). What is the child's state, and what resource does it still hold?**

- [ ] The child is immediately and completely removed from the system; no resources are held.
- [ ] The child stays in the WAITING state, holding its address space until the parent calls wait().
- [x] The child becomes a zombie (TERMINATED state) and retains its PCB, holding a PID slot until the parent calls wait().
- [ ] The child is adopted by init, which automatically frees its PCB within 1 second.

_A zombie has released its address space and file descriptors, but the kernel keeps the PCB (and PID) so the parent can later retrieve the exit status via wait()._

---

**Q5. What is the primary purpose of the copy-on-write (COW) mechanism used by fork()?**

- [ ] To encrypt the child's address space so the parent cannot read the child's memory after the fork.
- [ ] To ensure the child's code segment is always a fresh copy of the binary file on disk.
- [x] To avoid immediately duplicating all of the parent's memory pages by marking them shared and read-only, copying a page only when either process actually writes to it.
- [ ] To allow two processes to share a single page table entry permanently with no overhead.

_COW makes fork() fast even for large processes — gigabytes of data are not physically copied unless modified. Only the pages that diverge are duplicated._

---

**Q6. After a successful exec() call, which of the following is preserved in the new program?**

- [ ] The previous program's text segment (machine code).
- [ ] Signal handlers registered by the old program.
- [ ] The heap and its dynamic allocations from the old program.
- [x] The process ID (PID) and open file descriptors (unless marked FD_CLOEXEC).

_exec() replaces the entire address space — code, data, heap, stack — and resets signal handlers to defaults, but the PID remains the same and open file descriptors survive unless the close-on-exec flag is set. This is what lets shells set up I/O redirections between fork() and exec()._
