# Context Switching

A **context switch** is the mechanism by which the OS saves the complete state of one process (or thread) and restores the complete state of another, handing the CPU to the new process. It is the fundamental heartbeat of multitasking — without it, only one program could run at a time.

## What Gets Saved and Restored

The **context** of a process is everything needed to resume it exactly where it left off, as if it had never been paused:

```
Saved/Restored per thread during a context switch:
┌─────────────────────────────────────────────┐
│ General-purpose registers                   │
│   x86-64: rax, rbx, rcx, rdx, rsi, rdi,    │
│           rbp, r8–r15 (16 registers total)  │
│ Program counter (rip)    ← next instruction │
│ Stack pointer (rsp)      ← top of the stack │
│ Status/flags (rflags)    ← condition codes  │
│ Segment registers (cs, ss, fs, gs)          │
│ x87 FPU / SSE state (if used by process)   │
│   (lazy save — only if process used floats) │
└─────────────────────────────────────────────┘
Plus, in the PCB (not in registers):
┌─────────────────────────────────────────────┐
│ Page table base (CR3 on x86)               │
│   ← points to this process's page tables   │
│ Open file descriptor table                  │
│ Signal masks                                │
│ Virtual memory area list (VMA)             │
└─────────────────────────────────────────────┘
```

## Steps of a Context Switch: Detailed Trace

```
Scenario: Process A is running, a timer interrupt fires, scheduler picks Process B.

1. Timer interrupt arrives:
   CPU hardware automatically:
   a. Saves A's rip (next instruction) and rsp onto A's kernel stack
   b. Saves rflags onto A's kernel stack
   c. Loads the interrupt handler address from IDT[timer_vector]
   d. Switches from ring 3 → ring 0

2. Timer interrupt handler runs in kernel mode:
   a. Acknowledges the interrupt to the PIC/APIC
   b. Increments system tick counter (jiffies in Linux)
   c. Calls the scheduler: scheduler()

3. Scheduler (schedule() in Linux):
   a. Checks if current process needs preemption (quantum expired?)
   b. Calls context_switch(prev=A, next=B):

4. context_switch(A → B):
   a. switch_mm(A, B):
      - Load B's page table base address into CR3
      - This flushes the TLB (unless ASID/PCID is used)
   b. switch_to(A, B):
      - Save A's remaining registers (general-purpose, FPU state) into A's PCB
      - Load B's registers from B's PCB
      - Load B's kernel stack pointer
      - Jump to B's saved rip (B resumes from wherever it was)

5. Process B is now RUNNING:
   - It sees its own registers and memory (via page tables)
   - Interrupts are re-enabled
   - B continues executing as if nothing happened
```

From B's perspective, it just "woke up." It has no way to tell it was ever paused — unless it measures wall clock time.

## The Cost of a Context Switch

Context switches are not free:

| Cost Component | Typical Overhead | Notes |
|----------------|-----------------|-------|
| Save/restore CPU registers | ~50–200 ns | ~16 integer registers + flags |
| Save/restore FPU/SIMD state | ~100–400 ns | 512 bytes for AVX-512 state; lazy save avoids this if unused |
| CR3 write + TLB flush | ~100 ns – 10 µs | Large if working set is hot; mitigated by PCID on modern x86 |
| Cache cold-start (cache miss penalty) | 0 – several ms | Main cost; B's data is cold in L1/L2 |
| Kernel bookkeeping | ~100 ns | Update PCB timestamps, scheduler structures |

The **cache warm-up** cost dominates for long-running CPU-intensive processes. Switching away from a process that had 16 MB of L2 cache hot means the next time it runs, it re-fetches everything from L3 or RAM.

**PCID (Process-Context Identifiers)** on modern x86: each process has a 12-bit PCID. The TLB stores entries tagged with the PCID; a CR3 load with a new PCID does not flush entries from other PCIDs. This eliminates most TLB flush costs on process switches. Linux uses PCID since kernel 4.14.

**Thread switches within the same process:** No CR3 change → no TLB flush → 2–5× cheaper than process switches. Same page tables; only register state changes.

