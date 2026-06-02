# Quiz: Polling, Interrupt-Driven I/O, and the Timer Interrupt

**Q1. A 25 Gbps NIC can receive approximately 37 million minimum-size packets per second. Which I/O strategy is most appropriate for its driver?**

- [ ] One interrupt per received packet, handled synchronously in the ISR
- [x] Polling with hardware interrupt coalescing and NAPI-style batch processing
- [ ] Blocking the kernel on a wait queue until the NIC buffer is full
- [ ] Using a workqueue to process each packet in process context

_At 37 Mpps, per-packet interrupts would consume entire CPU cores just on ISR overhead. Polling/NAPI/coalescing batches the work, keeping throughput high._

---

**Q2. Which of the following is ILLEGAL inside an Interrupt Service Routine?**

- [ ] Reading a device register with `readl()`
- [ ] Writing to a spinlock-protected variable using `spin_lock_irq()`
- [x] Calling `kmalloc(size, GFP_KERNEL)` to allocate memory
- [ ] Scheduling a tasklet with `tasklet_schedule()`

_`GFP_KERNEL` may sleep waiting for memory to be freed, which is forbidden in interrupt context. Use `GFP_ATOMIC` instead._

---

**Q3. The Linux kernel is compiled with `HZ=250`. A timer set for exactly 10 ms may actually fire after how long?**

- [ ] Exactly 10 ms — the kernel compensates for tick granularity
- [ ] Between 0 ms and 4 ms
- [x] Between 10 ms and 14 ms (up to one tick late)
- [ ] Always 10 ms if using `hrtimer`

_With HZ=250 the tick period is 4 ms. A standard timer fires on the next tick after the deadline, so it can be up to one tick (4 ms) late. `hrtimer` bypasses this by programming the hardware timer directly._

---

**Q4. What is the primary purpose of the `TIF_NEED_RESCHED` flag?**

- [ ] To signal the CPU to disable interrupts immediately
- [ ] To mark a process as having exited
- [ ] To tell the memory manager to reclaim the process's pages
- [x] To indicate that the scheduler should run when execution returns to a safe context

_The timer ISR sets `TIF_NEED_RESCHED` when a time slice expires. The actual `schedule()` call happens later, at the return-to-user-space path or an explicit preemption point — not inside the ISR itself._

---

**Q5. A device driver's bottom half needs to allocate a large buffer and then read from a file on disk. Which deferred work mechanism should it use?**

- [ ] Softirq, because softirqs have the highest priority among bottom halves
- [ ] Tasklet, because tasklets are serialized and safe
- [x] Workqueue, because it runs in process context and can sleep
- [ ] The top half (ISR) directly, to minimize latency

_Disk reads block. Only workqueues run in process context where sleeping is allowed. Softirqs and tasklets run in interrupt context — sleeping there deadlocks the system._

---

**Q6. You run `ethtool -C eth0 rx-usecs 0 rx-frames 1` on a trading server. What is the expected effect?**

- [ ] Maximum throughput — packets are batched into the largest possible groups
- [ ] No effect — interrupt coalescing is a read-only NIC property
- [x] Minimum latency — one interrupt per received packet, no coalescing delay
- [ ] The NIC switches to polling mode and disables interrupts entirely

_Setting `rx-usecs=0` and `rx-frames=1` disables coalescing, generating one interrupt per packet. This minimizes the time between packet arrival and application notification, at the cost of higher CPU overhead — the correct choice for latency-sensitive workloads like algorithmic trading._
