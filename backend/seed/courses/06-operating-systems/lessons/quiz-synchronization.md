# Quiz: Synchronization & Deadlock

**Q1. Which of the four Coffman conditions is EASIEST to prevent by programming convention alone?**

- [ ] Mutual exclusion — avoid making resources non-shareable
- [ ] No preemption — allow locks to be stolen
- [ ] Hold and wait — require all resources before starting
- [x] Circular wait — by enforcing a global total ordering on lock acquisition

**Q2. What is the key difference between a mutex and a binary semaphore?**

- [ ] A mutex can have a value greater than 1; a binary semaphore is limited to 0 or 1
- [x] A mutex has ownership — only the thread that acquired it may release it; any thread may call signal() on a semaphore
- [ ] A binary semaphore can be used for inter-process synchronization; a mutex cannot cross process boundaries
- [ ] There is no meaningful difference — they are interchangeable in all scenarios

**Q3. In the producer-consumer problem with a bounded buffer, the `full` semaphore tracks:**

- [ ] The number of free slots remaining in the buffer
- [x] The number of items currently in the buffer that are ready to be consumed
- [ ] Whether the mutex protecting the buffer is currently held or free
- [ ] The number of producer threads that are currently blocked waiting to insert

**Q4. What does `condition.wait()` do inside a monitor?**

- [ ] Spins in a busy loop until the condition variable becomes true
- [ ] Acquires the associated lock and then waits passively for a signal
- [x] Atomically releases the lock and suspends the calling thread; reacquires the lock automatically when notified
- [ ] Signals all other threads that are waiting on the same condition variable

**Q5. A livelock differs from a deadlock in that:**

- [ ] Livelock only affects I/O-bound processes; deadlock only affects CPU-bound ones
- [ ] Livelock requires more than two processes; deadlock can involve just two
- [x] In a livelock, processes keep actively changing state in response to each other but make no real progress; in a deadlock, all involved processes are completely blocked
- [ ] Livelock can only occur with spinlocks; deadlock requires sleeping mutexes

**Q6. The Banker's Algorithm avoids deadlock by:**

- [ ] Detecting cycles in the resource-allocation graph and killing one process
- [ ] Killing the lowest-priority process whenever the system runs low on resources
- [x] Only granting resource requests that keep the system in a safe state — one from which a safe completion sequence for all processes exists
- [ ] Ordering all resource acquisitions globally, preventing circular wait from forming