## Voluntary vs. Involuntary Context Switches

| Type | Trigger | Mechanism | Example |
|------|---------|-----------|---------|
| **Voluntary (yield)** | Process blocks or explicitly yields | Process calls `schedule()` | `sleep()`, blocking `read()` on empty socket, `mutex_lock()` when lock is held |
| **Involuntary (preemption)** | Timer interrupt; higher-priority process wakes | Forced by the kernel | Running process's quantum expires; real-time process unblocks |

**Non-preemptive (cooperative) scheduling** requires processes to voluntarily yield. If any process enters an infinite loop, the system hangs. Used in early Windows 3.x and classic Mac OS — notorious for "spinning beachball" hangs when a program froze.

**Preemptive scheduling** (Linux, macOS, Windows since NT) uses a hardware timer interrupt to force context switches. Even a runaway infinite loop gets preempted after its quantum.

## Measuring Context Switches

```bash
# Per-process: voluntary and involuntary switches since process start
cat /proc/<pid>/status | grep ctxt
# voluntary_ctxt_switches:     1245
# nonvoluntary_ctxt_switches:   87

# System-wide context switches per second (cs column)
vmstat 1 5
# procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
#  r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
#  3  0      0 1024000  50000 200000    0    0    10     5  500 2500 40 10 49  1  0
#                                                            ^^^^ 2500 cs/sec

# Fine-grained context switch count for a command
perf stat -e context-switches ls /tmp
```

A lightly-loaded desktop system might do 500–2,000 context switches per second. A heavily loaded server can do 100,000+ per second.

## The Scheduler vs. The Dispatcher

The context switch mechanism is the "how." The scheduler is the "who and when":

```
┌────────────────────────────┐  ┌────────────────────────────────┐
│ Scheduler (Policy)         │  │ Dispatcher (Mechanism)         │
│                            │  │                                │
│ • Decides WHICH process    │→ │ • Saves outgoing registers     │
│   to run next              │  │ • Updates page table (CR3)     │
│ • Uses: FCFS, RR, CFS, etc │  │ • Loads incoming registers     │
│ • Considers: priority,     │  │ • Grants CPU to new process    │
│   vruntime, deadlines      │  │ • Measured in microseconds     │
└────────────────────────────┘  └────────────────────────────────┘
```

The **dispatch latency** is the time between the scheduler deciding to switch and the new process actually running. Linux aims for < 1 ms dispatch latency for interactive processes; the `PREEMPT_RT` patch reduces it to < 100 µs for real-time workloads (used in medical devices, audio production).

## Context Switch in Multi-Core Systems

On a symmetric multiprocessing (SMP) system, each CPU core has its own:
- Current process (the one it's currently running)
- Kernel stack (for interrupt handlers)
- TLB (partially flushed on CR3 change)
- L1 and L2 caches (per core)

Context switching on one core does not affect other cores. However, a process that migrates between cores loses its L1/L2 cache warmth — the scheduler's **CPU affinity** logic tries to keep processes on the same core when possible.

**Cache-coherent NUMA (Non-Uniform Memory Access):** On multi-socket servers, memory access to a remote socket's DRAM takes 2–3× longer. Linux's NUMA-aware scheduler keeps processes on the NUMA node where their memory lives.

## Key Takeaways

- A context switch saves all CPU registers + page table info for the outgoing process and restores them for the incoming process.
- On x86-64, the largest single cost is typically a **TLB flush** when switching between different address spaces (different CR3 values); **PCID** mitigates this.
- **Thread** context switches within the same process skip the CR3 change and are 2–5× cheaper.
- Linux uses **preemptive scheduling** — a timer interrupt can forcibly remove any process from the CPU.
- The **scheduler** (policy: who runs next) is distinct from the **dispatcher** (mechanism: how to hand over the CPU).
- **Dispatch latency** (decision to running) targets < 1 ms for desktop Linux; the `PREEMPT_RT` patch achieves < 100 µs for real-time systems.
