# The Process Model

A **process** is a program in execution. The distinction is crucial: a program is a passive file on disk; a process is an active instance of that program with its own CPU registers, memory, open files, and execution state. The same program can give rise to multiple simultaneous processes (e.g., five `python3` interpreters running five different scripts at once).

## What a Process Contains

The OS represents each process with a **Process Control Block (PCB)** — a kernel data structure that stores everything the OS needs to manage the process. In Linux, the PCB is the `task_struct` (defined in `include/linux/sched.h`, currently over 700 fields).

| PCB Field | Description |
|-----------|-------------|
| **Process ID (PID)** | Unique integer identifier; root always has PID 1 |
| **Process state** | Running, Ready, Waiting, Stopped, Zombie |
| **Program counter** | Address of the next instruction to execute |
| **CPU registers** | Snapshot of all general-purpose registers |
| **Memory maps** | Virtual address space regions (code, heap, stack, mmap) |
| **Open file table** | List of file descriptors and their offsets |
| **Scheduling info** | Priority, virtual runtime, nice value |
| **Accounting** | CPU time consumed, memory peak, start time |
| **Parent PID (PPID)** | Which process created this one |
| **Signal table** | Registered signal handlers |
| **Namespaces** | (Linux) Network, PID, mount namespaces (for containers) |

## Process State Diagram

A process moves through well-defined states throughout its life:

```
         admit
  NEW ──────────► READY ◄────────────────┐
                    │                    │
              dispatch                   │ I/O complete /
              (scheduler)                │ event arrives
                    │                    │
                    ▼                    │
                RUNNING ─────────────────┘
                    │          (preemption or yield)
          ┌─────────┴──────────┐
          │                    │
     I/O request           process calls exit()
     or event wait              │
          │                     ▼
          ▼              TERMINATED (Zombie)
        WAITING           PCB kept until parent
                          calls wait(); then freed
```

- **READY** — eligible to run, but the CPU is busy with another process. Lives on the ready queue.
- **RUNNING** — currently executing on a CPU core. On an N-core machine, at most N processes can be RUNNING at once.
- **WAITING (Blocked)** — waiting for an event: disk I/O completion, network data, a lock, a sleep timer.
- **ZOMBIE** — the process has exited but its PCB is kept until the parent reads the exit status with `wait()`.
- **STOPPED** — paused by a signal (SIGSTOP or Ctrl+Z); resumes on SIGCONT.

## State Transitions in Detail

**READY → RUNNING:** The scheduler picks this process and the dispatcher loads its context onto a CPU core.

**RUNNING → READY:** The time quantum expired (preemption via timer interrupt), or a higher-priority process became ready.

**RUNNING → WAITING:** The process issued a blocking system call (`read` on an empty pipe, `recv` on a socket, `mutex_lock` when held by another thread). The kernel removes the process from the CPU and adds it to the appropriate wait queue.

**WAITING → READY:** The awaited event occurred (I/O completed, lock released, signal delivered). The kernel moves the process back to the ready queue.

## The Process Address Space

Each process lives in its own **virtual address space**. On a 64-bit Linux system (with 48-bit user VA), a typical layout:

```
Virtual address (hex)
  0xFFFF_8000_0000_0000  ──── Kernel space (invisible from user mode) ────
  ...
  0x0000_7FFF_FFFF_F000  ──── Stack (grows downward) ────────────────────
                                local variables, function call frames
                          ──── (unmapped gap — grows with stack) ─────────
                          ──── Memory-mapped region ───────────────────────
                                shared libraries (.so), anonymous mmap()
                          ──── Heap (grows upward via brk/mmap) ──────────
                                malloc() lives here
  0x0000_0000_0060_1000  ──── BSS segment (zero-initialized globals) ─────
  0x0000_0000_0060_0000  ──── Data segment (initialized globals) ─────────
  0x0000_0000_0040_0000  ──── Text segment (read-only code + constants) ───
```

Two processes can share the same virtual addresses — the page table maps them to completely different physical frames. This isolation is enforced by hardware: process A cannot read process B's memory even if they use the same virtual address.

## How the Kernel Tracks All Processes

Linux maintains a doubly-linked list of all `task_struct`s. The currently-running task is pointed to by the `current` macro (which reads a per-CPU register). The scheduler iterates this list (actually a red-black tree for CFS) to select the next process.

```bash
# See the process tree
ps auxf           # forest mode
pstree -p         # PID-annotated tree

# Inspect a specific process
cat /proc/1234/status    # key PCB fields
cat /proc/1234/maps      # virtual address space layout
ls -l /proc/1234/fd/     # open file descriptors
```

## Multiprogramming vs. Multitasking vs. Multiprocessing

| Term | Meaning |
|------|---------|
| **Multiprogramming** | Multiple processes in memory; CPU switches to avoid idle time (batch era) |
| **Multitasking / time-sharing** | CPU switches rapidly (milliseconds) — creates illusion of simultaneous execution |
| **Multiprocessing** | Multiple physical CPU cores executing processes truly in parallel |
| **Distributed computing** | Multiple physical machines cooperating via a network |

A modern server simultaneously uses all four: it multiprograms to keep CPUs busy, time-shares interactive users, runs truly parallel across 64 cores, and may distribute work across a cluster.

## Process Creation Costs

Creating a process has non-trivial cost:
- Allocate a new PID, `task_struct`, kernel stack.
- Set up page tables (Copy-on-Write from parent, or fresh for `exec`).
- Copy file descriptor table, signal handlers.
- Place the new process on the ready queue.

On Linux, `fork()` + `exec()` for a small shell command takes roughly 1–5 ms. This is why servers use long-lived process pools (or threads) rather than forking per request.

## Key Takeaways

- A **process** = program + execution context (registers, memory, open files, OS metadata).
- The **PCB** (`task_struct` in Linux) is the kernel's data structure for tracking everything about a process.
- Processes move through states: **New → Ready → Running → Waiting → Terminated**.
- Each process has an isolated **virtual address space** — they cannot directly read each other's memory.
- The OS creates the illusion of parallel execution via rapid context switching.
- `ps`, `pstree`, and `/proc/<pid>/` are real Linux tools for inspecting live processes.
