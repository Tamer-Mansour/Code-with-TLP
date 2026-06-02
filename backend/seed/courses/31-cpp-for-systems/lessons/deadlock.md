# Deadlock: Causes and the Four Coffman Conditions

A **deadlock** is a state in which two or more threads are each waiting for a resource held by another, causing all of them to block forever. The program does not crash — it silently hangs. Deadlocks are among the hardest bugs to reproduce and diagnose because they often depend on precise timing.

## A Classic Two-Thread Deadlock

```cpp
#include <mutex>
#include <thread>

std::mutex mtx_a;
std::mutex mtx_b;

void thread1() {
    std::lock_guard<std::mutex> la(mtx_a);  // acquires A
    std::this_thread::sleep_for(std::chrono::milliseconds(1));
    std::lock_guard<std::mutex> lb(mtx_b);  // waits for B — BLOCKED
}

void thread2() {
    std::lock_guard<std::mutex> lb(mtx_b);  // acquires B
    std::this_thread::sleep_for(std::chrono::milliseconds(1));
    std::lock_guard<std::mutex> la(mtx_a);  // waits for A — BLOCKED
}

int main() {
    std::thread t1(thread1);
    std::thread t2(thread2);
    t1.join();  // hangs forever
    t2.join();
}
```

Thread 1 holds A and waits for B. Thread 2 holds B and waits for A. Neither can proceed.

## The Four Coffman Conditions

In 1971, Edward Coffman and colleagues identified four **necessary and sufficient** conditions for deadlock. All four must hold simultaneously for deadlock to occur. Eliminating any one prevents it.

### 1. Mutual Exclusion

At least one resource must be non-shareable — only one thread can use it at a time.

- Mutexes, file write locks, and hardware devices are typical examples.
- Read-only resources shared freely cannot cause deadlock.

### 2. Hold and Wait

A thread holds at least one resource while waiting to acquire additional resources held by other threads.

```cpp
// Thread holds mtx_a and waits for mtx_b — classic hold-and-wait
std::lock_guard la(mtx_a);
std::lock_guard lb(mtx_b);  // block while holding la
```

### 3. No Preemption

Resources cannot be forcibly taken from a thread. A thread must voluntarily release what it holds.

- OS schedulers do not preempt mutexes — a thread that hangs while holding a lock keeps it.
- Some higher-level systems (databases) implement preemption via transaction rollback.

### 4. Circular Wait

There must be a circular chain of two or more threads, each waiting for a resource held by the next thread in the chain.

```
Thread 1 → waits for mtx_b (held by Thread 2)
Thread 2 → waits for mtx_a (held by Thread 1)
```

Visually, this forms a cycle in the **resource allocation graph**.

## Deadlock vs Livelock vs Starvation

| Condition | Description |
|---|---|
| **Deadlock** | Threads block forever, making no progress |
| **Livelock** | Threads keep changing state in response to each other but make no real progress (like two people stepping aside for each other repeatedly) |
| **Starvation** | One thread never gets scheduled, even though others make progress |

## Detecting Deadlock

- **Linux:** `gdb` attached to a hung process → `info threads` → `thread apply all bt` shows each thread's backtrace and what lock it is waiting on.
- **Helgrind** (Valgrind tool): detects lock ordering violations that *can* deadlock, even if they have not yet.
- **ThreadSanitizer (TSan):** can detect some deadlock-prone patterns.

```bash
g++ -fsanitize=thread -g -o prog prog.cpp
./prog
```

## Why Deadlock Is Insidious

- It may only occur under high load or specific timing windows.
- Test environments often differ from production in thread count and scheduling policy.
- Adding logging or debug prints changes timing and can make the deadlock disappear (a **Heisenbug**).

> **Interview answer:** Deadlock requires all four Coffman conditions simultaneously: mutual exclusion, hold-and-wait, no preemption, and circular wait. Break any one — for example, acquire all locks at once in a fixed global order — and deadlock cannot occur.
