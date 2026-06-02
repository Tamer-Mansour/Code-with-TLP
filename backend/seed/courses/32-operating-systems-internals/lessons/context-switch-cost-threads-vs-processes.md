# Why Thread Switches Are Cheaper Than Process Switches

Context switches are not all equal. Switching between two threads of the same process is significantly cheaper than switching between two processes. Understanding the difference requires knowing what the kernel must do in each case.

## What a Context Switch Must Do

Every context switch, at minimum, must:

1. Save the outgoing entity's CPU register state (PC, SP, general-purpose regs, EFLAGS/CPSR).
2. Update the scheduler's data structures (state → runnable/blocked).
3. Select the next entity to run.
4. Restore the incoming entity's register state.
5. Transfer control.

That baseline is the same for both thread and process switches.

## The Extra Cost of a Process Switch: Address Space

When switching between two **different processes**, the kernel must also:

- **Load a new page table base** (`cr3` on x86-64 / `TTBR0` on ARM). This is a single register write, but it triggers the next bullet.
- **Flush the TLB.** The Translation Lookaside Buffer caches virtual-to-physical mappings. After a process switch those mappings are wrong — the new process has a different address space. A full TLB flush forces every subsequent memory access to walk the page tables again until the TLB is refilled.
- **Evict cache lines (indirectly).** The new process will access different memory, causing its data to be loaded into L1/L2 cache while the old process's data is evicted. This "cold cache" penalty can dominate the switch cost.

```
Thread switch:
  save regs → pick next thread → restore regs → run
  TLB: UNTOUCHED (same page table base — cr3 unchanged)
  Cache: mostly warm (shared code and heap)

Process switch:
  save regs → load new cr3 → TLB flush → restore regs → run
  TLB: COLD on every access until refilled
  Cache: cold for the new process's working set
```

## TLB Cost Is the Dominant Factor

A TLB miss causes the MMU to walk the 4-level page table — 4 memory accesses per miss at ~50–100 ns each. In a working set of 1000 pages, a full TLB flush causes 1000 misses × ~200 ns ≈ 200 µs of extra latency just for TLB refill.

Hardware mitigations include **PCID (Process-Context Identifiers)** on x86-64: the CPU tags TLB entries with a 12-bit PCID. If the returning process's PCID is still in the TLB, its entries are reused without a full flush. Linux uses PCID since kernel 4.14.

```bash
# Check PCID support
grep pcid /proc/cpuinfo | head -1
# flags: ... pcid ...
```

## Quantified Comparison (Typical x86-64 Linux)

| Switch type | Kernel overhead | TLB cost | Total (approx) |
|---|---|---|---|
| Thread (same process) | ~1–2 µs | ~0 (cr3 unchanged) | ~1–3 µs |
| Process (PCID hit) | ~2–3 µs | Partial refill | ~3–8 µs |
| Process (full flush) | ~2–3 µs | ~50–200 µs | ~50–200 µs |

These numbers vary with hardware, working set, and kernel version.

## Kernel vs User Thread Switch Cost

Even within threads, kernel threads cost more than user-level coroutine switches:

```
User-level coroutine switch (no syscall):
  ~50–200 ns — just swap stack pointer and a handful of registers

Kernel thread switch (timer interrupt → kernel → schedule → iret):
  ~1–3 µs — mode switch in + scheduler path + mode switch out
```

## Practical Consequence

Applications that switch between many short-lived tasks benefit from:

1. **Thread pools over process pools** — avoids TLB flushing.
2. **Coroutines / async over threads** — avoids kernel mode transitions.
3. **NUMA-aware scheduling** — avoid migrating threads across sockets (cold L3 cache + NUMA penalty).

```python
# Python: switching coroutines is cheaper than switching threads
import asyncio

async def task_a():
    await asyncio.sleep(0)   # yield to event loop — no syscall, no TLB flush

async def task_b():
    await asyncio.sleep(0)

asyncio.run(asyncio.gather(task_a(), task_b()))
```

## Common Pitfall

Candidates say "thread switches don't touch the TLB" and think that fully explains the savings. The fuller picture includes cache warmth: threads share code and heap, so switching threads keeps more L1/L2 data hot. Process switches cold-start the cache for the new working set — that indirect cost often exceeds the direct TLB flush cost.

> **Interview answer:** A thread context switch saves and restores registers but leaves the page table base register (`cr3`) unchanged, so the TLB remains valid and cache data stays warm. A process context switch must load a new `cr3`, flushing (or partially invalidating) the TLB and evicting the old process's cache lines, making subsequent memory accesses much slower. The TLB and cache cold-start penalty is the primary reason process switches are 10–100x more expensive than thread switches.
