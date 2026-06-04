# RAII Lock Manager Trace

This exercise models the RAII pattern as applied to mutexes — one of the most important applications of RAII in production systems code. Rather than just protecting heap memory, you are protecting the invariant that only one thread executes a critical section at a time.

## What You Are Building

Given a trace of `LOCK`, `UNLOCK`, and `WORK` events, maintain state for a set of mutexes and blocked thread queues. Output exactly what a real RAII-aware scheduler would print.

See the prompt for the full command set and output format.

## Key Concepts Exercised

- **RAII for mutexes:** In real C++, `std::lock_guard<std::mutex>` acquires the mutex on construction and releases it when the guard goes out of scope. The trace models this acquire/release lifecycle.
- **Blocking and wakeup:** A thread that cannot acquire a mutex enters a FIFO wait queue. When the holder releases, the first waiter is unblocked automatically — mirroring `std::condition_variable::notify_one()`.
- **Critical section exclusion:** A blocked thread cannot do useful work, so `WORK` commands for blocked threads are silent.

## Suggested Data Structures

```python
from collections import deque

mutex_holder  = {}   # mid -> tid or None
mutex_waiters = {}   # mid -> deque of tids
```

To check if a thread is blocked:

```python
def is_blocked(tid):
    return any(tid in waiters for waiters in mutex_waiters.values())
```

## Why This Matters

The [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines), rule **CP.20**, states:

> Use RAII, never plain `lock()`/`unlock()`.

And **CP.44**:

> Remember to name your `lock_guard`s and `unique_lock`s.

The reason is exactly what this trace demonstrates: if you call `mtx.lock()` manually and then throw an exception or return early, `mtx.unlock()` never runs and every waiting thread blocks forever. `std::lock_guard` ties the unlock to scope exit, making it structurally impossible to forget.

For further reading on the OS theory behind blocking and unblocking, see *Operating Systems: Three Easy Pieces*, Chapter 28 ("Locks") at [https://pages.cs.wisc.edu/~remzi/OSTEP/](https://pages.cs.wisc.edu/~remzi/OSTEP/).
