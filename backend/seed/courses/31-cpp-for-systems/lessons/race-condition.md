# What Is a Race Condition?

A **race condition** occurs when the correctness of a program depends on the relative timing or interleaving of two or more threads. If the "wrong" thread wins the race, the program produces incorrect results — and the bug may appear only rarely, making it notoriously hard to reproduce.

## The Classic Counter Race

```cpp
#include <iostream>
#include <thread>

int counter = 0;

void increment() {
    for (int i = 0; i < 100'000; ++i) {
        counter++;  // looks atomic — it is NOT
    }
}

int main() {
    std::thread t1(increment);
    std::thread t2(increment);
    t1.join();
    t2.join();
    std::cout << counter << '\n';  // almost never 200,000
}
```

The expected output is `200000`, but you will typically see something like `137842` — different every run.

## Why `counter++` Is Not Atomic

The expression `counter++` compiles to three machine instructions:

```asm
mov  eax, [counter]   ; 1. LOAD value from memory
inc  eax              ; 2. INCREMENT in register
mov  [counter], eax   ; 3. STORE back to memory
```

When two threads execute this sequence, the CPU can interleave them in any order:

```
Thread 1: LOAD  (reads 5)
Thread 2: LOAD  (reads 5)   ← both see the same value
Thread 1: INC → 6
Thread 2: INC → 6
Thread 1: STORE 6
Thread 2: STORE 6           ← one increment is lost!
```

The net result: two increments happened, but the counter only advanced by one. This is called a **lost update**.

## Data Race vs Race Condition

These terms are often used interchangeably but have a technical distinction:

| Term | Meaning |
|---|---|
| **Data race** | Two threads access the same memory location concurrently, at least one writes, and there is no synchronization. This is **undefined behavior** in C++. |
| **Race condition** | A logic bug where output depends on thread scheduling. Can occur even with proper synchronization (e.g., check-then-act patterns). |

A data race is always undefined behavior. A race condition is a logical bug that may or may not involve a data race.

## Check-Then-Act: A Higher-Level Race

```cpp
// Even with atomic individual operations, this is still a race:
if (cache.contains(key)) {         // check
    return cache.get(key);         // act  ← another thread may delete key here!
}
```

The gap between the check and the act is called a **TOCTOU** (time-of-check to time-of-use) window. The fix requires holding a lock across both operations.

## Detecting Race Conditions

**ThreadSanitizer (TSan)** is the best tool for catching data races at runtime:

```bash
# Compile with TSan instrumentation
g++ -fsanitize=thread -g -o my_program my_program.cpp
./my_program
# TSan prints a detailed race report if one is detected
```

TSan reports include which threads accessed what memory and from which call stacks.

## How to Fix a Race Condition

1. **Mutex** — surround the critical section with a lock (covered in the next lesson).
2. **Atomic operations** — use `std::atomic<int>` for simple integer operations.
3. **Message passing** — threads never share mutable state; communicate by sending data.
4. **Immutable data** — const/read-only data can be shared freely.

```cpp
#include <atomic>
std::atomic<int> counter{0};

void safe_increment() {
    for (int i = 0; i < 100'000; ++i) {
        counter++;  // atomic read-modify-write, no data race
    }
}
```

## Key Signs of a Race Condition in Code Reviews

- Shared mutable global or member variables accessed from multiple threads
- `if (flag) { use(flag); }` pattern without a lock held across both
- Thread that modifies a container while another iterates it
- Lazy initialization without `std::call_once` or a mutex

> **Interview answer:** A race condition is a bug where two threads access shared mutable state without synchronization, so the result depends on execution order. In C++, any unsynchronized concurrent write (or write+read) to the same object is undefined behavior — a data race. Fix it with a mutex, `std::atomic`, or by eliminating shared mutable state.
