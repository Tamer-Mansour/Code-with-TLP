# Quiz: Classic Synchronization Problems

**Q1. In the semaphore-based producer-consumer solution, what is the initial value of the `full` semaphore?**

- [ ] Equal to the buffer capacity N
- [x] 0
- [ ] 1
- [ ] Undefined — it depends on the number of producers

`full` counts the number of items currently in the buffer. At startup the buffer is empty, so `full` starts at 0; consumers block immediately until a producer posts to it.

---

**Q2. In the readers-preferred readers-writers solution, which of the following is TRUE?**

- [ ] Writers can run concurrently with readers
- [ ] Writers are always served before readers
- [x] A writer can be starved if readers arrive continuously
- [ ] Only one reader is allowed at a time

The readers-preferred solution allows new readers to join while existing readers are active. If readers arrive at a high enough rate, the write_lock is never released, starving the writer indefinitely.

---

**Q3. In the naive dining philosophers solution (each picks up left fork then right fork), which of the four deadlock conditions is present that causes the deadlock?**

- [ ] Mutual exclusion
- [ ] Hold and wait
- [ ] No preemption
- [x] Circular wait

All four conditions are present, but the one that the table geometry directly creates is circular wait: each philosopher holds their left fork and waits for the right, forming a cycle among all five philosophers.

---

**Q4. You replace `pthread_cond_broadcast` with `pthread_cond_signal` in a barrier implementation. What is the most likely result?**

- [ ] The barrier works correctly but is slightly slower
- [ ] A data race on the counter variable
- [x] All but one waiting thread sleep forever
- [ ] The barrier wakes threads in LIFO order instead of FIFO

`cond_signal` wakes exactly one waiting thread. The remaining N-1 threads stay blocked on the condition variable and are never woken, causing the program to hang.

---

**Q5. Which change correctly breaks the circular wait in the dining philosophers problem?**

- [ ] Each philosopher waits a random time before picking up any fork
- [x] One philosopher picks up the right fork before the left fork (while all others pick left first)
- [ ] Each philosopher picks up both forks simultaneously using a single atomic operation
- [ ] Reducing the number of philosophers by one

Making a single philosopher pick up forks in the opposite order breaks the cycle in the circular dependency graph. With asymmetric ordering, at least one pair of adjacent philosophers will compete for the same fork first, preventing a full circular wait from forming.

---

**Q6. In the producer-consumer semaphore solution, a producer thread executes `sem_wait(&mutex)` BEFORE `sem_wait(&empty)`. The buffer is full. What happens?**

- [ ] The producer correctly blocks until a consumer frees a slot
- [ ] A spurious wakeup occurs
- [x] Deadlock — the producer holds mutex while blocked on empty, so consumers cannot acquire mutex to consume
- [ ] The producer overwrites the oldest item in the buffer

Acquiring `mutex` before `empty` causes the producer to hold the buffer lock while waiting for a slot. Any consumer needing `mutex` to consume an item (and post to `empty`) will block indefinitely, creating a deadlock.
