# Interview Drill: Kernel Architecture Questions

This lesson covers the kernel architecture questions most commonly asked in systems engineering, OS internals, and senior software engineering interviews. For each question you will find the key points to hit and a crisp answer you could deliver in under 60 seconds.

---

## Q1. What is the difference between a monolithic kernel and a microkernel?

**Key points to hit:**
- Where code runs (kernel mode vs user space)
- IPC vs direct call
- Failure isolation consequences

**Crisp answer:** "A monolithic kernel runs all OS services — scheduling, memory, drivers, file systems — in a single privileged address space, so a driver bug can crash the system. A microkernel keeps only IPC, scheduling, and address-space management in kernel mode; everything else is a user-space server, so a driver crash is contained. The trade-off is IPC overhead versus isolation."

---

## Q2. Why don't most production systems use microkernels?

**Key points to hit:**
- Historical IPC overhead (Mach)
- Linux ecosystem maturity
- Practical driver support

**Crisp answer:** "Early microkernels like Mach were 10–100x slower than monolithic kernels for IPC-heavy workloads. Linux won the ecosystem war — it supports thousands more hardware devices. Modern microkernels (L4, seL4) have closed the performance gap, but the driver and software ecosystem hasn't caught up. QNX and seL4 win in embedded and safety-critical niches where reliability trumps breadth."

---

## Q3. What is a hybrid kernel? Give an example.

**Crisp answer:** "A hybrid kernel uses a small microkernel core for scheduling and IPC, but runs performance-critical services like device drivers in kernel mode rather than as separate user-space servers. Windows NT is the classic example — it has a tiny microkernel at the bottom and an 'Executive' layer in kernel mode. XNU (macOS/iOS) embeds the BSD subsystem directly in the Mach address space for performance while retaining Mach IPC for inter-subsystem communication."

---

## Q4. What is RCU and why does the Linux kernel use it?

**Key points to hit:**
- Read-Copy-Update pattern
- Zero-cost reads, delayed writer cleanup
- Grace period concept

**Crisp answer:** "RCU is a synchronization mechanism where readers pay no lock overhead — `rcu_read_lock()` just disables preemption. Writers make a copy of the data, modify it, atomically publish the new pointer, then wait for a grace period (all CPUs must pass through a quiescent state) before freeing the old version. Linux uses it for routing tables, module lists, and other heavily-read data structures because reads dominate and the occasional writer can afford to wait."

---

## Q5. What does "preemptible kernel" mean and why does it matter?

**Crisp answer:** "A preemptible kernel lets the scheduler interrupt a thread even while it is executing kernel code (a system call). Without it, a long-running syscall blocks all higher-priority tasks until it completes. With `CONFIG_PREEMPT`, the worst-case scheduling latency drops from 'duration of the longest syscall' to 'length of the longest non-preemptible critical section'. The PREEMPT_RT patch goes further, converting spinlocks to sleeping mutexes and making interrupt handlers preemptible, achieving sub-millisecond worst-case latency for real-time workloads."

---

## Q6. Why can't you use a mutex in an interrupt handler?

**Crisp answer:** "A mutex is a sleeping lock — if it's unavailable, the caller blocks and the scheduler runs another thread. Interrupt handlers run at interrupt priority with no associated process context; there's no thread to sleep and no way to reschedule from inside an ISR. You must use a spinlock, which busy-waits without sleeping. If you need to protect data shared between an IRQ handler and process context, you use `spin_lock_irqsave()` to also disable local interrupts and prevent a deadlock where the interrupt fires while the process holds the lock."

---

## Q7. What is seL4 and what does "formally verified" mean in that context?

**Crisp answer:** "seL4 is a microkernel (~9,000 lines of C) whose implementation has been machine-checked in Isabelle/HOL to be functionally correct — meaning the C code matches a high-level abstract specification — and free of memory safety violations. It also has proofs of integrity (user code can't corrupt kernel state) and confidentiality (no unauthorized information flows). This doesn't guarantee zero bugs in the hardware or compiler, but it's the strongest correctness assurance ever achieved for a real OS kernel, making seL4 the go-to choice for military avionics and safety-critical embedded systems."

---

## Q8. What is an exokernel? How does it differ from a microkernel?

**Crisp answer:** "An exokernel (MIT, 1995) does even less than a microkernel: it only securely multiplexes raw hardware resources — disk blocks, memory pages, CPU time — without providing any OS abstractions. Applications link a library OS that implements whatever abstractions they need. A microkernel still provides IPC and address-space abstractions; an exokernel exposes raw hardware with protection. The gain is that applications can tune every OS abstraction for their workload. The cost is that each application must implement its own (security-sensitive) OS logic."

---

## Quick-Reference Cheat Sheet

| Term | One-line definition |
|------|---------------------|
| Monolithic kernel | All OS services in one kernel-mode binary |
| Microkernel | Only IPC + scheduling in kernel mode |
| Hybrid kernel | Microkernel core + some services in kernel mode |
| Exokernel | Kernel only multiplexes hardware; apps supply abstractions |
| Unikernel | App + OS libraries compiled into one single-AS image |
| Spinlock | Busy-wait lock; usable in interrupt context |
| Mutex | Sleeping lock; process context only |
| RCU | Read-Copy-Update; zero-cost reads, deferred writer cleanup |
| Preemptible kernel | Scheduler can interrupt a thread mid-syscall |
| seL4 | Formally verified L4 microkernel |
