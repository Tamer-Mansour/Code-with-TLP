# Interview Drill: Process Fundamentals

This lesson walks through the most common interview questions on processes, PCBs, context switches, and process lifecycle. For each question, you'll find the key insight to lead with, the follow-up depth an interviewer typically probes, and a crisp answer you can deliver under time pressure.

---

## Q1: What is the difference between a process and a thread?

**Key insight:** Resource ownership vs. execution.

- A **process** is the unit of resource ownership — it has its own virtual address space, file descriptors, and PID.
- A **thread** is the unit of execution — it has its own stack, program counter, and register set, but shares the address space and resources of the process it belongs to.

**Follow-up pitfall:** "Can two threads in the same process corrupt each other's stack?" — Yes, if one overflows its stack (unbounded recursion), it can overwrite adjacent thread stacks since they all live in the same address space.

> **Crisp answer:** A process owns a virtual address space and resources; threads are lightweight execution units that share a process's address space but have independent stacks and register state.

---

## Q2: What is a context switch and what does it cost?

**Key insight:** Save state, pick next, restore state.

Steps: (1) hardware saves minimal interrupt frame, (2) kernel saves all GPRs into the outgoing PCB, (3) scheduler picks the next process, (4) kernel restores GPRs from the new PCB, (5) page table pointer (CR3) is switched, flushing the TLB.

**Cost factors:**
- Direct: ~100 ns for register save/restore.
- Indirect: TLB flush (microseconds to refill), instruction/data cache cold start (up to hundreds of µs).

> **Crisp answer:** A context switch saves the outgoing process's CPU registers into its PCB, selects the next process, restores that process's registers, and switches the page table — costing roughly 1–10 µs including cache and TLB warm-up.

---

## Q3: What is a zombie process and how do you prevent it?

**Key insight:** A zombie is a process that has exited but whose exit status has not been collected.

When a child calls `exit()`, the kernel frees its address space but retains the PCB in the ZOMBIE state until the parent calls `wait()`. If the parent never calls `wait()`, the PCB and PID slot are leaked.

**Prevention:**
- Call `waitpid()` after each `fork()`.
- Install a `SIGCHLD` handler that calls `waitpid(-1, NULL, WNOHANG)` in a loop.
- Use the double-fork trick so the grandchild is adopted by init, which always reaps.

> **Crisp answer:** A zombie process has exited but its PCB is kept until the parent calls `wait()`. Prevent accumulation by installing a SIGCHLD handler that non-blockingly reaps all children with `waitpid(-1, NULL, WNOHANG)`.

---

## Q4: What happens when fork() is called?

**Key insight:** Copy-on-write clone with a new PID.

- A new PCB is allocated for the child.
- The child's virtual address space is set up as a copy-on-write mirror of the parent's — pages are shared and marked read-only until either process writes.
- File descriptors are duplicated (both point to the same open-file table entries).
- The child gets a new PID; `fork()` returns the child's PID in the parent and 0 in the child.

> **Crisp answer:** `fork()` creates a new process by copying the parent's PCB and marking the address space copy-on-write. The child has a new PID; both processes run from the line after `fork()`, distinguished by the return value (0 in child, child's PID in parent).

---

## Q5: What is the difference between SIGKILL and SIGTERM?

**Key insight:** SIGTERM is a polite request; SIGKILL is an unconditional kernel-level termination.

- `SIGTERM` (signal 15): delivered to the process, which may catch it, clean up, and exit gracefully. A process can ignore or block SIGTERM.
- `SIGKILL` (signal 9): handled entirely by the kernel — the process never even sees it. Cannot be caught, blocked, or ignored. However, a process in `TASK_UNINTERRUPTIBLE` (D state) will not be killed until the kernel wait it is blocked on completes.

> **Crisp answer:** SIGTERM is a catchable signal asking the process to exit gracefully; SIGKILL is uncatchable and handled by the kernel, immediately terminating the process — but it cannot affect a process stuck in uninterruptible kernel sleep (D state).

---

## Q6: What is stored in the PCB?

**Key insight:** Everything the OS needs to suspend and resume a process.

- **Process identity**: PID, PPID, UID, GID.
- **CPU context**: all general-purpose registers, program counter, stack pointer, flags, FPU state.
- **Scheduling info**: state (READY/RUNNING/WAITING), priority, CPU time used.
- **Memory info**: page table pointer (CR3), memory map.
- **I/O info**: file descriptor table, current working directory.
- **Signal info**: pending and blocked signal masks, signal handler table.

> **Crisp answer:** The PCB stores a process's PID, saved CPU register context, scheduling state and priority, page table pointer, file descriptor table, and signal state — everything needed to suspend the process on a context switch and resume it later.

---

## Quick-Reference Cheat Sheet

| Concept | One-line summary |
|---------|-----------------|
| Process | Running program — owns virtual address space + resources |
| Thread | Execution stream inside a process — shares AS, has own stack |
| PCB | Kernel data structure holding all state needed to resume a process |
| Context switch | Save registers to old PCB, restore from new PCB, swap page table |
| Zombie | Exited child whose exit status has not been collected by parent |
| Orphan | Child whose parent exited; adopted by init, safely reaped |
| fork() | COW clone with new PID; returns 0 in child, child PID in parent |
| exec() | Replaces address space with new program; PID unchanged |
