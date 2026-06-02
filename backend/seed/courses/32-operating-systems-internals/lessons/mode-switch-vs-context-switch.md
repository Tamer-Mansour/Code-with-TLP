# Mode Switch vs Context Switch: Don't Confuse Them

These two terms sound similar and often happen together, but they are fundamentally different events. Mixing them up in an interview is a red flag — here is exactly what each one is and how they relate.

## Mode Switch: Changing CPU Privilege Level

A **mode switch** (also called a **privilege level transition**) is when the CPU changes between user mode (Ring 3) and kernel mode (Ring 0).

- It involves **no change of process or thread identity**.
- The same thread continues running — just at a different privilege level.
- Triggered by: system calls (`SYSCALL`/`SYSENTER`), hardware interrupts, software exceptions.
- Relatively **cheap**: saves a small set of registers, switches stacks, changes CPL.

```
Thread A (user mode)
   │
   │  write(fd, buf, len)   ← system call
   ▼
Thread A (kernel mode)     ← same thread, now in Ring 0
   │  [kernel does I/O]
   │  sysretq
   ▼
Thread A (user mode)       ← back to Ring 3, same process
```

## Context Switch: Changing Which Thread Runs

A **context switch** is when the CPU stops running one thread and starts running a different one. It may occur between processes or between threads of the same process.

- It involves **saving and restoring the full CPU state** of one thread and loading another's.
- Triggered by: the scheduler preempting a thread (timer interrupt), a thread blocking on I/O, or a thread voluntarily yielding.
- More **expensive** than a mode switch: saves/restores general-purpose registers, FPU/SIMD state, stack pointer, instruction pointer, and (for a process switch) the page table base register (CR3), which flushes the TLB.

```
Thread A running
   │
   │  Timer interrupt → kernel scheduler runs
   ▼
save A's registers to A's kernel stack / PCB
load B's registers from B's kernel stack / PCB
   │
   ▼
Thread B running
```

## Side-by-Side Comparison

| Property | Mode Switch | Context Switch |
|---|---|---|
| Thread identity changes | No | Yes |
| Process identity changes | No | Sometimes (if switching across processes) |
| Saves full register file | No (minimal set) | Yes (all user registers) |
| Switches stack | Yes (user → kernel stack) | Yes (to next thread's kernel or user stack) |
| Switches page table (CR3) | No (kernel mapped in same table) | Yes, when switching processes |
| TLB flush (without PCID) | No | Yes (process switch) |
| Typical cost | ~100 ns | ~1–10 µs |

## They Often Happen Together — But Not Always

- A system call causes a **mode switch** but typically no context switch (unless the syscall blocks).
- A timer interrupt causes a **mode switch** (user → kernel for the interrupt handler) and then **may or may not** cause a context switch (the scheduler decides).
- A voluntary `sleep()` causes a mode switch, then a context switch (the thread blocks, another runs).
- A context switch between two kernel threads involves no mode switch (both are already in kernel mode).

## Worked Scenario

```
Time →

Process A (user)  ──syscall──▶  A (kernel)  ──read blocks──▶  [B runs]  ──B exits──▶  A (kernel)  ──sysretq──▶  A (user)
                  mode switch                context switch               context switch              mode switch
```

1. `A` calls `read()` — **mode switch** only.
2. `read()` blocks waiting for disk — **context switch** from A to B.
3. B finishes — **context switch** from B back to A (kernel mode).
4. `read()` returns — **mode switch** from kernel to user.

## Common Pitfalls

- **"Every system call causes a context switch"**: False. Most syscalls return without ever switching processes.
- **"Context switches only happen between processes"**: False. Threads within the same process are context-switched too.
- **"Mode switches are free"**: Not free. With KPTI, they now include a page-table swap. Still cheaper than a full context switch, but measurable.

## Interview Answer

> **Q: What is the difference between a mode switch and a context switch?**
>
> **Interview answer:** A mode switch changes the CPU's privilege level between user mode and kernel mode while keeping the same thread running. A context switch replaces the running thread entirely, saving its CPU state and loading another thread's state. A context switch always goes through kernel mode, but a mode switch does not imply a context switch.
