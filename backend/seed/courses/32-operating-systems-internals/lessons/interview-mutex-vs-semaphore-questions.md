# Interview Drill: Mutex vs Semaphore Questions

This lesson walks through the most commonly asked interview questions on synchronization primitives. For each question you will find the key facts, a common wrong answer to avoid, and a crisp one-line answer you can deliver confidently.

## Q1. What is the difference between a mutex and a semaphore?

**Key facts:**
- A mutex has **ownership** — only the locking thread can unlock it.
- A semaphore is a **counter** — any thread can increment (signal) it.
- Mutexes support **priority inheritance**; semaphores generally do not.
- Semaphores can count beyond 1, enabling resource-pool throttling.

**Common wrong answer:** "They're the same thing — both prevent race conditions."

> **One-liner:** A mutex is an owned binary lock for mutual exclusion; a semaphore is a counter for either mutual exclusion or inter-thread signaling, with no ownership.

---

## Q2. Can you use a binary semaphore instead of a mutex?

**Key facts:**
- You can use a binary semaphore (initial value = 1) to implement mutual exclusion syntactically.
- But you lose ownership: any thread can accidentally `post` it, bypassing the critical section.
- You lose priority inheritance: priority inversion is unmitigated.
- For pure signaling (one thread notifies another), a binary semaphore with initial value 0 is actually the **correct** choice; a mutex cannot do this cleanly.

**Common wrong answer:** "Yes, they're interchangeable."

> **One-liner:** A binary semaphore can enforce mutual exclusion syntactically, but it lacks ownership and priority inheritance — use a mutex for guarding shared state and a semaphore for signaling.

---

## Q3. What is priority inversion and how does a mutex solve it?

**Key facts:**
- Priority inversion: high-priority thread H waits on a lock held by low-priority thread L; medium-priority thread M preempts L, blocking H indirectly.
- Solution: **priority inheritance** — the OS temporarily boosts L to H's priority until L releases the lock.
- This requires knowing who holds the lock — possible with a mutex (ownership), impossible with a semaphore (no owner tracked).

**Diagram:**
```
Without priority inheritance:
  H (high)   [BLOCKED waiting for mutex]
  M (medium) [RUNNING — preempts L]
  L (low)    [PREEMPTED — holds mutex]
  Result: H is blocked by M despite M being lower priority than H

With priority inheritance:
  L is boosted to H's priority → M cannot preempt L
  L releases mutex → H wakes and runs
```

> **One-liner:** Priority inversion occurs when a medium-priority thread blocks a high-priority thread indirectly; a mutex with priority inheritance solves it by temporarily boosting the lock holder's priority.

---

## Q4. What happens if you call lock() twice on a non-recursive mutex?

**Key facts:**
- If the same thread calls `lock()` twice on a plain mutex, it **deadlocks** — the thread is waiting for itself to release the lock it already holds.
- POSIX defines the behavior as **undefined** for `PTHREAD_MUTEX_DEFAULT` type.
- `PTHREAD_MUTEX_ERRORCHECK` type returns `EDEADLK`.
- `PTHREAD_MUTEX_RECURSIVE` type allows re-entrant locking with a depth counter.

> **One-liner:** A double-lock on a non-recursive mutex deadlocks the calling thread; use a recursive mutex or refactor to avoid re-entrant locking.

---

## Q5. When would you use a spinlock over a mutex?

**Key facts:**
- A spinlock is appropriate when the critical section is measured in **nanoseconds** — shorter than a context switch.
- Spinlocks are **mandatory** in interrupt handlers and kernel code where sleeping is forbidden.
- On a **uniprocessor**, a spinlock is dangerous: the holder cannot run while you spin, guaranteeing a deadlock.
- On multiprocessors with short hold times, a spinlock avoids the ~1–10 µs context-switch cost.

**Common wrong answer:** "Spinlocks are always faster."

> **One-liner:** Use a spinlock in kernel/interrupt context or for nanosecond-duration critical sections on a multiprocessor; for any significant hold time, a mutex's ability to sleep the waiter is far more efficient.

---

## Q6. How does `pthread_cond_wait` relate to a mutex?

**Key facts:**
- `pthread_cond_wait(&cond, &mtx)` atomically releases `mtx` and puts the thread to sleep.
- When signaled, the thread **reacquires** `mtx` before returning.
- The condition must **always** be checked in a `while` loop to handle spurious wakeups.
- The mutex prevents the race between checking the condition and calling wait (the lost-wakeup problem).

```c
// Correct pattern
pthread_mutex_lock(&mtx);
while (!condition_is_true()) {
    pthread_cond_wait(&cond, &mtx);  // releases mtx, sleeps, reacquires mtx
}
// condition is now true, mtx is held
pthread_mutex_unlock(&mtx);
```

> **One-liner:** `pthread_cond_wait` atomically releases the mutex and sleeps, preventing the lost-wakeup race; the condition must be re-checked in a while loop after wakeup.

---

## Q7. Explain the convoy effect.

**Key facts:**
- A slow thread holds a lock; many fast threads queue behind it.
- Each waiter incurs a kernel context-switch to be woken, converting an O(1) operation into O(n) per lock release.
- Even after the slow thread finishes, the queued threads run serially — not concurrently.
- Fix: keep critical sections short; never block on I/O while holding a lock; use try-lock with back-off.

> **One-liner:** The convoy effect is the cascading serialization of fast threads queued behind a slow lock holder — the cure is minimizing lock hold time and avoiding blocking calls inside critical sections.

---

## Rapid-Fire Facts

| Question | Answer |
|---|---|
| Who can unlock a mutex? | Only the thread that locked it |
| Who can signal a semaphore? | Any thread |
| What is a counting semaphore? | A semaphore with initial value N, limiting N concurrent accesses |
| What does sem_wait do if value is 0? | Blocks the calling thread |
| What is a monitor? | A mutex + one or more condition variables bundled with shared data |
| What is lock convoying? | Fast threads queuing serially behind a slow lock holder |
