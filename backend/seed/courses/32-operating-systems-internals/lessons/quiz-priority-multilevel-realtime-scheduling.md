# Quiz: Priority, Multilevel, and Real-Time Scheduling

**Q1. In a preemptive priority scheduler (lower number = higher priority), processes P1 (priority 3, burst 10), P2 (priority 1, burst 4), and P3 (priority 2, burst 6) all arrive at t=0. Which process runs first?**

- [ ] P1, because it has the longest burst
- [x] P2, because priority 1 is the highest
- [ ] P3, because priority 2 is the median
- [ ] They share the CPU equally in Round-Robin fashion

P2 has the numerically smallest priority value (1), making it the highest-priority process. The scheduler dispatches it immediately.

---

**Q2. What is the primary purpose of the "priority boost" in a Multilevel Feedback Queue (MLFQ)?**

- [ ] To reward processes that use their full CPU quantum
- [ ] To speed up I/O-bound processes permanently
- [x] To prevent starvation and re-adapt to processes that have changed behavior
- [ ] To increase the quantum size for lower-priority queues

Without periodic priority boosts, processes demoted to lower queues can wait indefinitely. The boost resets all processes to the top queue, giving demoted processes a fresh chance and re-evaluating changed workload patterns.

---

**Q3. A task set has three periodic tasks with utilizations U1=0.30, U2=0.25, U3=0.20. The Rate-Monotonic utilization bound for 3 tasks is approximately 0.780. What can we conclude?**

- [ ] The task set will definitely miss some deadlines under RM
- [x] The task set is guaranteed schedulable under RM
- [ ] EDF is required because RM cannot handle this task set
- [ ] Nothing — we need exact response-time analysis first

Total U = 0.30 + 0.25 + 0.20 = 0.75, which is below the RM bound of 0.780 for n=3. The sufficient condition is satisfied, so the task set is guaranteed schedulable under RM without needing further analysis.

---

**Q4. Which statement best describes the difference between hard and soft real-time systems?**

- [ ] Hard real-time systems are faster; soft real-time systems use more memory
- [ ] Hard real-time systems use SCHED_FIFO; soft real-time systems use SCHED_RR
- [ ] Soft real-time systems cannot use priority scheduling
- [x] In hard real-time, a missed deadline is a system failure; in soft real-time, occasional deadline misses are tolerable

The distinction is about the consequence of a miss, not about implementation choice. Hard RT systems (pacemakers, ABS) cannot tolerate any deadline violation. Soft RT systems (video players) degrade gracefully when a deadline is missed.

---

**Q5. What is priority inversion, and what is the standard fix?**

- [ ] A high-priority process demoting itself; fixed by MLFQ demotion
- [ ] Two processes sharing the same priority; fixed by aging
- [x] A high-priority process blocked on a resource held by a low-priority process while medium-priority processes run; fixed by priority inheritance
- [ ] A process running at a lower priority than assigned; fixed by the OS scheduler automatically

Priority inversion occurs when a medium-priority process indirectly blocks a high-priority one. Priority inheritance solves this by temporarily elevating the low-priority holder's priority to that of the waiting high-priority task, so it can complete and release the resource quickly.

---

**Q6. In Rate-Monotonic scheduling, how are static priorities assigned?**

- [ ] Longer burst time → higher priority
- [ ] Higher base priority number → higher priority
- [x] Shorter period (higher frequency) → higher priority
- [ ] Later deadline → higher priority

RM assigns priority inversely proportional to period: the task that repeats most frequently gets the highest priority. This assignment is optimal among all fixed-priority algorithms for periodic task sets.
