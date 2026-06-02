# What Is a Mutex and How Does Lock/Unlock Work?

A **mutex** (mutual exclusion lock) is the most fundamental synchronization primitive in concurrent programming. Its single purpose: ensure that only one thread at a time can execute a critical section — a block of code that reads or writes shared state.

## The Core Idea

Imagine two threads both incrementing a shared counter. At the machine level, `counter++` is three instructions: load, add, store. If thread A reads the value, thread B reads the same stale value, both add one, and both store — you lose an update. A mutex prevents this by making the load-add-store sequence appear atomic to other threads.

```cpp
#include <mutex>
#include <thread>

std::mutex mtx;
int counter = 0;

void increment() {
    mtx.lock();       // acquire
    counter++;        // critical section — only one thread here at a time
    mtx.unlock();     // release
}
```

## Lock and Unlock — What Happens Under the Hood

When a thread calls `lock()`:

1. The OS (or the hardware instruction `CMPXCHG` / `LOCK XCHG`) attempts to atomically set the mutex's internal flag from "free" to "owned".
2. If the flag was already "owned", the calling thread is **blocked** — placed on the mutex's wait queue and descheduled.
3. When the owning thread calls `unlock()`, the OS picks one waiter, marks the mutex as owned by that thread, and wakes it.

This blocking behavior distinguishes a mutex from a spinlock (which burns CPU cycles polling).

## Ownership Semantics

A mutex has a strict **owner**: the thread that locked it is the only thread permitted to unlock it. This is a defining property — violating it is undefined behavior in most APIs.

```cpp
// Correct: same thread locks and unlocks
void safe_update() {
    mtx.lock();
    shared_data = compute();
    mtx.unlock();
}

// Wrong: thread A locks, thread B unlocks — undefined behavior
```

## RAII — The Right Way in C++

Manual `lock()`/`unlock()` is error-prone (exceptions skip the unlock). Use `std::lock_guard` or `std::unique_lock`:

```cpp
void increment() {
    std::lock_guard<std::mutex> guard(mtx);  // locks on construction
    counter++;
    // unlocks automatically when guard goes out of scope
}
```

## Common Pitfalls

| Pitfall | Consequence |
|---|---|
| Forgetting to unlock | Deadlock — other threads block forever |
| Holding a lock too long | High contention, poor throughput |
| Locking the wrong mutex | Data race still occurs |
| Nested lock of the same non-recursive mutex | Deadlock on the same thread |

## Worked Example — Bank Transfer

```cpp
std::mutex account_mtx;
double balance = 1000.0;

void withdraw(double amount) {
    std::lock_guard<std::mutex> lk(account_mtx);
    if (balance >= amount) {
        balance -= amount;
    }
}
```

Without the mutex, two concurrent withdrawals could both pass the `balance >= amount` check before either decrements — an overdraft race condition.

## Key Facts for Interviews

- A mutex is **not** a counter — it is either locked or unlocked.
- Only the **owning thread** can release it.
- Blocked threads are put to **sleep** (context switch), making mutex acquisition relatively expensive compared to a spinlock for very short critical sections.
- In Linux, the fast path uses `futex` (fast userspace mutex): the lock/unlock is a single atomic operation in userspace when there is no contention; the kernel is involved only when a thread must sleep.

> **Interview answer:** A mutex guarantees mutual exclusion by allowing only one thread to hold the lock at a time; it has ownership semantics — the locker must be the unlocker — and blocked threads sleep rather than spin.
