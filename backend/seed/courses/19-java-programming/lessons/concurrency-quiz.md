# Quiz: Java Concurrency

**Q1. What does `volatile` guarantee in Java?**
- [ ] Atomicity of compound operations
- [x] Visibility of writes to all threads
- [ ] Mutual exclusion
- [ ] That the field is immutable

**Q2. Which class provides a lock-free thread-safe counter?**
- [ ] `SynchronizedInteger`
- [ ] `volatile int`
- [x] `AtomicInteger`
- [ ] `ReentrantLock`

**Q3. What is the difference between `thenApply` and `thenCompose` on a `CompletableFuture`?**
- [x] `thenApply` maps `T -> U`; `thenCompose` maps `T -> CompletableFuture<U>` (flatMap)
- [ ] `thenApply` runs asynchronously; `thenCompose` runs synchronously
- [ ] They are identical
- [ ] `thenCompose` is used for error handling

**Q4. `ExecutorService.shutdown()` vs `shutdownNow()` — what is the difference?**
- [x] `shutdown()` stops accepting new tasks but waits for running tasks to finish; `shutdownNow()` attempts to interrupt running tasks immediately
- [ ] `shutdown()` interrupts all running threads; `shutdownNow()` waits for completion
- [ ] They are equivalent
- [ ] `shutdown()` is for thread pools; `shutdownNow()` is for single threads

**Q5. Which concurrent collection is best for a high-throughput read-heavy map?**
- [ ] `Collections.synchronizedMap(new HashMap<>())`
- [x] `ConcurrentHashMap`
- [ ] `Hashtable`
- [ ] `TreeMap`

**Q6. A `ReentrantLock` advantage over `synchronized` is:**
- [ ] It is automatically released if you forget to unlock
- [ ] It prevents deadlocks
- [x] It supports `tryLock()` and timed/interruptible locking
- [ ] It is faster in all scenarios

**Q7. What happens if `CompletableFuture.allOf(f1, f2, f3).join()` is called and `f2` throws an exception?**
- [ ] The other futures are cancelled
- [ ] The exception is silently swallowed
- [x] `join()` throws a `CompletionException` wrapping the original exception
- [ ] Only `f2`'s result is skipped; the others succeed normally
