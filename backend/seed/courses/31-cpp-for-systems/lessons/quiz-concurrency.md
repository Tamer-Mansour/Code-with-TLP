# Quiz: Concurrency: Threads and Synchronization

**Q1. What happens if a `std::thread` object is destroyed while still joinable (neither joined nor detached)?**

- [ ] The thread is automatically joined before the destructor returns.
- [ ] The thread is automatically detached and continues running in the background.
- [x] `std::terminate()` is called, crashing the program.
- [ ] The destructor blocks until the thread finishes.

`std::thread`'s destructor calls `std::terminate()` if the thread is still joinable. This is a deliberate design choice to prevent resource leaks from being silently ignored. Use `std::jthread` (C++20) for automatic joining.

---

**Q2. Which of the following correctly acquires two mutexes `mtx_a` and `mtx_b` without risk of deadlock?**

- [ ] `std::lock_guard la(mtx_a); std::lock_guard lb(mtx_b);`
- [x] `std::scoped_lock lock(mtx_a, mtx_b);`
- [ ] `mtx_a.lock(); mtx_b.lock();`
- [ ] `std::unique_lock la(mtx_a, std::defer_lock); la.lock(); std::unique_lock lb(mtx_b); lb.lock();`

`std::scoped_lock` (C++17) acquires multiple mutexes atomically using a deadlock-avoidance algorithm. The other options can deadlock if another thread acquires the same mutexes in a different order.

---

**Q3. In the producer-consumer pattern, why must `std::condition_variable::wait()` always be called with a predicate?**

- [ ] Without a predicate, the wait does not release the mutex.
- [ ] Without a predicate, `notify_one()` has no effect.
- [x] Spurious wakeups can cause `wait()` to return without `notify_one()` being called.
- [ ] The predicate is required for the compiler to infer the lock type.

Spurious wakeups are allowed by the C++ standard and occur on some OS implementations. Without a predicate loop, the waiting thread may proceed even though the condition it is waiting for is not yet true, causing incorrect behavior.

---

**Q4. What is the key difference between a data race and a race condition?**

- [ ] Data races occur only in multi-process programs; race conditions occur in multithreaded programs.
- [ ] A data race is always a logic bug; a race condition is always undefined behavior.
- [x] A data race is unsynchronized concurrent access with at least one write (undefined behavior in C++); a race condition is a logic bug where output depends on thread ordering.
- [ ] They are synonyms; both terms describe the same phenomenon.

A data race has a precise C++ standard definition: two threads access the same memory location, at least one access is a write, and there is no happens-before relationship between them. This is undefined behavior. A race condition is a broader logical concept and can occur even with proper synchronization (e.g., TOCTOU bugs).

---

**Q5. Which `std::memory_order` should you use on a `store` when publishing data to another thread via a flag?**

- [ ] `memory_order_relaxed`
- [ ] `memory_order_consume`
- [x] `memory_order_release`
- [ ] `memory_order_seq_cst` is the only safe option

`memory_order_release` on the store creates a happens-before edge with any thread that performs an `acquire` load and sees the stored value. This guarantees that all writes before the release-store are visible to the acquiring thread. `seq_cst` also works but adds unnecessary overhead.

---

**Q6. Which statement about `std::atomic<int>` is TRUE?**

- [ ] `std::atomic<int>` always uses a mutex internally.
- [ ] `counter++` on a `std::atomic<int>` is not safe without an additional lock.
- [ ] `std::atomic<int>` variables cannot be used without specifying a memory order explicitly.
- [x] `std::atomic<int>` guarantees that `counter++` is an indivisible read-modify-write operation with no data race.

On platforms where `int` is natively lock-free (virtually all modern architectures), `std::atomic<int>` uses hardware atomic instructions and involves no mutex. The default memory order is `seq_cst`, so no explicit annotation is needed. The operation is guaranteed atomic and free of data races.
