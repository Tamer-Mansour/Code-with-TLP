# Spinlock vs Mutex: Busy-Wait vs Block

Both spinlocks and mutexes provide mutual exclusion. The difference is entirely about **what a thread does while waiting**: a spinlock keeps the CPU spinning in a tight loop; a mutex yields the CPU and sleeps. This distinction has profound performance implications.

## The Spinlock

A spinlock is implemented with a single atomic flag. A thread acquiring the lock loops (spins) until the flag flips from "taken" to "free":

```c
// Simplified spinlock using GCC builtins
typedef volatile int spinlock_t;

void spin_lock(spinlock_t *lock) {
    while (__sync_lock_test_and_set(lock, 1)) {
        // spin: keep trying until we read 0 and set it to 1 atomically
        while (*lock) { /* yield hint optional: _mm_pause() on x86 */ }
    }
}

void spin_unlock(spinlock_t *lock) {
    __sync_lock_release(lock);  // atomic store of 0
}
```

On x86, the `LOCK XCHG` or `LOCK CMPXCHG` instruction makes the test-and-set atomic across all cores.

## The Blocking Mutex

A mutex suspends the thread when the lock is unavailable:

```
Thread calls lock():
  - Attempt atomic test-and-set
  - If fail → syscall into kernel → thread moved to WAITING queue
  - CPU given to another thread
Thread wakes when the holder calls unlock():
  - Kernel picks one waiter → moves it to READY
  - Thread re-attempts the acquisition
```

## Cost Comparison

| Factor | Spinlock | Mutex |
|---|---|---|
| Lock overhead (uncontended) | ~2–10 ns (a few atomic ops) | ~25–100 ns (user-space futex fast path) |
| Lock overhead (contended) | Burns CPU cycles | Context switch cost ~1–10 µs |
| CPU consumption while waiting | 100% of the core | 0% (thread is asleep) |
| Appropriate hold time | Nanoseconds to microseconds | Microseconds to seconds |
| Usable in interrupt context | Yes | No (sleeping is forbidden) |
| Works on uniprocessor | No (dangerous — spins forever) | Yes |

## When to Use a Spinlock

- **Critical sections measured in nanoseconds**: If the lock is typically held for fewer cycles than a context switch takes, spinning is cheaper than sleeping.
- **Interrupt handlers and kernel code**: Sleeping inside an interrupt handler is illegal. The kernel uses spinlocks extensively for this reason.
- **Multiprocessor only**: On a single CPU, spinning blocks the holder from running, causing a guaranteed deadlock. Spinlocks are meaningless on uniprocessors.

```c
// Linux kernel pattern — disables interrupts + acquires spinlock
unsigned long flags;
spin_lock_irqsave(&my_lock, flags);
/* critical section — cannot sleep here */
spin_unlock_irqrestore(&my_lock, flags);
```

## When to Use a Mutex

- **Lock held for any significant time** (file I/O, database queries, anything measured in microseconds or longer).
- **User-space applications**: Spinning wastes battery and starves other threads sharing the core.
- **When fairness matters**: Mutex implementations often include queues with fairness guarantees; spinlocks do not.

## The Hybrid: Adaptive Mutex

Modern OS kernels (Linux, macOS, Solaris) use **adaptive mutexes**: spin briefly (a few hundred cycles) hoping the holder finishes, then sleep if not. This captures the best of both worlds for typical mutex contention patterns.

```
Adaptive mutex lock():
  attempt atomic CAS
  if fail:
    spin for N cycles watching the owner's run state
    if owner is running: keep spinning (it will release soon)
    if owner is descheduled: go to sleep (it won't release soon)
```

## Worked Example — Choosing the Right Primitive

```cpp
// Global statistics counter updated on every packet received
// Critical section: one integer increment — nanoseconds
std::atomic<int> packet_count;  // even better: use atomics directly

// File cache: may require disk I/O while holding the lock
std::mutex file_cache_mtx;  // correct: block other threads, don't spin

// Kernel network driver interrupt handler updating a ring buffer index
spinlock_t ring_lock;  // must use spinlock; cannot sleep in IRQ
```

## Key Pitfalls

- **Spinlock on a uniprocessor**: the holder cannot run while you spin — instant deadlock.
- **Holding a spinlock during a blocking call** (e.g., `read()`, `malloc()`): the holder sleeps while others spin — terrible performance.
- **Priority inversion with spinlocks**: a low-priority thread holding the lock is preempted; high-priority threads spin forever. Many spinlock implementations disable preemption to prevent this.

> **Interview answer:** A spinlock burns CPU cycles polling the lock flag and is appropriate for nanosecond-duration critical sections or interrupt context where sleeping is forbidden. A mutex puts the waiting thread to sleep, incurring a context-switch cost, but is correct whenever the lock may be held for any meaningful duration.
