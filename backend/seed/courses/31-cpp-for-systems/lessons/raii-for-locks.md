# RAII for Locks and Critical Sections

A mutex that is acquired but never released causes deadlock. In multi-threaded system code this bug is especially insidious: it may appear only under load, only on certain paths through the code, or only when an exception is thrown inside a critical section. RAII lock guards make "unlock on every exit" automatic.

## The Classic Problem

```cpp
std::mutex mtx;
int shared_counter = 0;

void increment() {
    mtx.lock();
    if (shared_counter > 1000)
        return;          // BUG: mutex never unlocked
    ++shared_counter;
    mtx.unlock();
}
```

The early return forgets to call `unlock`. Every thread that later tries to acquire `mtx` will block forever.

## `std::lock_guard` — The Simplest Fix

```cpp
#include <mutex>

void increment() {
    std::lock_guard<std::mutex> guard(mtx);  // locks in constructor
    if (shared_counter > 1000)
        return;          // guard's destructor unlocks — safe
    ++shared_counter;
}                        // guard destroyed here — unlocks if not already
```

`std::lock_guard` is non-copyable, non-movable, and has no `unlock` method. Its simplicity is a feature: there is nothing you can do wrong except fail to create it.

## `std::unique_lock` — Flexible Ownership

When you need to unlock early, re-lock, or transfer lock ownership to another scope:

```cpp
void conditional_work() {
    std::unique_lock<std::mutex> lk(mtx);

    if (!data_ready) {
        lk.unlock();        // release while waiting for I/O
        fetch_data();
        lk.lock();          // re-acquire
    }

    process();
}   // unlocks in destructor regardless of which path was taken
```

`std::unique_lock` also supports deferred locking and timed locking:

```cpp
// Try to acquire within 100 ms; proceed only if successful
std::unique_lock<std::mutex> lk(mtx, std::defer_lock);
if (lk.try_lock_for(std::chrono::milliseconds(100))) {
    // critical section
}
```

## `std::scoped_lock` — Deadlock-Free Multi-Mutex Locking (C++17)

Acquiring two mutexes one at a time risks deadlock if two threads acquire them in opposite order. `std::scoped_lock` acquires all of them atomically using a deadlock-avoidance algorithm:

```cpp
std::mutex mtx_a, mtx_b;

void transfer(Account& a, Account& b, int amount) {
    std::scoped_lock lk(mtx_a, mtx_b);   // both locked, deadlock-free
    a.balance -= amount;
    b.balance += amount;
}   // both unlocked in destructor
```

## Condition Variables Need `unique_lock`

`std::condition_variable::wait` requires a `std::unique_lock` because it must release the mutex while waiting and re-acquire it on wake-up:

```cpp
std::mutex mtx;
std::condition_variable cv;
bool ready = false;

void consumer() {
    std::unique_lock<std::mutex> lk(mtx);
    cv.wait(lk, [] { return ready; });   // atomically unlocks, sleeps, re-locks
    // now holding the lock again
    consume();
}
```

## RAII for Spinlocks and OS Primitives

The same pattern applies to non-standard locks. Wrap any primitive that has acquire/release semantics:

```cpp
// POSIX read-write lock
class ReadLock {
public:
    explicit ReadLock(pthread_rwlock_t& rwl) : rwl_(rwl) {
        pthread_rwlock_rdlock(&rwl_);
    }
    ~ReadLock() noexcept { pthread_rwlock_unlock(&rwl_); }
    ReadLock(const ReadLock&) = delete;
    ReadLock& operator=(const ReadLock&) = delete;
private:
    pthread_rwlock_t& rwl_;
};
```

## Windows Critical Sections

On Windows, `CRITICAL_SECTION` is a fast user-mode lock:

```cpp
class CriticalSectionLock {
public:
    explicit CriticalSectionLock(CRITICAL_SECTION& cs) : cs_(cs) {
        EnterCriticalSection(&cs_);
    }
    ~CriticalSectionLock() noexcept { LeaveCriticalSection(&cs_); }
    CriticalSectionLock(const CriticalSectionLock&) = delete;
private:
    CRITICAL_SECTION& cs_;
};
```

## Key Rules

| Rule | Reason |
|---|---|
| Destructor must be `noexcept` | Throwing during stack unwinding calls `std::terminate` |
| Delete copy constructor | Two guards would double-unlock, causing undefined behavior |
| Keep lock scope as narrow as possible | Reduces contention; never do I/O while holding a mutex |
| Prefer `lock_guard` over `unique_lock` when flexibility is not needed | Communicates intent and prevents misuse |

**Interview answer:** `std::lock_guard` acquires a mutex in its constructor and releases it in its destructor, guaranteeing unlock on every exit path — including exceptions — without any manual `unlock` calls.
