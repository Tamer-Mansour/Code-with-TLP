# Interview Drill: Race Conditions and Critical Sections

This lesson presents the most frequently asked interview questions on race conditions and critical sections — at both the conceptual level (define, explain, design) and the code level (spot the bug, fix it). For each question you'll find a crisp answer you can deliver in 30–60 seconds.

## Conceptual Questions

**Q: What is a race condition?**

> A race condition is a defect where the program's output depends on the non-deterministic interleaving of concurrent threads accessing shared data, with at least one thread writing. Because scheduling order is unpredictable, the bug is intermittent and hard to reproduce.

---

**Q: What are the three requirements a correct critical-section solution must satisfy?**

> Mutual exclusion (only one thread inside at a time), progress (a thread can enter if no one else is inside and it wants to), and bounded waiting (no thread waits indefinitely after requesting entry). These map to safety, liveness, and fairness.

---

**Q: Why is `count++` not thread-safe?**

> It compiles to three separate instructions: load from memory, add in a register, store back. Two threads can both load the same old value, both add 1, and both store the same result — losing one increment. Fix it with `std::atomic<int>` or a mutex.

---

**Q: What is the difference between a data race and a race condition?**

> A **data race** (C++ definition) is when two threads access the same memory location concurrently, at least one writes, and there is no synchronization between them. It is undefined behavior in C/C++. A **race condition** is a broader logical bug where the outcome depends on timing — it can exist even without a data race (e.g., a TOCTOU bug using file system calls, which are not in-process memory accesses).

---

**Q: What is a critical section and how do you minimize its impact on performance?**

> A critical section is any code that accesses shared state and must not run concurrently. To minimize impact: keep the section as small as possible (only protect the data mutation, not surrounding computation), use fine-grained locks (per-item locks rather than a global lock), prefer read-write locks for read-heavy workloads, and consider lock-free data structures for hot paths.

---

## Code-Level Questions

**Q: Spot the bug.**

```c
if (instance == NULL) {
    instance = create_singleton();
}
return instance;
```

> This is a **check-then-act** race. Two threads can both see `instance == NULL`, both call `create_singleton()`, and both assign — resulting in two instances (memory leak, broken singleton). Fix: use `pthread_once`, `std::call_once`, or double-checked locking with a mutex and an `atomic` pointer with `acquire`/`release` semantics.

---

**Q: What does Peterson's algorithm use to guarantee mutual exclusion without hardware instructions?**

> It uses two shared variables: a `flag` array (each thread signals intent to enter) and a `turn` variable (a tiebreaker). A thread sets its flag, yields the turn to the other thread, and only enters if the other thread's flag is down OR it's not that thread's turn. Since `turn` can only hold one value at a time, both threads cannot satisfy the condition simultaneously.

---

**Q: What is the ABA problem?**

> When using Compare-and-Swap, thread T1 reads value A, gets preempted, another thread changes the location to B then back to A. T1's CAS succeeds because the value *looks* unchanged, but the underlying state may have changed meaningfully (e.g., a pointer was freed and reallocated to a different object). Solutions: version counters (tagged pointers) or Load-Linked/Store-Conditional primitives which detect *any* write, not just a value change.

---

## Quick-Reference Answers

| Question | One-line answer |
|---|---|
| Heisenbug | A bug (often a race) that disappears when you add instrumentation, because the instrumentation changes timing |
| TOCTOU | Time-of-check to time-of-use: a race between checking a condition and acting on it |
| Priority inversion | A high-priority thread blocks on a lock held by a low-priority thread |
| Deadlock vs. livelock | Deadlock: all threads block forever. Livelock: all threads keep changing state but make no progress |
| Spinlock vs. mutex | Spinlock burns CPU while waiting (good for short waits, no context switch). Mutex puts thread to sleep (good for long waits, higher overhead) |

## Common Pitfalls Interviewers Test For

- Assuming `volatile` provides atomicity in C/C++ — it does not (it only prevents caching in a register, not atomic RMW).
- Forgetting that even atomic operations can form non-atomic *sequences* (`if (atomic_load(x)) atomic_store(x, v)` is still a race).
- Using a mutex in an interrupt/signal handler — mutexes are not async-signal-safe.
- Double-free from a race in destructor/cleanup code in multi-threaded programs.
