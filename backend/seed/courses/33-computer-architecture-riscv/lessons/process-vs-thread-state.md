# Process and Thread State on the Hardware

From the hardware's perspective, the CPU knows only one thing: registers and memory. The OS abstracts this into processes and threads. Understanding what state belongs to each level — and which registers are shared versus private — clarifies why threads are "cheaper" than processes and why context switches have different costs.

## Process vs. Thread: What the Hardware Sees

| Concept | Hardware Reality |
|---------|----------------|
| Process | A distinct virtual address space (unique `satp` value) + one or more threads |
| Thread | One set of CPU registers (PC, integer, FP) running in a shared address space |

Switching between threads in the **same** process only requires swapping registers — `satp` stays the same, so the TLB does not need a full flush. Switching between processes requires loading a new `satp` and flushing stale TLB entries with `sfence.vma`.

## Per-Thread Hardware State

Every schedulable thread must have its own private copy of:

- **Program counter** (`sepc` at trap time, or `ra`/`pc` inside `swtch`)
- **Stack pointer** (`sp`) — each thread has its own user-mode and kernel-mode stack
- **All 32 integer registers** (`x0`–`x31`)
- **All 32 FP registers** (`f0`–`f31`) and `fcsr` if the FP extension is used
- **CSR snapshot**: `sstatus`, `sepc`, `scause` captured at trap entry

```c
// xv6-riscv trapframe structure (one per thread)
struct trapframe {
    uint64 kernel_satp;   // kernel page table
    uint64 kernel_sp;     // top of kernel stack for this thread
    uint64 kernel_trap;   // address of usertrap()
    uint64 epc;           // saved user program counter
    uint64 kernel_hartid; // saved kernel tp
    uint64 ra;
    uint64 sp;
    // ... x3 through x31
    uint64 t6;
};
```

## Per-Process (Shared) State

Within a process, all threads share:

- **Virtual address space** (`satp` / page table root)
- **File descriptor table**
- **Signal handlers**
- **Memory-mapped regions** (heap, text, data, mmap)

When two threads in the same process run on two different harts simultaneously, they share the page table — a write by one thread is immediately visible to the other. This is why thread synchronization primitives are necessary.

## The RISC-V `tp` Register

RISC-V designates `x4` (`tp` — thread pointer) as a convention for pointing to thread-local storage (TLS). The OS sets `tp` when it first schedules a thread, and the linker places thread-local variables (declared `__thread` in C) at offsets from `tp`. The hardware does not enforce this — it is an ABI convention.

```c
__thread int errno_val;   // per-thread, accessed via tp-relative addressing
```

In xv6-riscv, `tp` holds the hart ID in the kernel, which threads use to index per-CPU data structures without locks.

## Thread States and the Scheduler

A thread can be in one of these states at any time:

| State | Description |
|-------|-------------|
| RUNNING | Executing on a hart right now |
| RUNNABLE | In the ready queue, waiting for a hart |
| SLEEPING | Waiting for an event (I/O, lock, timer) |
| ZOMBIE | Exited, waiting for parent to `wait()` |

The OS tracks these states in software (a `state` field in the PCB/TCB struct). The hardware has no notion of "sleeping" — from its view, a sleeping thread simply is not loaded into any hart's registers.

## Common Pitfalls

- Assuming `sfence.vma` is not needed between threads in the same process — it is still needed if page table entries are modified (e.g., on `mmap`).
- Forgetting that signal delivery to a multi-threaded process requires choosing one thread — the hardware cannot deliver a signal; the kernel must select a thread in RUNNABLE or RUNNING state.
- Thread-local errno: in single-threaded C, `errno` is a global; in multi-threaded programs it must be `__thread` or accessed via a function — mixing them is a data race.

> **Interview answer:** From the hardware's view, a thread is a full set of CPU registers (PC + 32 integers + 32 FP) and a kernel stack; threads in the same process share one `satp` value so intra-process context switches skip the TLB flush, making them faster than inter-process switches.
