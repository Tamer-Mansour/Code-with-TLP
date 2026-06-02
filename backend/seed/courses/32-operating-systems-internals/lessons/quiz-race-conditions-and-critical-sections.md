# Quiz: Concurrency Hazards: Race Conditions and Critical Sections

**Q1. Two threads simultaneously execute `counter++` on the same shared integer (initially 0). Which of the following is the most accurate description of the possible outcomes?**

- [ ] The result is always 2 because modern CPUs serialize memory writes automatically.
- [x] The result can be 1 or 2 depending on the interleaving of load, add, and store micro-steps.
- [ ] The result is always 1 because only one thread can execute at a time on a multi-core CPU.
- [ ] The program will always crash with a segmentation fault.

*Explanation: `counter++` is a load-add-store sequence. If both threads load before either stores, both compute 1 and the final value is 1 (lost update). If they execute sequentially, the result is 2.*

---

**Q2. Which of the three critical-section requirements is violated by "strict alternation" (a protocol that forces threads to take turns even when one is not interested in entering)?**

- [ ] Mutual exclusion
- [x] Progress
- [ ] Bounded waiting
- [ ] Atomicity

*Explanation: Strict alternation violates progress because a thread that is NOT trying to enter the critical section can block another thread that IS waiting. The decision about entry must not involve threads in their remainder sections.*

---

**Q3. What does the `LOCK` prefix on an x86 instruction (e.g., `LOCK XADD`) guarantee?**

- [ ] The instruction cannot be interrupted by an OS context switch.
- [ ] The instruction executes in a single CPU clock cycle.
- [x] The read-modify-write on the memory operand is indivisible across all CPU cores.
- [ ] The instruction disables all hardware interrupts for its duration.

*Explanation: `LOCK` causes the processor to assert exclusive ownership of the relevant cache line for the duration of the instruction, making the read-modify-write atomic from the perspective of all other cores. It does NOT disable interrupts or guarantee single-cycle execution.*

---

**Q4. Which statement about Compare-and-Swap (CAS) and the ABA problem is correct?**

- [ ] CAS is immune to the ABA problem because it compares the full value, not just the address.
- [ ] The ABA problem only occurs in single-threaded programs.
- [x] CAS can incorrectly succeed when a value changes from A to B and back to A, because it only checks the current value, not the history of changes.
- [ ] The ABA problem is automatically prevented by using 64-bit CAS on a 64-bit system.

*Explanation: CAS compares by value. If another thread changes a location from A→B→A while your thread is preempted, your CAS sees A and succeeds — potentially on stale data. Version counters or LL/SC primitives are used to prevent this.*

---

**Q5. In Peterson's algorithm for two threads, what is the purpose of the `turn` variable?**

- [ ] To count how many times each thread has entered the critical section.
- [ ] To store the thread ID of the current owner of the critical section.
- [x] To act as a tiebreaker when both threads simultaneously want to enter, ensuring only one proceeds.
- [ ] To implement bounded waiting by rotating entry priority.

*Explanation: Both threads set `turn` to the OTHER thread when they want to enter. If both threads execute simultaneously, the second write to `turn` wins, and only that thread's value stands — causing the other thread to be the one that may proceed (since `turn` won't equal its waiting condition).*

---

**Q6. Which of the following correctly describes the difference between `memory_order_relaxed` and `memory_order_seq_cst` in C++ atomics?**

- [ ] `relaxed` is faster but only works on x86; `seq_cst` is portable.
- [ ] `relaxed` prevents compiler reordering; `seq_cst` additionally prevents CPU reordering.
- [ ] They produce identical machine code on all architectures.
- [x] `relaxed` provides no ordering guarantees relative to other operations; `seq_cst` imposes a single total order of all sequentially-consistent operations across all threads.

*Explanation: `relaxed` atomics are atomic (no torn reads/writes) but allow the compiler and CPU to freely reorder them relative to other memory accesses. `seq_cst` is the strongest ordering — it implies acquire/release AND a global total order, at the cost of a full memory fence on weakly-ordered architectures like ARM.*
