# What Is a Race Condition?

A **race condition** occurs when the correctness of a program depends on the relative timing or interleaving of multiple threads or processes. When two or more threads access shared data concurrently and at least one of them writes to it, the final result can vary non-deterministically — depending on who "wins the race."

Race conditions are among the most dangerous bugs in systems programming. They are notoriously hard to reproduce because they only manifest under specific scheduling conditions, and they can lie dormant for years before causing a production failure.

## A Classic Example

Consider two threads, each incrementing a shared counter:

```c
// Shared global
int counter = 0;

// Thread A and Thread B both execute this:
void increment() {
    counter = counter + 1;
}
```

Intuitively, if both threads call `increment()` once each, you'd expect `counter` to be `2`. But the result can be `1`. Here's why.

The statement `counter = counter + 1` is **not a single hardware instruction** on most architectures. It compiles to three steps:

1. **Load** — read `counter` from memory into a CPU register.
2. **Add** — compute `register + 1`.
3. **Store** — write the result back to memory.

A dangerous interleaving looks like this:

| Step | Thread A                   | Thread B                   | counter (in memory) |
|------|----------------------------|----------------------------|---------------------|
| 1    | Load counter → reg = 0     |                            | 0                   |
| 2    |                            | Load counter → reg = 0     | 0                   |
| 3    | Add: reg = 0 + 1 = 1       |                            | 0                   |
| 4    |                            | Add: reg = 0 + 1 = 1       | 0                   |
| 5    | Store: counter = 1         |                            | 1                   |
| 6    |                            | Store: counter = 1         | 1                   |

Thread B's store overwrites Thread A's result. One increment is silently **lost**.

## Why Race Conditions Are Hard to Find

- They are **timing-dependent**: a race might only trigger under heavy load or a specific CPU frequency.
- They often **pass unit tests** because tests run in a controlled, low-concurrency environment.
- They can produce **undefined behavior** in C/C++ (data races are undefined behavior, meaning the compiler is permitted to generate arbitrary code).
- **Heisenbugs**: adding print statements or a debugger changes timing, often making the race disappear.

## Common Sources

- Shared mutable state without synchronization (counters, flags, caches, linked lists).
- Check-then-act patterns: `if (file_exists()) { open(file); }` — the file can disappear between the check and the act.
- Lazy initialization without locks.
- Signal handlers that modify global state accessed by the main thread.

## Detecting Race Conditions

| Tool / Technique | Description |
|---|---|
| **ThreadSanitizer (TSan)** | Compiler instrumentation that detects data races at runtime (Clang/GCC `-fsanitize=thread`) |
| **Helgrind / DRD** | Valgrind tools for race detection |
| **Code review** | Look for shared state accessed in multiple threads without locks |
| **Stress testing** | Run many threads in tight loops; increase the chance of bad interleavings |

```bash
# Compile with ThreadSanitizer
gcc -fsanitize=thread -g -o prog prog.c -lpthread
./prog
```

## The Fix

A race condition is fixed by ensuring that the conflicting operations happen **atomically** — as an indivisible unit — or are **serialized** through a synchronization primitive like a mutex.

```c
#include <pthread.h>

pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;
int counter = 0;

void increment() {
    pthread_mutex_lock(&lock);
    counter = counter + 1;   // now inside critical section
    pthread_mutex_unlock(&lock);
}
```

> **Interview answer:** A race condition is a bug where the program's output depends on the non-deterministic interleaving of concurrent operations on shared data. It occurs when at least two threads access the same memory location simultaneously and at least one access is a write, with no synchronization between them.
