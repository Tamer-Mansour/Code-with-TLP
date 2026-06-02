# Condition Variables and Monitors

A condition variable lets a thread **wait for a logical condition** to become true — not just for a lock to be available. It solves the classic problem of needing to release a lock, wait for a state change, and reacquire the lock — all atomically from the OS's perspective.

## The Problem They Solve

Suppose a consumer thread must wait until a buffer is non-empty. Without a condition variable, it would have to poll:

```c
// Bad: wastes CPU and holds the lock the whole time
mtx.lock();
while (buffer.empty()) {
    mtx.unlock();
    sleep(1);          // arbitrary delay — either too slow or too wasteful
    mtx.lock();
}
// consume
mtx.unlock();
```

A condition variable makes the wait-and-recheck atomic with respect to the mutex.

## Core API (POSIX)

```c
pthread_mutex_t mtx = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t  cond = PTHREAD_COND_INITIALIZER;

// Consumer: wait until condition is true
pthread_mutex_lock(&mtx);
while (buffer_empty()) {                  // always a while, never if
    pthread_cond_wait(&cond, &mtx);       // atomically: release mtx, sleep, reacquire mtx
}
item = dequeue();
pthread_mutex_unlock(&mtx);

// Producer: signal that condition may have changed
pthread_mutex_lock(&mtx);
enqueue(item);
pthread_cond_signal(&cond);              // wake one waiter
pthread_mutex_unlock(&mtx);
```

`pthread_cond_wait` does three things atomically from the waiting thread's point of view:
1. Release the mutex.
2. Put the thread to sleep on the condition variable's wait queue.
3. When woken, reacquire the mutex before returning.

## Why the `while` Loop Is Mandatory

Condition variables can suffer **spurious wakeups** — a thread can be woken without anyone calling `signal`. Additionally, with multiple consumers, another consumer may have already taken the item between the wakeup and the reacquisition of the lock (the TOCTOU problem). The `while` loop re-checks the condition and re-waits if it is still false.

```cpp
// Correct: always re-check in a while loop
std::unique_lock<std::mutex> lk(mtx);
cv.wait(lk, [] { return !buffer.empty(); });  // C++ lambda condition — wraps the while loop
item = buffer.front();
buffer.pop();
```

## `signal` vs `broadcast`

| Operation | Effect |
|---|---|
| `cond_signal` / `notify_one` | Wakes exactly one waiting thread |
| `cond_broadcast` / `notify_all` | Wakes all waiting threads |

Use `broadcast` when multiple threads might satisfy different conditions after a state change, or when you cannot determine which waiter should proceed. Use `signal` when exactly one consumer should wake per producer event.

## Monitors — The Higher-Level Abstraction

A **monitor** packages a mutex, one or more condition variables, and the shared data they protect into a single object. Languages like Java make every object a monitor:

```java
class BoundedBuffer {
    private final int[] buf;
    private int count = 0;

    synchronized void put(int item) throws InterruptedException {
        while (count == buf.length) wait();   // releases monitor lock, sleeps
        buf[count++] = item;
        notifyAll();                          // wake all waiters
    }

    synchronized int take() throws InterruptedException {
        while (count == 0) wait();
        int item = buf[--count];
        notifyAll();
        return item;
    }
}
```

Java's `synchronized` keyword is the lock; `wait()` is `cond_wait`; `notifyAll()` is `cond_broadcast`.

## Hoare vs Mesa Semantics

- **Hoare monitors**: When a thread signals, the signaler immediately yields to the waiter, which runs and then returns control to the signaler. The waiter is guaranteed the condition holds when it runs — an `if` is safe.
- **Mesa monitors** (used in practice — Linux, Java, pthreads): The woken thread is placed back on the run queue but competes normally. The condition may no longer hold by the time it runs — a `while` loop is mandatory.

## Worked Example — Thread-Safe Queue (C++)

```cpp
#include <mutex>
#include <condition_variable>
#include <queue>

template<typename T>
class SafeQueue {
    std::queue<T>           q;
    std::mutex              mtx;
    std::condition_variable cv;
public:
    void push(T val) {
        {
            std::lock_guard<std::mutex> lk(mtx);
            q.push(std::move(val));
        }
        cv.notify_one();
    }

    T pop() {
        std::unique_lock<std::mutex> lk(mtx);
        cv.wait(lk, [&]{ return !q.empty(); });  // wait until non-empty
        T val = std::move(q.front());
        q.pop();
        return val;
    }
};
```

> **Interview answer:** A condition variable allows a thread to atomically release a mutex and sleep until a logical condition changes, avoiding CPU-wasting busy-wait. The associated mutex must always be held when checking the condition, and the condition must always be re-checked in a `while` loop after wakeup to guard against spurious wakeups and races.
