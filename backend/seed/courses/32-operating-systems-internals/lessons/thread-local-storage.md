# Thread-Local Storage and Per-Thread State

Thread-Local Storage (TLS) gives each thread its own private copy of a variable. The variable name and type are shared across the program, but the value is siloed per thread — no synchronization needed.

## The Problem TLS Solves

Global and static variables are shared across threads. That forces you to either:
1. Use a mutex every time you access them, or
2. Find a different design.

TLS is option 3: make the variable global in name but private in storage.

```c
// Without TLS — shared, needs a lock
static int request_count = 0;           // race condition
pthread_mutex_lock(&mu);
request_count++;
pthread_mutex_unlock(&mu);

// With TLS — no lock needed
static __thread int request_count = 0;  // each thread has its own copy
request_count++;                        // safe
```

## Declaring TLS Variables

```c
// C11 and GCC/Clang extension
__thread int my_var = 0;          // GCC/Clang
_Thread_local int my_var = 0;    // C11 standard keyword

// C++ (C++11)
thread_local int my_var = 0;

// Python — use threading.local()
import threading
_local = threading.local()
_local.counter = 0    # per-thread attribute
```

## How TLS Is Implemented

The compiler transforms `thread_local int x` into an access through a segment register (on x86-64: `fs` or `gs`) that points to each thread's TLS block.

```
Thread 1 memory layout:
  fs: ──→ [ TLS block for Thread 1 ]
             offset +0: errno copy
             offset +8: x (= 42)
             offset +16: ...

Thread 2 memory layout:
  fs: ──→ [ TLS block for Thread 2 ]
             offset +0: errno copy
             offset +8: x (= 99)    ← different value, same variable name
```

Access to `x` compiles to something like:

```asm
mov rax, QWORD PTR fs:0x10    ; read x from this thread's TLS at offset 0x10
```

The `fs` base register is set by the kernel for each thread at creation time (via `arch_prctl(ARCH_SET_FS, tls_addr)` on Linux x86-64).

## Common TLS Use Cases

| Use case | Example |
|---|---|
| Error codes | `errno` in glibc |
| Per-thread allocator state | tcmalloc, jemalloc thread caches |
| Profiling / tracing | Per-thread event buffer |
| Connection context | Database connection handle per worker thread |
| Random state | Per-thread PRNG seed |

## Worked Example: Per-Thread Random State

```c
#include <stdlib.h>
#include <stdint.h>

static __thread uint64_t rng_state = 0;  // per-thread seed

void thread_seed(uint64_t s) { rng_state = s; }

uint64_t thread_rand(void) {
    // xorshift64 — no locks, no sharing
    rng_state ^= rng_state << 13;
    rng_state ^= rng_state >> 7;
    rng_state ^= rng_state << 17;
    return rng_state;
}
```

Every thread gets its own `rng_state`. Two threads calling `thread_rand()` concurrently produce independent sequences. No mutex. No atomic.

## Python thread_local Example

```python
import threading

_local = threading.local()

def worker(name):
    _local.name = name          # each thread sets its own value
    print(f"{threading.current_thread().name}: {_local.name}")

t1 = threading.Thread(target=worker, args=("Alice",), name="T1")
t2 = threading.Thread(target=worker, args=("Bob",),   name="T2")
t1.start(); t2.start()
t1.join();  t2.join()
# T1: Alice
# T2: Bob   ← no conflict
```

## Pitfalls

- **TLS is not free.** First access to a TLS variable may require a slow path (dynamic TLS in shared libraries). Prefer `__thread` in the main executable for hot paths.
- **Inheritance.** TLS is initialized per thread — a child thread does not inherit the parent thread's TLS values (they get the initializer value or zero).
- **Thread pool reuse.** If thread pool workers reuse threads, TLS state from a previous task may leak into the next one. Always reset TLS at the start of a task.

> **Interview answer:** Thread-Local Storage provides each thread with its own private instance of a variable. It is implemented using a per-thread TLS block pointed to by a segment register (`fs` on x86-64). The compiler generates accesses through that register, so reads and writes are fast and require no synchronization. Canonical examples include `errno`, per-thread allocator caches, and per-thread PRNG state.
