# Full-Stack OS Interview Integration: Tying It Together

Senior OS and embedded systems interviews do not test individual topics in isolation. They test whether you can trace a single operation — a system call, an interrupt, a page fault — all the way from user-space source code down to the physics of the hardware bus cycle. This lesson maps the full vertical stack and shows how to connect every layer in a coherent interview answer.

## The Full Stack, Layer by Layer

```
User process (C code)
       │  write(fd, buf, n)
       ▼
Syscall interface (RISC-V ecall / x86 syscall)
       │  trap into kernel, switch to kernel stack
       ▼
VFS layer (sys_write → vfs_write)
       │  filesystem abstraction
       ▼
File system driver (ext4, FAT, tmpfs …)
       │  block I/O requests
       ▼
Block layer (I/O scheduler, bio)
       │
       ▼
Device driver (MMC, NVMe, UART …)
       │  MMIO register writes
       ▼
Interrupt controller (PLIC / GIC)
       │  IRQ line → CPU
       ▼
MMU / TLB (virtual → physical address translation)
       │
       ▼
DRAM / Peripheral (physical hardware)
```

A strong interview answer traces this chain end-to-end for the scenario the interviewer names.

## Connecting the Topics in This Course

| Module topic | How it appears in the full stack |
|---|---|
| System calls & traps | Transition from user to kernel at ecall |
| Virtual memory & MMU | Every pointer dereference triggers a TLB lookup |
| Page tables | Walk happens on TLB miss; page fault on invalid entry |
| Interrupt controller | Peripheral completion IRQ routed through PLIC/GIC |
| Scheduler & context switch | User process blocked on I/O; scheduler picks next runnable |
| Locking & synchronization | Driver ISR and process share a buffer; spinlock protects it |
| Virtual prototype / ISS | Entire stack runs on a virtual prototype before silicon exists |

## Framing a Full-Stack Answer

A reliable interview framework: **Trigger → Trap → Kernel Service → HW Interaction → Completion → Return**.

Example: "Walk me through what happens when a user process writes to a serial port."

1. **Trigger** — `write(fd, buf, 4)` in user space.
2. **Trap** — `ecall` raises an exception; CPU jumps to trap vector, switches privilege level.
3. **Kernel service** — VFS dispatches to the UART driver's `write` method.
4. **HW interaction** — driver polls or waits for TX-empty, then writes byte to THR MMIO register.
5. **Completion** — UART asserts TX-empty interrupt; PLIC forwards to CPU; ISR wakes the blocked process.
6. **Return** — scheduler resumes the process; `write()` returns.

> **Interview answer:** I trace the call from the user-space API through the syscall trap, kernel VFS and driver layers, MMIO register writes, interrupt acknowledgment, and scheduler wake-up — every layer is visible and reproducible on a virtual prototype.

## Phrasing Crisp One-Liners

Interviewers often want a quick definition before asking for depth. Memorize these:

- **Virtual memory** — each process has its own address space; the MMU translates virtual to physical using page tables.
- **Page fault** — a TLB/page table miss that traps into the kernel; resolved by mapping a physical frame or killing the process.
- **Interrupt** — an asynchronous hardware signal that preempts the CPU and vectors to a registered ISR.
- **Context switch** — saving one thread's register state and restoring another's; the MMU switches address spaces for process switches.
- **Virtual prototype** — a software model of a SoC that runs real firmware/OS before physical silicon is available.
- **ISS** — the CPU component of a virtual prototype; decodes and executes target instructions on the host.

## Common Interview Traps

- **"What is the difference between a trap and an interrupt?"** — Traps are synchronous (caused by the current instruction: ecall, page fault, illegal instruction). Interrupts are asynchronous (caused by external hardware).
- **"Where does the page table walk happen?"** — In hardware (the MMU's page table walker), not in kernel software. The kernel only runs on a TLB miss that the hardware cannot resolve (page fault).
- **"How does the kernel know which interrupt fired?"** — It reads the PLIC claim register (RISC-V) or GIC IAR (Arm) to get the source ID, then dispatches to the registered handler.
- **"Why does the kernel disable interrupts during a spinlock?"** — To prevent a local interrupt handler from trying to acquire the same lock on the same CPU, causing a deadlock.

## Building Interview Fluency

Practice narrating the full stack for five scenarios:

1. A process reads from a file on NVMe.
2. A timer interrupt fires and the scheduler context-switches.
3. A process accesses an unmapped page (demand paging).
4. A DMA transfer completes and wakes a blocked driver thread.
5. A kernel module is loaded and probes a device.

Each scenario exercises a different cross-section of the stack. Fluency comes from tracing the same path many times until the connections feel natural.
