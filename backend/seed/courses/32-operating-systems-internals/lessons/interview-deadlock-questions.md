# Interview Drill: Deadlock and Priority Inversion

This lesson collects the most frequently asked interview questions on deadlock, livelock, and priority inversion — along with concise, accurate answers you can deliver confidently in a technical interview.

## Question 1: What are the four necessary conditions for deadlock?

**Strong answer:**

Mutual exclusion, hold-and-wait, no preemption, and circular wait. All four must hold simultaneously. Eliminating any one of the four prevents deadlock entirely. The most practical elimination target in software is circular wait, achieved by enforcing a global lock-ordering discipline.

## Question 2: How do you prevent deadlock in practice?

**Strong answer:**

The most robust technique is **lock ordering**: assign a consistent global rank to every lock and always acquire locks in increasing rank order. In C++ this is automated with `std::lock()`, which uses a deadlock-safe acquisition protocol. Other options include acquiring all needed locks atomically at the start of a transaction (eliminates hold-and-wait), or using lock-free data structures that eliminate mutual exclusion entirely.

```cpp
// Safe: std::lock acquires both without deadlock regardless of order
std::lock(mutex_a, mutex_b);
std::lock_guard<std::mutex> la(mutex_a, std::adopt_lock);
std::lock_guard<std::mutex> lb(mutex_b, std::adopt_lock);
```

## Question 3: What is the Banker's Algorithm and when is it used?

**Strong answer:**

The Banker's Algorithm (Dijkstra, 1965) is a **deadlock avoidance** technique that grants resource requests only when a safety algorithm confirms every process can still complete. It requires processes to pre-declare their maximum resource needs. It is used in database systems and real-time schedulers where the resource set is bounded and known. It is too expensive and restrictive for general-purpose OSes. Time complexity: O(n² m) per request.

## Question 4: What is the difference between deadlock detection and deadlock prevention?

| | Prevention | Detection |
|--|-----------|----------|
| When? | Design time | Runtime |
| How? | Remove one of the 4 conditions | Run cycle detection; recover |
| Concurrency | Reduced | Full |
| Cost | Structural constraints | Periodic CPU overhead + rollback |

**Prevention** is conservative and restricts how processes use resources. **Detection** is optimistic, allows more concurrency, but requires recovery mechanisms.

## Question 5: How does a database handle deadlock?

**Strong answer:**

Most RDBMS engines (PostgreSQL, MySQL InnoDB, SQL Server) maintain a **lock graph** (Wait-For Graph) and run cycle detection after each lock acquisition. When a cycle is found, the engine selects a **victim transaction** based on rollback cost (typically the one that has done the least work), aborts it, and returns an error to the application. The application is expected to catch this error and retry the transaction.

```sql
-- Application-level retry pattern in pseudo-code
for attempt in range(MAX_RETRIES):
    try:
        BEGIN TRANSACTION
        ... your queries ...
        COMMIT
        break
    except DeadlockError:
        ROLLBACK
        sleep(random_backoff())
```

## Question 6: What is livelock? How is it different from deadlock?

**Strong answer:**

In a deadlock, processes are **blocked** and consume no CPU. In a livelock, processes are **actively running** but keep politely yielding to each other in a cycle, consuming CPU without making progress. Livelock is harder to detect because the Wait-For Graph shows no cycle — no process is actually blocked. The canonical fix is **randomised exponential backoff** so retries are unlikely to collide.

## Question 7: Explain priority inversion and how to fix it.

**Strong answer:**

Priority inversion occurs when a high-priority task (H) is blocked waiting for a mutex held by a low-priority task (L), while a medium-priority task (M) preempts L — effectively making H wait as long as M runs. The standard fix is **priority inheritance**: when H blocks on L's mutex, L temporarily inherits H's priority so M cannot preempt it. L finishes its critical section quickly, releases the mutex, and H resumes. POSIX provides `PTHREAD_PRIO_INHERIT` for this purpose. The Mars Pathfinder spacecraft experienced this exact bug in 1997 and was fixed remotely.

## Question 8: How would you debug a suspected deadlock in production?

**Strong answer — step-by-step approach:**

1. **Take a thread dump** (`kill -3` on JVM, `pstack` on Linux native, `!threads` in WinDbg).
2. **Identify blocked threads** — look for threads stuck in lock acquisition (WAITING or BLOCKED state).
3. **Build the Wait-For Graph** — trace which thread holds what lock and which thread is waiting for it.
4. **Find the cycle** — the deadlocked threads form a closed chain.
5. **Find the root cause** — look for lock-ordering violations, missing timeouts, or callbacks acquired inside a lock.
6. **Fix** — enforce lock ordering, add `try_lock` with timeout, or restructure to avoid nested locking.

For Go programs, the runtime detects deadlock automatically and panics with a full goroutine dump.

## Rapid-Fire Answers

| Question | One-Line Answer |
|----------|----------------|
| Can a single-threaded program deadlock? | Only if it tries to acquire a non-recursive lock it already holds. |
| Is starvation the same as deadlock? | No. In starvation, progress exists for others; in deadlock, no one can proceed. |
| Does Java's `synchronized` support priority inheritance? | No — JVM locks do not propagate priorities. Use a real-time JVM if needed. |
| What kernel tool detects lock ordering violations? | Linux `lockdep` (CONFIG_LOCKDEP) detects circular lock dependencies at runtime. |
| When is deadlock avoidance preferred over detection? | When rollback is expensive or impossible (e.g., real-time systems, robotics). |
