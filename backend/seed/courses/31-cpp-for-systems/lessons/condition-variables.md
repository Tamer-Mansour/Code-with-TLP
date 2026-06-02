# Condition Variables and Producer-Consumer

A mutex protects shared data, but it cannot efficiently **wait for a condition** — a thread would have to spin in a loop checking the condition while holding or releasing the mutex repeatedly. A **condition variable** solves this: it lets a thread atomically release a mutex and sleep, waking only when another thread signals that the condition may be true.

## The Core API

```cpp
#include <condition_variable>
#include <mutex>

std::mutex mtx;
std::condition_variable cv;
bool condition = false;

// Waiting thread
void waiter() {
    std::unique_lock<std::mutex> lk(mtx);
    cv.wait(lk, []{ return condition; });  // predicate form
    // condition is true here, mutex is re-locked
}

// Notifying thread
void notifier() {
    {
        std::lock_guard<std::mutex> lk(mtx);
        condition = true;
    }
    cv.notify_one();  // wake one waiter
}
```

`cv.wait(lk, predicate)` is equivalent to:

```cpp
while (!predicate()) {
    cv.wait(lk);  // atomically unlocks lk and sleeps
}
// woke up: lk re-locked, predicate true
```

Always use the predicate form to handle **spurious wakeups** — `wait()` may return without `notify_one()` being called on some implementations.

## Producer-Consumer Queue

The canonical use case: one thread produces items, another consumes them, and the consumer should sleep when the queue is empty.

```cpp
#include <condition_variable>
#include <deque>
#include <iostream>
#include <mutex>
#include <thread>

std::mutex mtx;
std::condition_variable cv;
std::deque<int> queue;
bool done = false;

void producer() {
    for (int i = 0; i < 10; ++i) {
        {
            std::lock_guard<std::mutex> lk(mtx);
            queue.push_back(i);
            std::cout << "Produced: " << i << '\n';
        }
        cv.notify_one();  // wake consumer
    }
    {
        std::lock_guard<std::mutex> lk(mtx);
        done = true;
    }
    cv.notify_all();  // wake consumer to check done flag
}

void consumer() {
    while (true) {
        std::unique_lock<std::mutex> lk(mtx);
        cv.wait(lk, []{ return !queue.empty() || done; });

        while (!queue.empty()) {
            int item = queue.front();
            queue.pop_front();
            lk.unlock();                // release while processing
            std::cout << "Consumed: " << item << '\n';
            lk.lock();                  // re-acquire to check queue
        }

        if (done) break;
    }
}

int main() {
    std::thread t_prod(producer);
    std::thread t_cons(consumer);
    t_prod.join();
    t_cons.join();
}
```

## notify_one vs notify_all

| Method | Effect |
|---|---|
| `cv.notify_one()` | Wakes at most one waiting thread — use when only one thread can make progress |
| `cv.notify_all()` | Wakes all waiting threads — use when multiple threads may be able to proceed, or when broadcasting a state change |

Calling notify while **not** holding the mutex is legal and often preferred for performance, but requires care to avoid a missed wakeup race (notify arrives before the waiter calls `wait`). The predicate loop handles this correctly.

## std::condition_variable_any

`std::condition_variable` only works with `std::unique_lock<std::mutex>`. `std::condition_variable_any` works with any lock type (e.g., a shared lock for reader-writer patterns) at a small extra cost.

## Timed Wait

```cpp
auto deadline = std::chrono::steady_clock::now() + std::chrono::seconds(5);

std::unique_lock<std::mutex> lk(mtx);
bool ok = cv.wait_until(lk, deadline, []{ return ready; });
if (!ok) {
    // timed out
}
```

## Common Mistakes

- **Missing predicate:** without the lambda, spurious wakeups silently pass the wait.
- **Notifying inside the lock:** legal but can cause the woken thread to immediately block again trying to reacquire the mutex. Move `notify_one()` outside the lock when possible.
- **Using `lock_guard` with `cv.wait`:** `wait` must unlock the mutex, so it requires `unique_lock`. `lock_guard` doesn't support unlock.

```cpp
// WRONG — lock_guard cannot be passed to cv.wait
std::lock_guard<std::mutex> lk(mtx);
cv.wait(lk, predicate);  // compile error
```

> **Interview answer:** A condition variable allows a thread to atomically release a mutex and sleep until another thread calls `notify_one()` or `notify_all()`. Always use the predicate form of `wait()` to handle spurious wakeups. It pairs with `std::unique_lock` (not `lock_guard`) because `wait()` must temporarily release the mutex.
