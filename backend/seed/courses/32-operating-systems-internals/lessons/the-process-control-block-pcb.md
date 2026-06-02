# The Process Control Block (PCB) and What It Stores

The operating system must track every live process so it can schedule them, respond to interrupts, and resume them accurately. It does this through a kernel data structure called the **Process Control Block (PCB)** — sometimes called a **task_struct** (Linux) or **EPROCESS** (Windows).

Think of the PCB as the OS's "filing card" for a process: every piece of information the kernel needs to manage, suspend, and resume that process is stored here.

## What the PCB Contains

### 1. Process Identification
- **PID** (Process ID) — unique integer assigned at creation.
- **PPID** (Parent PID) — PID of the process that spawned this one.
- **UID / GID** — user and group identifiers governing access permissions.
- **Session ID, process group ID** — for job control in shells.

### 2. CPU State (Register Context)
When a context switch occurs, the kernel saves the contents of all CPU registers into the PCB so the process can resume exactly where it left off:

- **Program Counter (PC / RIP)** — address of the next instruction to execute.
- **Stack Pointer (SP / RSP)** — top of the current stack.
- **General-purpose registers** (RAX, RBX, … on x86-64).
- **Flags register** — condition codes (zero, carry, overflow, etc.).
- **Floating-point / SIMD state** (saved separately via `fxsave`/`xsave`).

### 3. Process State
A field indicating the current scheduling state: **Running**, **Ready**, **Waiting**, **Zombie**, or **Stopped**. The scheduler reads this to decide which process to pick next.

### 4. Memory Management Information
- Base and limit (or page-table pointer — `CR3` on x86) for the virtual address space.
- Memory map: location of text, data, heap, stack.
- Swap area pointer (if the process is paged out).

### 5. I/O and File Information
- **File descriptor table** — an array of pointers to open-file structures (stdin, stdout, stderr, and any other open files or sockets).
- Current working directory.
- Root directory (for chroot jails).
- `umask` — default permission mask for new files.

### 6. Accounting and Statistics
- CPU time used (user mode + kernel mode).
- Real time elapsed (wall clock).
- Number of page faults.
- Nice value / scheduling priority.

### 7. Signal Information
- **Pending signals** — bitmask of signals sent but not yet handled.
- **Signal mask** — signals currently blocked.
- **Signal handlers** — table of function pointers for each signal number.

## Simplified PCB Structure in C

```c
// Conceptual (not actual Linux source)
typedef struct PCB {
    pid_t   pid;
    pid_t   ppid;
    int     state;          // RUNNING, READY, WAITING, ZOMBIE ...

    /* CPU context — saved on context switch */
    uint64_t rip;           // instruction pointer
    uint64_t rsp;           // stack pointer
    uint64_t rax, rbx, rcx, rdx;
    uint64_t rsi, rdi, rbp;
    uint64_t eflags;

    /* Memory */
    uint64_t *page_table;   // physical address of PML4 (x86-64)
    size_t   mem_limit;

    /* File system */
    struct file *fd_table[OPEN_MAX];
    struct dentry *cwd;

    /* Scheduling */
    int      priority;
    uint64_t cpu_time_us;

    /* Signals */
    sigset_t pending;
    sigset_t blocked;
    sighandler_t sig_handlers[NSIG];

    /* Linkage */
    struct PCB *next;       // linked list / run-queue pointer
} PCB;
```

## Where the PCB Lives

The PCB resides in **kernel memory**, which is inaccessible to the process itself (user space cannot read or modify it). On Linux, each process also has a small **kernel stack** (~8 KB) used while running in kernel mode on behalf of that process; a pointer to the `task_struct` is stored at the bottom of this stack for fast access.

## PCB Lifecycle

| Event | PCB action |
|-------|-----------|
| `fork()` | New PCB allocated and mostly copied from parent |
| Context switch out | CPU registers saved into PCB |
| Context switch in | CPU registers restored from PCB |
| `exit()` | PCB moved to Zombie state; resources freed (but PCB kept until parent calls `wait()`) |
| `wait()` by parent | PCB fully deallocated |

## Common Pitfalls

- **The PCB is not the process itself**: It is metadata. The actual code and data live in the address space.
- **Register context is incomplete without the FPU state**: Forgetting to save/restore `xsave` state causes subtle floating-point bugs in context switches — a real historical bug in early SMP kernels.
- **PID 1 is special**: On Linux, PID 1 is `init`/`systemd`. If it exits, the kernel panics. Its PCB is never freed during normal operation.

> **Interview answer:** The PCB (Process Control Block) is a kernel data structure that stores everything the OS needs to manage a process: its PID, CPU register context (so the process can be resumed after a context switch), memory map, file descriptor table, signal state, and scheduling priority.
