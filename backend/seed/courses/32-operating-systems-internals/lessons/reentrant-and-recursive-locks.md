# Reentrant and Recursive Locks

A standard (non-recursive) mutex will **deadlock** if the owning thread tries to lock it a second time. Recursive and reentrant locks solve this — but introduce their own subtleties.

## The Problem: Self-Deadlock

```cpp
std::mutex mtx;

void helper() {
    std::lock_guard<std::mutex> lk(mtx);  // tries to lock mtx
    // do work...
}

void outer() {
    std::lock_guard<std::mutex> lk(mtx);  // locks mtx
    helper();                              // DEADLOCK: tries to lock already-owned mtx
}
```

On most systems, `pthread_mutex_lock` on an already-owned non-recursive mutex results in **undefined behavior** or an immediate deadlock, depending on the mutex type.

## Recursive Mutex

A recursive mutex (also called a reentrant mutex) tracks both:
- Which thread owns it.
- How many times that thread has locked it (the **recursion depth**).

```cpp
#include <mutex>

std::recursive_mutex rmtx;

void helper() {
    std::lock_guard<std::recursive_mutex> lk(rmtx);  // safe: same thread
    // do work
}

void outer() {
    std::lock_guard<std::recursive_mutex> lk(rmtx);  // depth = 1
    helper();                                          // depth = 2; no deadlock
}                                                      // depth back to 0; lock released
```

The lock is only truly released when the recursion depth returns to zero.

## POSIX API

```c
pthread_mutex_t rmtx;
pthread_mutexattr_t attr;

pthread_mutexattr_init(&attr);
pthread_mutexattr_settype(&attr, PTHREAD_MUTEX_RECURSIVE);
pthread_mutex_init(&rmtx, &attr);
pthread_mutexattr_destroy(&attr);
```

## Reentrant vs Recursive — the Distinction

These terms are often used interchangeably, but they have different origins:

| Term | Context | Meaning |
|---|---|---|
| **Reentrant** (function) | Single-threaded | A function is reentrant if it can be interrupted mid-execution and safely called again (no global state, no static locals) |
| **Reentrant** (lock) | Multi-threaded | Often synonymous with recursive — a lock the owner can re-acquire |
| **Recursive mutex** | Multi-threaded | Explicit OS/library construct with depth tracking |

A reentrant function uses only stack variables and is safe to call from signal handlers or nested contexts. A recursive mutex solves the nested-lock deadlock for multi-threaded code.

## When to Use a Recursive Mutex

- **Legacy code refactoring**: Large codebases where call chains are hard to untangle.
- **Recursive algorithms operating on shared data**: e.g., a recursive tree traversal that modifies a shared tree.
- **Library code that calls callbacks**: The callback may call back into the library.

```cpp
// Recursive traversal of a locked tree
void process_node(Node *n) {
    std::lock_guard<std::recursive_mutex> lk(tree_mtx);
    if (!n) return;
    // modify n
    process_node(n->left);   // re-enters the lock
    process_node(n->right);
}
```

## Pitfalls and Why to Avoid Them When Possible

- **Performance**: A recursive mutex must atomically read, compare, and write both the owner ID and the depth on every lock/unlock — more expensive than a plain mutex.
- **Mask design flaws**: If you find yourself reaching for a recursive mutex, it often signals that your locking strategy is not clearly layered. Refactoring to avoid re-entrant locking is usually the cleaner solution.
- **Correctness illusion**: A recursive mutex can let an invariant-violating state be observed by a re-entrant call. The inner call acquires the lock but the outer call may have partially updated shared data.

```cpp
// Bug: outer has partially updated data; inner call sees inconsistent state
void bad_update() {
    std::lock_guard<std::recursive_mutex> lk(rmtx);
    data.field1 = new_val;           // partial update
    helper_that_reads_data();        // reads inconsistent data — lock allows it!
    data.field2 = related_new_val;   // rest of update
}
```

## Quick Rules

- Default to a **plain mutex** and restructure code to avoid recursive locking.
- Use a **recursive mutex** as a pragmatic bridge when restructuring is not feasible.
- Never use a recursive mutex as an excuse to skip reasoning about your locking structure.

> **Interview answer:** A recursive mutex tracks the owning thread and a lock-depth counter, allowing the same thread to re-acquire it without deadlocking. The lock is released only when the depth returns to zero. It comes at a performance cost and can mask design flaws — prefer plain mutexes and layered locking when possible.
