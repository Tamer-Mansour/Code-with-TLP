# Stack Overflow and Deep Recursion

The stack is fast and automatic, but it has a hard size limit — typically 1–8 MB per thread. Exceeding that limit causes a **stack overflow**, one of the most abrupt crashes a program can suffer. Understanding why it happens and how to avoid it is both a practical skill and a common interview topic.

## What Causes a Stack Overflow

Every function call pushes a new stack frame. If frames accumulate faster than they are destroyed — most commonly through deep or infinite recursion — the stack grows until it hits the **guard page** placed by the OS just below the stack limit. Touching the guard page raises a segmentation fault (SIGSEGV on Linux, access violation on Windows), which the OS converts into a stack overflow signal.

Common causes:

- **Infinite recursion** — missing or wrong base case.
- **Deeply nested valid recursion** — e.g., traversing a 100 000-node linked list recursively.
- **Large stack-allocated buffers** — a single function with `char buf[2 * 1024 * 1024]` can overflow without recursion.
- **Thread stacks** — newly created threads often have a smaller stack than the main thread.

## The Infinite Recursion Case

```c
int factorial(int n) {
    // BUG: missing base case
    return n * factorial(n - 1);  // recurses forever
}
```

On a typical system with 8 MB of stack and ~100 bytes per frame, this crashes after roughly 80 000 calls. The OS raises SIGSEGV; the program prints something like "Segmentation fault (core dumped)".

## Correct Recursive Version

```c
int factorial(int n) {
    if (n <= 1) return 1;          // base case
    return n * factorial(n - 1);   // bounded recursion
}
```

This is safe for small `n` but will still overflow for very large inputs (n > ~10 000 on most systems) because the call depth grows linearly.

## Tail Call Optimization (TCO)

A **tail call** is a recursive call that is the very last operation in a function — no work remains after the call returns. Some compilers (GCC with `-O2`, Clang) can optimize tail calls by **reusing the current stack frame** instead of allocating a new one, reducing stack depth to O(1).

```c
// Tail-recursive version with accumulator
int factorial_tail(int n, int acc) {
    if (n <= 1) return acc;
    return factorial_tail(n - 1, n * acc);  // tail call
}
```

With TCO enabled, `factorial_tail(1000000, 1)` can complete without overflowing. Without TCO (or in languages that don't guarantee it), it will still crash.

## Converting Recursion to Iteration

The safest fix for deep recursion is converting to an explicit loop using your own stack data structure:

```c
// Iterative factorial — zero stack growth risk
long factorial_iter(int n) {
    long result = 1;
    for (int i = 2; i <= n; i++) {
        result *= i;
    }
    return result;
}
```

For tree/graph traversal, maintain an explicit stack (array or linked list) instead of relying on the call stack.

## Increasing Stack Size

As a last resort, you can increase the stack limit:

```bash
# Linux: raise stack size limit to 64 MB for the current shell session
ulimit -s 65536
```

```c
// Or per-thread via pthread attributes
pthread_attr_t attr;
pthread_attr_init(&attr);
pthread_attr_setstacksize(&attr, 64 * 1024 * 1024);  // 64 MB
pthread_create(&tid, &attr, thread_func, NULL);
```

This is a workaround, not a fix — address the algorithm's depth instead.

## Detecting Stack Depth at Runtime

```c
#include <stdio.h>
void recurse(int depth) {
    char probe;                          // take the address to measure
    printf("depth %d, approx stack addr %p\n", depth, (void*)&probe);
    recurse(depth + 1);
}
```

Watching the address decrease confirms the stack grows downward on x86.

## Interview Answer

> "Stack overflow occurs when recursive calls (or large local allocations) exhaust the per-thread stack limit — typically 1–8 MB. The OS detects the violation via a guard page and sends SIGSEGV. The fix is usually converting to iteration, adding a proper base case, or using tail-call optimization where the compiler supports it."
