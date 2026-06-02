# Avoiding Deadlock: Lock Ordering and std::scoped_lock

Deadlock prevention is preferable to detection. The two most practical strategies in C++ are **consistent lock ordering** and using `std::scoped_lock` to atomically acquire multiple mutexes.

## Strategy 1: Consistent Lock Ordering

If every thread always acquires mutexes in the same global order, a circular wait cannot form — breaking Coffman condition #4.

```cpp
std::mutex mtx_a;
std::mutex mtx_b;

// ALWAYS acquire in the order: A then B
void thread1() {
    std::lock_guard la(mtx_a);  // 1st
    std::lock_guard lb(mtx_b);  // 2nd
    // work...
}

void thread2() {
    std::lock_guard la(mtx_a);  // 1st — same order!
    std::lock_guard lb(mtx_b);  // 2nd
    // work...
}
```

Thread 2 now blocks at `mtx_a` if Thread 1 holds it. Thread 1 can complete its work and release both locks. No cycle forms.

**Enforcing ordering in large codebases:** assign each mutex a numeric priority and document it in comments or a header. Code review should verify lock acquisition order.

## Strategy 2: std::lock (C++11)

`std::lock(m1, m2, ...)` acquires multiple mutexes **atomically** — it will not leave some locked and others unlocked if blocking is required. It uses a deadlock-avoidance algorithm internally (often try-lock-and-back-off).

```cpp
#include <mutex>

std::mutex mtx_a, mtx_b;

void safe_transfer() {
    // Acquire both without deadlock risk — order doesn't matter
    std::lock(mtx_a, mtx_b);

    // Adopt ownership into lock_guards so they RAII-unlock
    std::lock_guard la(mtx_a, std::adopt_lock);
    std::lock_guard lb(mtx_b, std::adopt_lock);

    // work with both locks held...
}
```

`std::adopt_lock` tells `lock_guard` that the mutex is already locked — don't lock again, just take ownership for RAII release.

## Strategy 3: std::scoped_lock (C++17) — Preferred

`std::scoped_lock` is the clean C++17 solution. It accepts any number of mutexes, acquires them all atomically (same deadlock-free algorithm as `std::lock`), and releases them all on destruction.

```cpp
#include <mutex>

std::mutex mtx_a, mtx_b;

void safe_transfer() {
    std::scoped_lock lock(mtx_a, mtx_b);  // acquire both atomically
    // work...
}  // both released here
```

This replaces the verbose `std::lock` + `adopt_lock` pattern. For a single mutex, it degenerates to the same behavior as `lock_guard`.

## Lock Hierarchies

A more formal version of lock ordering is a **mutex hierarchy** — mutexes are assigned numeric levels, and threads may only acquire a mutex at a level strictly lower than any mutex they currently hold.

```cpp
// Pseudo-code: enforce at runtime with thread_local tracking
class hierarchical_mutex {
    int level;
    // compare against thread_local current_level before locking
};
```

Anthony Williams's book *C++ Concurrency in Action* includes a full implementation.

## Avoiding Hold-and-Wait

Another approach: never hold one lock while trying to acquire another. Structure code so that all required locks are acquired at the start of the operation, or use `try_lock` and back off completely if any lock is unavailable.

```cpp
bool try_transfer() {
    std::unique_lock la(mtx_a, std::try_to_lock);
    std::unique_lock lb(mtx_b, std::try_to_lock);

    if (!la.owns_lock() || !lb.owns_lock()) {
        return false;  // back off, retry later
    }
    // proceed with work
    return true;
}
```

## Summary of Strategies

| Strategy | Breaks Coffman Condition | Notes |
|---|---|---|
| Global lock ordering | Circular wait (#4) | Simple, but requires discipline |
| `std::scoped_lock` | Circular wait (#4) | Best practice in modern C++ |
| Try-lock and back-off | Hold and wait (#2) | Can cause livelock if not randomized |
| Single lock for all shared state | Hold and wait (#2) | Simplest but limits parallelism |

> **Interview answer:** The cleanest deadlock prevention in C++ is `std::scoped_lock`, which acquires multiple mutexes atomically using a deadlock-avoidance algorithm. Alternatively, enforce a strict global lock acquisition order across the codebase so a circular wait can never form.
