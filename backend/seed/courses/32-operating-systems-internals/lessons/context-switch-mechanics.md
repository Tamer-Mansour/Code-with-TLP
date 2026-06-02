# Context Switch Mechanics: Saving and Restoring State

A **context switch** is the mechanism by which the OS removes one process from the CPU and places another. From each process's perspective, it ran continuously — the illusion of dedicated hardware. Under the hood, the kernel performs a precise save-and-restore dance that must preserve every aspect of the outgoing process's execution state.

## When Does a Context Switch Happen?

- **Timer interrupt (preemption)**: A hardware timer fires at regular intervals (typically every 1–10 ms). The interrupt handler checks if the running process has used its time slice and, if so, triggers a switch.
- **Voluntary yield / blocking system call**: The process calls `sleep()`, `read()` (blocking), `wait()`, or tries to acquire a locked mutex. It voluntarily gives up the CPU.
- **I/O completion**: A device interrupt wakes a waiting process. If the newly-ready process has higher priority, the current process may be preempted immediately.
- **Higher-priority process becomes ready**: In preemptive schedulers, a `fork()` or waking a high-priority thread can immediately displace the running process.

## The Mechanics Step-by-Step

```
CPU is running Process A
        │
        ▼  (timer interrupt fires)
┌───────────────────────────────┐
│ 1. Hardware saves minimal     │  ← CPU automatically pushes RIP,
│    state (interrupt frame)    │    RSP, RFLAGS onto the kernel stack
└──────────────┬────────────────┘
               │
               ▼
┌───────────────────────────────┐
│ 2. Kernel interrupt handler   │  ← switches to kernel stack of Process A
│    saves full CPU context     │    saves all GPRs into PCB_A
│    into PCB_A                 │
└──────────────┬────────────────┘
               │
               ▼
┌───────────────────────────────┐
│ 3. Scheduler runs             │  ← picks next process (Process B)
│    (pick_next_task)           │    from ready queue
└──────────────┬────────────────┘
               │
               ▼
┌───────────────────────────────┐
│ 4. Kernel restores context    │  ← loads all GPRs from PCB_B
│    from PCB_B                 │    switches to Process B's kernel stack
└──────────────┬────────────────┘
               │
               ▼
┌───────────────────────────────┐
│ 5. Switch address space       │  ← loads Process B's page table root
│    (CR3 load on x86-64)       │    flushes TLB (or uses tagged TLB if ASID supported)
└──────────────┬────────────────┘
               │
               ▼
┌───────────────────────────────┐
│ 6. iret / sysretq             │  ← returns to Process B's user-space RIP
│    returns to user space      │    Process B resumes exactly where it left off
└───────────────────────────────┘
CPU is now running Process B
```

## What Gets Saved

```c
// Simplified context struct (x86-64)
struct cpu_context {
    uint64_t rip;      // instruction pointer
    uint64_t rsp;      // stack pointer
    uint64_t rflags;   // condition flags
    uint64_t rax, rbx, rcx, rdx;
    uint64_t rsi, rdi, rbp;
    uint64_t r8,  r9,  r10, r11;
    uint64_t r12, r13, r14, r15;
    uint64_t cs, ss;   // segment selectors
    // FPU/SSE state saved separately (fxsave area)
};
```

On x86-64, the hardware automatically pushes `RIP`, `RSP`, `RFLAGS`, `CS`, and `SS` onto the kernel stack on interrupt entry. The kernel saves the remaining general-purpose registers manually in assembly before calling C code.

## The TLB Flush Problem

Each process has a distinct virtual-to-physical address mapping. When `CR3` is loaded with the new process's page-table root, the CPU must not use stale Translation Lookaside Buffer (TLB) entries from the previous process.

- **Naive approach**: Flush the entire TLB on every context switch. Simple but costly on workloads with many short processes.
- **ASID (Address Space ID)**: Modern CPUs (ARM, x86 via PCID) tag TLB entries with a per-process ID. Entries from process A don't contaminate process B's lookups — no flush needed unless ASIDs are exhausted.

## The Cost of a Context Switch

A context switch is not free. Typical overheads include:

| Component | Approximate cost |
|-----------|-----------------|
| Save/restore registers | ~100 ns |
| TLB flush (without PCID) | ~1–5 µs (re-fill cost) |
| Cache warm-up after switch | ~10–100 µs (cold cache) |
| Total (rough) | ~1–10 µs |

This is why having thousands of threads context-switching rapidly (thread thrashing) degrades throughput. Modern systems use cooperative techniques (async I/O, coroutines, io_uring) to reduce switch frequency.

## Voluntary vs. Involuntary Switches

```bash
# See context switch counts for a process (Linux)
cat /proc/<pid>/status | grep ctxt_switches
# voluntary_ctxt_switches:   blocking calls (I/O, sleep, mutex)
# nonvoluntary_ctxt_switches: preemption by scheduler
```

A high `nonvoluntary_ctxt_switches` count suggests the process is CPU-bound and frequently preempted. A high `voluntary_ctxt_switches` count suggests I/O-bound behaviour.

## Common Pitfalls

- **Forgetting FPU state**: The floating-point and SIMD register files are large (512+ bytes for AVX-512). Saving them on every context switch is expensive, so many kernels use lazy FPU switching — only saving when a different process actually uses FP instructions.
- **Assuming instant switch**: Context switches take microseconds. Real-time systems must budget for this in worst-case execution time (WCET) analysis.
- **User-space "context switches" are cheaper**: Coroutines and fibers switch context entirely in user space, avoiding the kernel mode transition and often the TLB flush, making them 10–100x faster than OS context switches.

> **Interview answer:** A context switch saves the outgoing process's CPU registers (including the instruction pointer and stack pointer) into its PCB, then restores the incoming process's saved registers from its PCB, and finally switches the page table pointer so the new process's virtual address space is active.
