# Interview Drill: Classic Synchronization Problems

This lesson condenses the four canonical synchronization problems into crisp answers and decision frameworks you can deploy under interview pressure. Each section follows the same pattern: restate the problem, name the correct primitive, give the one-line answer, then flag the pitfall the interviewer is likely probing for.

## Quick-Reference Table

| Problem | Core challenge | Key primitives | Classic pitfall |
|---------|---------------|----------------|-----------------|
| Producer-Consumer | Block on full/empty | 3 semaphores or mutex + 2 CVs | Locking mutex before counting semaphore → deadlock |
| Readers-Writers | Concurrent reads, exclusive writes | reader_count + write_lock | Writer starvation (readers-preferred) |
| Dining Philosophers | Circular wait on forks | Asymmetric order or room semaphore | All grab left fork → deadlock |
| Barrier | All threads reach phase boundary | Mutex + CV broadcast, or 2 turnstiles | Using `signal` instead of `broadcast` |

## 1. Producer-Consumer

**One-line answer**: Three semaphores — `empty` (N), `full` (0), `mutex` (1) — where producers wait on `empty` and signal `full`, consumers do the reverse, both hold `mutex` only while touching the buffer.

**Probe pitfall**: "What happens if the producer acquires `mutex` before `empty`?" → deadlock: the producer blocks inside the lock; the consumer can never free a slot because it cannot acquire `mutex`.

**Follow-up**: "Can you use condition variables instead?" → Yes. Replace `empty`/`full` with two `pthread_cond_t` variables (`not_full`, `not_empty`). Always use `while`, never `if`, around `cond_wait` to handle spurious wakeups.

## 2. Readers-Writers

**One-line answer**: A `reader_count` integer (protected by `mutex`) determines whether readers or writers hold `write_lock`; the first reader acquires it, the last reader releases it; writers compete for it directly.

**Probe pitfall**: "In the readers-preferred solution, can a writer starve?" → Yes. A steady stream of readers keeps `reader_count > 0`, so `write_lock` is never released.

**Fix in one sentence**: Add a turnstile semaphore that every thread must pass; a waiting writer holds the turnstile, blocking new readers behind it.

**Real-world callout**: `std::shared_mutex` (C++17) and `pthread_rwlock_t` both implement readers-writers. Prefer them over hand-rolling.

## 3. Dining Philosophers

**One-line answer**: The naive solution deadlocks because all five philosophers grab their left fork simultaneously, forming a circular wait; break it by either (a) making one philosopher pick up forks in reverse order, or (b) allowing at most N-1 philosophers to compete at once.

**Probe pitfall**: "What is livelock?" → Each philosopher picks up their left fork, sees the right is unavailable, puts the left back, waits, and retries — everyone is active, nobody progresses. Adding random backoff reduces but does not eliminate livelock; a proper solution needs the room semaphore or asymmetric ordering.

**State machine answer**: The most correct solution tracks each philosopher's state (`THINKING / HUNGRY / EATING`) in a monitor and only grants both forks when neither neighbor is `EATING`. This is deadlock-free and starvation-free.

## 4. Barriers

**One-line answer**: A barrier blocks every thread until all N threads have arrived, then releases all of them simultaneously; implemented with a counter, a mutex, and `cond_broadcast` (not `cond_signal`).

**Probe pitfall**: "What goes wrong if you use `cond_signal` instead of `cond_broadcast`?" → Only one waiting thread is woken; the rest sleep forever.

**Reusability pitfall**: A single-phase barrier (counter never resets) fails on the second use — all threads pass immediately because the counter is already 0. Fix: use a generation counter or two-turnstile design to reset state after each barrier crossing.

## Pattern Recognition Cheat Sheet

- **"Threads must not overlap in a region"** → mutex / binary semaphore
- **"Block until resource is available (counting)"** → counting semaphore
- **"Block until a condition is true (complex predicate)"** → condition variable + mutex
- **"All threads must reach point X before any continues"** → barrier
- **"Concurrent reads, exclusive writes"** → readers-writers lock (`shared_mutex`)
- **"Fixed-capacity shared queue"** → producer-consumer with 3 semaphores

## Final Interview Tip

When asked to design a synchronization solution, always state:
1. What the shared state is.
2. Which invariants must hold.
3. Which primitive enforces each invariant.
4. What happens in the boundary cases (empty, full, 0 readers, last thread at barrier).

Examiners reward structured thinking over memorized code.
