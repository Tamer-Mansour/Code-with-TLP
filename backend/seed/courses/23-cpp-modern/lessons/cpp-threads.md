# Concurrency: Threads, Mutexes, and Futures

C++11 added a portable threading model to the standard library. You no longer need platform-specific APIs (pthreads on POSIX, Win32 threads on Windows) for basic concurrency.

## std::thread

```cpp
#include <thread>
#include <iostream>

void worker(int id) {
    std::cout << "Thread " << id << " running\n";
}

int main() {
    std::thread t1(worker, 1);
    std::thread t2(worker, 2);

    t1.join();   // wait for t1 to finish
    t2.join();
}
```

Key rules:
- A `std::thread` object must be joined or detached before it is destroyed; otherwise `std::terminate` is called.
- Use `t.detach()` only for true "fire and forget" background tasks.
- Pass arguments by value or use `std::ref`/`std::cref` for references.

## Data Races and Mutexes

A **data race** is undefined behavior: two threads accessing the same memory concurrently where at least one is writing. Use a mutex to protect shared state:

```cpp
#include <mutex>

std::mutex mtx;
int counter = 0;

void increment(int times) {
    for (int i = 0; i < times; ++i) {
        std::lock_guard<std::mutex> lock(mtx);
        ++counter;   // protected
    }
}
```

`std::lock_guard` locks on construction and unlocks when it goes out of scope (RAII). Prefer it over manual `lock()`/`unlock()`.

### Mutex Types

| Type | Use case |
|------|---------|
| `std::mutex` | Basic exclusive lock |
| `std::recursive_mutex` | Same thread may lock multiple times |
| `std::shared_mutex` | Multiple readers OR one writer (C++17) |
| `std::timed_mutex` | Try-lock with timeout |

## std::condition_variable

Used to block a thread until a condition is signaled:

```cpp
#include <condition_variable>
#include <queue>

std::queue<int> workQueue;
std::mutex qMutex;
std::condition_variable cv;

void producer() {
    for (int i = 0; i < 5; ++i) {
        {
            std::lock_guard<std::mutex> lock(qMutex);
            workQueue.push(i);
        }
        cv.notify_one();
    }
}

void consumer() {
    while (true) {
        std::unique_lock<std::mutex> lock(qMutex);
        cv.wait(lock, []{ return !workQueue.empty(); });
        int val = workQueue.front();
        workQueue.pop();
        std::cout << "Consumed: " << val << "\n";
        if (val == 4) break;
    }
}
```

## std::future and std::async

`std::async` runs a callable asynchronously and returns a `std::future` that holds the result:

```cpp
#include <future>
#include <numeric>

int sumRange(int start, int end) {
    int total = 0;
    for (int i = start; i <= end; ++i) total += i;
    return total;
}

int main() {
    // Launch on a new thread (or thread pool, implementation-defined)
    auto f1 = std::async(std::launch::async, sumRange, 1,    500'000);
    auto f2 = std::async(std::launch::async, sumRange, 500'001, 1'000'000);

    int total = f1.get() + f2.get();   // blocks until both finish
    std::cout << "Sum 1-1000000: " << total << "\n";   // 500000500000
}
```

`f.get()` retrieves the result and re-throws any exception thrown by the async task.

## std::atomic

For single-variable lock-free access:

```cpp
#include <atomic>

std::atomic<int> hitCount{0};

void handler() {
    hitCount.fetch_add(1, std::memory_order_relaxed);
}
```

`std::atomic<T>` works with integral types and pointers. It does not replace mutexes for compound operations.

## Thread Safety Checklist

- Protect shared mutable state with a mutex.
- Prefer `lock_guard` / `scoped_lock` over manual lock/unlock.
- Avoid holding locks across I/O or expensive computation.
- Use `std::atomic` for simple counters and flags.
- Test under thread sanitizer (`-fsanitize=thread`) to catch races.
