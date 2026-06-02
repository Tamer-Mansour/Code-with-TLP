# Quiz: Synchronization Primitives: Mutexes, Semaphores, and Spinlocks

Test your understanding of mutexes, semaphores, spinlocks, and related synchronization concepts.

---

**Q1. Which property distinguishes a mutex from a binary semaphore with initial value 1?**

- [ ] A mutex can be signaled by any thread; a semaphore cannot.
- [ ] A mutex allows counting beyond 1; a semaphore does not.
- [x] A mutex has ownership — only the locking thread may unlock it; a semaphore does not.
- [ ] A mutex uses busy-waiting; a semaphore uses blocking.

A mutex enforces ownership: the thread that calls lock() is the only thread permitted to call unlock(). This enables priority inheritance and stricter correctness guarantees. A binary semaphore with value 1 can be signaled by any thread.

---

**Q2. A thread calls `sem_wait()` on a semaphore whose current value is 0. What happens?**

- [ ] The call returns immediately with an error code.
- [x] The thread blocks until another thread calls `sem_post()`.
- [ ] The semaphore value is decremented to -1 and the thread continues.
- [ ] The call spins until the value becomes 1.

`sem_wait()` blocks the calling thread when the value is 0, placing it on the semaphore's wait queue. It is woken when another thread calls `sem_post()`, incrementing the value and releasing one waiter.

---

**Q3. In which scenario is a spinlock the better choice over a mutex?**

- [ ] Protecting a database connection that may hold the lock for several seconds.
- [ ] User-space code running on a uniprocessor machine.
- [x] A kernel interrupt handler that must update a short shared data structure.
- [ ] A web server handling multiple simultaneous client connections.

A spinlock is mandatory in interrupt-handler (IRQ) context because sleeping is forbidden there. For long-held locks or user-space code — especially on a uniprocessor where spinning blocks the holder — a mutex is correct.

---

**Q4. Why must the condition check in `pthread_cond_wait` always be placed in a `while` loop rather than an `if` statement?**

- [ ] Because `pthread_cond_wait` always returns a non-zero error code.
- [ ] Because the mutex is not reacquired before the function returns.
- [x] Because spurious wakeups can occur and another thread may have already consumed the resource.
- [ ] Because condition variables do not support broadcast semantics.

Condition variables can produce spurious wakeups (woken without a signal). Additionally, with multiple consumers, another thread may have already taken the awaited resource between the wakeup and the reacquisition of the mutex. The `while` loop re-checks the condition and re-waits if it is still false.

---

**Q5. You have a hash map accessed by 32 threads simultaneously. Using one global mutex causes poor throughput. What is the most practical first step to improve scalability?**

- [ ] Replace the mutex with a spinlock.
- [ ] Increase the thread count to 64.
- [x] Shard the hash map into N buckets, each protected by its own mutex (fine-grained locking).
- [ ] Remove all locking and rely on atomic operations for every field.

Fine-grained locking (one lock per shard) allows threads accessing different buckets to proceed in parallel, directly reducing contention. Lock-free structures are also effective but far more complex to implement correctly.

---

**Q6. What is the convoy effect?**

- [ ] When threads are scheduled in strict FIFO order, causing high-priority threads to starve.
- [ ] When a thread acquires two locks in opposite order, causing deadlock.
- [ ] When priority inheritance boosts a low-priority thread above a medium-priority thread.
- [x] When many fast threads queue behind a slow lock holder, then wake and run serially, causing cascading serialization.

The convoy effect occurs when a slow thread holds a lock long enough for many other threads to accumulate in its wait queue. Those waiters then run one at a time after the holder releases, creating serialized execution even though the individual waiters are fast. The remedy is keeping critical sections short and avoiding blocking I/O while holding a lock.
