# Interview Drill: Polling vs Interrupts and Timers

This lesson collects the most frequently asked interview questions on polling, interrupt-driven I/O, the timer interrupt, and related kernel mechanisms. Each answer is concise and structured for verbal delivery.

---

## Q1: What is the difference between polling and interrupt-driven I/O?

**Crisp answer:** Polling spins the CPU in a loop checking a device status register. Interrupt-driven I/O lets the CPU do other work and respond only when the device asserts an interrupt line. Polling has lower latency for fast devices; interrupts are more efficient for slow or infrequent ones.

**Follow-up trap:** *"Which is always better?"* — Neither. DPDK uses polling for 10 Gbps+ NICs because per-packet interrupt overhead exceeds the packet processing time itself.

---

## Q2: What is an ISR and what constraints apply to code running in one?

**Crisp answer:** An ISR (Interrupt Service Routine) is a kernel function registered for a specific interrupt vector. It runs with interrupts disabled (or at elevated priority), so it must:

- Complete in microseconds — no loops with unpredictable duration.
- Never sleep or block (no mutexes, no `kmalloc(GFP_KERNEL)`).
- Use `GFP_ATOMIC` for any memory allocation.
- Defer heavy work to a bottom half (softirq, tasklet, or workqueue).

---

## Q3: What is the timer interrupt and what does it enable?

**Crisp answer:** The timer interrupt is a periodic hardware interrupt (at HZ ticks/second, typically 250–1000 Hz on Linux). Each tick the kernel:

1. Increments `jiffies`.
2. Charges the running process for CPU time.
3. Decrements its time slice and sets `TIF_NEED_RESCHED` if expired.
4. Fires expired software timers.

This makes preemptive multitasking possible — without it, a process could spin forever.

---

## Q4: What is `jiffies` and what are its limitations?

**Crisp answer:** `jiffies` is a kernel counter incremented once per timer tick. Its resolution is one tick (1 ms at HZ=1000). Limitations:

- Too coarse for sub-millisecond timing — use `ktime_get()` (reads hardware clock directly).
- Wraps around on 32-bit systems every ~49 days — always use `time_after()` macro to compare, never raw subtraction.
- On tickless (NO_HZ) systems, `jiffies` may lag behind real time if the CPU was idle.

---

## Q5: What are top halves and bottom halves? When do you use a workqueue vs. a tasklet?

**Crisp answer:**

- **Top half (ISR):** minimal, fast, interrupts-disabled — acknowledge device, capture urgent data, schedule bottom half.
- **Bottom half:** deferred processing with interrupts re-enabled.
  - **Tasklet:** interrupt context, cannot sleep, serialized per-tasklet — good for medium complexity.
  - **Workqueue:** process context, can sleep, can use any kernel API — required when work may block.

**Rule:** If your bottom half might call `kmalloc(GFP_KERNEL)`, `msleep()`, or any blocking API, use a workqueue.

---

## Q6: What is interrupt coalescing and when would you tune it?

**Crisp answer:** Interrupt coalescing delays generating an interrupt until N completions accumulate or a timeout expires. It trades latency for throughput. Tune it when:

- **Reducing latency** (e.g., trading applications, gaming servers): set `rx-usecs=0`, `rx-frames=1` — one interrupt per packet.
- **Maximizing throughput** (e.g., bulk file transfer, video streaming): set `rx-usecs=100+`, `rx-frames=64+` — batch many packets per ISR.

Configured via `ethtool -C <interface> rx-usecs <N> rx-frames <N>`.

---

## Q7: What is NAPI and how does it combine polling and interrupts?

**Crisp answer:** NAPI (New API) is Linux's hybrid NIC driver model:

1. First packet arrives → interrupt fires → ISR disables further interrupts for that queue → schedules NAPI poll.
2. NAPI poll function drains the RX queue in a budget loop (e.g., 64 packets max).
3. If queue is empty after the budget: re-enable interrupts, exit.
4. If budget exhausted: yield to scheduler, reschedule poll next softirq cycle.

This prevents interrupt storms at high traffic while remaining power-efficient at low traffic.

---

## Q8: How can a single-CPU system have a race condition between an ISR and normal kernel code?

**Crisp answer:** Even on one CPU, an ISR can fire between any two instructions of normal code. If both the ISR and normal code access a shared variable, the ISR sees a partially updated state. Solution: use `local_irq_save(flags)` / `local_irq_restore(flags)` to disable interrupts around the critical section on the normal-code side — since the ISR itself cannot be preempted by another ISR of the same type by default.

---

## Q9: What is `TIF_NEED_RESCHED` and when is it checked?

**Crisp answer:** `TIF_NEED_RESCHED` is a per-thread flag set by the timer ISR (or any code that determines the current process should yield). It is checked at every **return-to-user-space path** (after system calls and after interrupt returns). If set, `schedule()` is called, which performs the actual context switch. This design keeps ISR code minimal — the ISR just sets a flag; the switch happens at a safe process-context boundary.

---

## Quick Reference Table

| Concept | One-line definition |
|---|---|
| Polling | CPU spins checking device status register |
| Interrupt | Device signals CPU asynchronously |
| Timer interrupt | Periodic interrupt enabling preemption and timekeeping |
| jiffies | Kernel tick counter, 1 ms resolution at HZ=1000 |
| Top half | Fast ISR: acknowledge + schedule bottom half |
| Bottom half | Deferred work: softirq/tasklet (no sleep) or workqueue (can sleep) |
| TIF_NEED_RESCHED | Flag set by timer tick; triggers schedule() on return to user space |
| Interrupt coalescing | Batch completions into fewer interrupts for throughput |
| NAPI | Hybrid: interrupt to start, then poll to drain queue |
