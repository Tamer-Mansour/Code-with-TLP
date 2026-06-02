# Quiz: C++ Concurrency

**Q1. What happens if a `std::thread` object is destroyed without being joined or detached?**
- [ ] The thread continues running in the background
- [ ] The thread is automatically joined
- [x] `std::terminate` is called
- [ ] A `std::system_error` is thrown

**Q2. Which RAII lock wrapper should you prefer for simple exclusive locking?**
- [x] `std::lock_guard`
- [ ] `std::mutex::lock()` / `unlock()` manually
- [ ] `std::unique_lock` with `defer_lock`
- [ ] `std::shared_lock`

**Q3. A data race in C++ is:**
- [ ] A performance issue that may slow your program
- [ ] Defined behavior as long as reads happen before writes
- [x] Undefined behavior — the compiler and CPU may produce arbitrary results
- [ ] Automatically prevented by the OS scheduler

**Q4. `std::condition_variable::wait` must be called with:**
- [ ] Any lock type
- [x] A `std::unique_lock<std::mutex>`
- [ ] A `std::lock_guard<std::mutex>`
- [ ] No lock (it manages its own mutex)

**Q5. `std::async(std::launch::async, f)` guarantees:**
- [ ] `f` runs on the calling thread
- [ ] `f` is deferred until `.get()` is called
- [x] `f` runs on a new thread (or a thread pool thread)
- [ ] `f` runs with elevated priority

**Q6. Which type is best for a simple lock-free hit counter shared across threads?**
- [ ] `int` with manual synchronization
- [ ] `std::mutex`-protected `int`
- [x] `std::atomic<int>`
- [ ] `std::future<int>`

**Q7. `std::scoped_lock(mtxA, mtxB)` compared to locking `mtxA` then `mtxB` manually:**
- [ ] Is slower but simpler
- [ ] Does the same thing in the same order
- [x] Avoids deadlock by locking both atomically using a deadlock-avoidance algorithm
- [ ] Only works if `mtxA == mtxB`
