# std::mutex, lock_guard, and unique_lock

A **mutex** (mutual exclusion) is the fundamental primitive for protecting shared data. Only one thread can hold a mutex at a time; others block until it is released. C++ provides several mutex and lock wrapper types to make correct usage ergonomic and exception-safe.

## std::mutex

The basic mutex lives in `<mutex>`. It has two key operations:

- `lock()` — acquires the mutex, blocking if another thread holds it
- `unlock()` — releases the mutex

```cpp
#include <iostream>
#include <mutex>
#include <thread>

int counter = 0;
std::mutex mtx;

void safe_increment() {
    for (int i = 0; i < 100'000; ++i) {
        mtx.lock();
        counter++;    // critical section
        mtx.unlock();
    }
}

int main() {
    std::thread t1(safe_increment);
    std::thread t2(safe_increment);
    t1.join(); t2.join();
    std::cout << counter << '\n';  // always 200000
}
```

Calling `lock()` / `unlock()` manually is error-prone — if an exception is thrown between them, the mutex is never unlocked and every subsequent thread deadlocks. Use RAII wrappers instead.

## std::lock_guard

`std::lock_guard<std::mutex>` locks the mutex on construction and **automatically unlocks** on destruction — RAII at its simplest.

```cpp
void safe_increment() {
    for (int i = 0; i < 100'000; ++i) {
        std::lock_guard<std::mutex> guard(mtx);  // locks here
        counter++;
    }  // guard destroyed → mutex unlocked automatically
}
```

With C++17 class template argument deduction (CTAD):

```cpp
std::lock_guard guard(mtx);  // type deduced
```

`lock_guard` cannot be unlocked early or moved — it holds the lock for exactly the lifetime of the guard object.

## std::unique_lock

`std::unique_lock<std::mutex>` is more flexible than `lock_guard`:

- Can be unlocked and re-locked manually
- Can be moved (transferring ownership)
- Required by `std::condition_variable`
- Supports deferred locking and try-locking

```cpp
#include <mutex>

std::mutex mtx;

void process() {
    std::unique_lock<std::mutex> lk(mtx);

    // do protected work...
    int data = read_shared_data();

    lk.unlock();  // release early if we no longer need the lock
    expensive_computation(data);  // runs without holding the lock

    lk.lock();    // re-acquire to write result
    write_result(data);
}
```

Deferred locking — acquire the mutex at a later point:

```cpp
std::unique_lock<std::mutex> lk(mtx, std::defer_lock);
// ... do non-protected setup ...
lk.lock();  // now acquire
```

## Choosing lock_guard vs unique_lock

| Feature | `lock_guard` | `unique_lock` |
|---|---|---|
| Overhead | Minimal | Slightly higher (stores lock state) |
| Manual unlock | No | Yes |
| Movable | No | Yes |
| Works with `condition_variable` | No | Yes |
| Try-lock support | No | Yes |

**Default choice:** `lock_guard`. Reach for `unique_lock` only when you need the extra capabilities.

## std::recursive_mutex

A thread that tries to lock a regular `std::mutex` it already holds will deadlock. `std::recursive_mutex` allows the same thread to lock multiple times (must unlock the same number of times).

```cpp
std::recursive_mutex rmtx;

void outer() {
    std::lock_guard guard(rmtx);
    inner();  // safe — same thread locks again
}

void inner() {
    std::lock_guard guard(rmtx);  // second lock by same thread — OK
    // ...
}
```

Use recursive mutexes sparingly; they often indicate a design problem.

## std::timed_mutex

Supports `try_lock_for()` and `try_lock_until()` — useful when you want to attempt a lock but fall back to other work rather than blocking indefinitely.

```cpp
std::timed_mutex tmtx;

if (tmtx.try_lock_for(std::chrono::milliseconds(100))) {
    // got the lock within 100 ms
    tmtx.unlock();
} else {
    // lock unavailable — do something else
}
```

## Critical Section Best Practices

- Keep critical sections **short** — hold the lock only while accessing shared data.
- Never call external code (callbacks, I/O) while holding a lock — it may block indefinitely or acquire other locks.
- Prefer returning data from a critical section and processing it outside.

> **Interview answer:** `std::mutex` prevents concurrent access to shared data. Wrap it with `lock_guard` for simple RAII locking (automatically unlocked on scope exit) or `unique_lock` when you need to unlock early or use condition variables. Never call `lock()`/`unlock()` directly — an exception between them leaves the mutex permanently locked.
