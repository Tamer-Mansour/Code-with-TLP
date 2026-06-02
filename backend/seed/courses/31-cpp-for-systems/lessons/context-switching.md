# Context Switching and Its Cost

A context switch is the mechanism by which the OS saves the state of the current running task and restores the state of another, allowing multiple processes or threads to share a single CPU.

## What Gets Saved and Restored

When the OS switches from Process A to Process B, it must save every piece of CPU state that Process A was using:

**Saved in the Process Control Block (PCB):**

- **Program counter (PC / RIP)** — next instruction to execute.
- **General-purpose registers** (RAX, RBX, …, R15 on x86-64).
- **Stack pointer (RSP)** and frame pointer (RBP).
- **CPU flags** (RFLAGS) — carry, zero, overflow, etc.
- **Segment registers** (CS, DS, SS in protected mode).
- **FPU / SIMD state** (x87, SSE, AVX registers — saved lazily on many kernels).

**Implicit costs beyond registers:**

- **TLB flush** — virtual address mappings are process-specific; switching processes invalidates TLB entries (unless the CPU supports ASIDs/PCIDs).
- **Cache pollution** — Process B's working set displaces Process A's cache lines; both processes pay cold-cache penalties after the switch.
- **Pipeline flush** — the CPU pipeline is drained at the trap boundary.

> **Interview answer:** A context switch saves and restores CPU registers and the PC, but the hidden costs — TLB invalidation and cache eviction — often dominate the measured overhead.

## How a Context Switch Is Triggered

1. **Timer interrupt (preemptive scheduling):** the hardware timer fires at each quantum boundary, generating an interrupt. The CPU automatically saves the PC and flags, then jumps to the kernel's interrupt handler.
2. **Voluntary yield:** the process calls `sleep()`, `read()`, `mutex_lock()`, or similar blocking syscalls, giving up the CPU explicitly.
3. **Higher-priority process becomes ready:** an interrupt unblocks a high-priority process; the kernel preempts the current one immediately.

## Measuring Context-Switch Time

On a modern x86-64 CPU, a process context switch costs roughly **1–10 µs** depending on:

- Whether the TLB needs flushing (x86-64 PCIDs reduce this).
- Working set size (cache footprint of the departing process).
- Kernel complexity of the scheduler.

Thread context switches (within the same process) are cheaper because:
- Address space is shared → no TLB flush.
- Fewer registers to save if using POSIX threads (kernel reuses the page tables).

A rough rule of thumb: thread switch ≈ 0.1–2 µs; process switch ≈ 1–10 µs.

## The Cost in Practice: Benchmark Sketch

```cpp
#include <pthread.h>
#include <cstdio>
#include <ctime>

// Measure round-trip ping-pong between two threads via a shared flag
volatile int flag = 0;

void* thread_fn(void*) {
    for (int i = 0; i < 100000; i++) {
        while (flag != 1);   // spin-wait (bad in production, fine for measurement)
        flag = 0;
    }
    return nullptr;
}

int main() {
    pthread_t t;
    pthread_create(&t, nullptr, thread_fn, nullptr);

    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (int i = 0; i < 100000; i++) {
        flag = 1;
        while (flag != 0);
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);

    pthread_join(t, nullptr);
    long ns = (t1.tv_sec - t0.tv_sec) * 1000000000L
            + (t1.tv_nsec - t0.tv_nsec);
    printf("Round-trip: %.1f ns\n", (double)ns / 100000);
    return 0;
}
```

## Voluntary vs. Involuntary Switches

| Type | Cause | Example |
|---|---|---|
| **Voluntary** | Process blocks on I/O or lock | `read()`, `mutex_lock()` |
| **Involuntary** | Timer expires or higher-priority process wakes | Scheduler preemption |

You can observe both with:

```bash
# On Linux, per-process context switch counts
cat /proc/<PID>/status | grep ctxt
# voluntary_ctxt_switches:    1234
# nonvoluntary_ctxt_switches: 56
```

## Reducing Context-Switch Overhead

- **CPU pinning** (`sched_setaffinity`) keeps a thread on one core, preserving cache state.
- **Large time quanta** reduce involuntary switches at the cost of response time.
- **Lock-free data structures** reduce voluntary switches from contention.
- **User-space threading (coroutines, fibers)** avoids kernel involvement entirely for cooperative multitasking — no kernel trap, no TLB flush.

## Common Pitfalls

- Assuming thread switches are free — they still require saving registers and can evict cache lines.
- Writing spin-loops instead of `futex`-based locks for long waits — wastes CPU during context switches.
- Over-threading: more threads than cores multiplies context-switch frequency without adding parallelism.
