# Threads vs. Processes

A **thread** is the smallest schedulable unit of CPU execution. Every process starts with one thread — the "main thread." Additional threads can be created within the same process, sharing its address space and resources while each maintaining an independent execution path, stack, and register set.

## What Threads Share and What They Don't

| Resource | Shared Among Threads? | Notes |
|----------|-----------------------|-------|
| Virtual address space (code, heap) | Yes | All threads see the same memory |
| Global and static variables | Yes | Source of race conditions |
| Open file descriptors | Yes | All threads can read/write the same files |
| Signal handlers | Yes | Handler code is shared |
| Working directory | Yes |  |
| Memory-mapped regions | Yes | `mmap()` results visible to all |
| Thread ID (TID) | **No** | Each thread has a unique TID |
| Stack | **No** | Each thread has its own private stack (default 8 MB on Linux) |
| CPU registers (including `rip`, `rsp`) | **No** | The whole point of threading |
| Errno (thread-local storage) | **No** | TLS makes `errno` per-thread |
| Signal mask | **No** | Each thread can block/unblock signals independently |

Because threads share memory, communication between threads is as fast as a load/store instruction — orders of magnitude faster than inter-process communication (IPC) via pipes, sockets, or shared memory segments.

## Creating Threads: Python and C

```python
import threading

counter = 0
lock = threading.Lock()

def increment(n):
    global counter
    for _ in range(n):
        with lock:
            counter += 1   # Protected by mutex

t1 = threading.Thread(target=increment, args=(100_000,))
t2 = threading.Thread(target=increment, args=(100_000,))
t1.start(); t2.start()
t1.join();  t2.join()
print(counter)   # Always 200000 — protected by lock
```

In C (POSIX threads):

```c
#include <pthread.h>
pthread_t t1, t2;

pthread_create(&t1, NULL, increment_fn, (void*)100000);
pthread_create(&t2, NULL, increment_fn, (void*)100000);
pthread_join(t1, NULL);
pthread_join(t2, NULL);
```

On Linux, `pthread_create` calls `clone(CLONE_VM | CLONE_FS | CLONE_FILES | ...)` — a more general version of `fork()` that shares specific resources with the parent instead of copying them.

## Thread Stacks and Stack Overflow

Each thread gets its own stack (8 MB by default on Linux). The OS places a **guard page** (a non-mapped page) just below the stack bottom. If a thread overflows its stack (e.g., infinite recursion), it accesses the guard page and receives a SIGSEGV — a "stack overflow" crash.

```
Thread 1's virtual address range:
  [stack bottom guard page]
  [8 MB stack]              ← rsp starts here
Thread 2's virtual address range:
  [stack bottom guard page]
  [8 MB stack]
```

Large stack frames (e.g., a C function allocating 1 MB of local arrays) can silently eat through the stack guard. `ulimit -s unlimited` removes the stack size limit (dangerous on memory-constrained systems).

## Kernel Threads vs. User Threads

| | Kernel Threads | User-Space Threads (Green Threads) |
|-|----------------|------------------------------------|
| Managed by | OS scheduler | User-space library or runtime |
| Context switch cost | ~1–10 µs (kernel involved) | ~100–1000 ns (no syscall) |
| True parallelism | Yes — each on a separate core | No — unless 1:1 with kernel threads |
| Blocking syscall | Only blocks that one thread | Can block all threads on the same kernel thread |
| Examples | Linux `pthread`, Windows `CreateThread` | Python `asyncio` coroutines, Ruby fibers, Lua coroutines |

## The 1:1, N:1, and N:M Threading Models

```
1:1 model (Linux, Windows, macOS):
  User thread ────────► Kernel thread
  User thread ────────► Kernel thread
  User thread ────────► Kernel thread
  (each user thread is a kernel-scheduled task)
  Pros: true parallelism, simple model
  Cons: expensive to create (syscall), OS limits thread count

N:1 model (old Java green threads):
  User thread ─┐
  User thread ─┼──► Single kernel thread
  User thread ─┘
  Pros: cheap creation, no syscall per thread
  Cons: no parallelism; one blocking syscall blocks all

N:M model (Go goroutines, Java Virtual Threads, Erlang):
  Goroutine G1 ─┐                ┌── Kernel thread KT1
  Goroutine G2 ─┤  Go runtime   ├── Kernel thread KT2
  Goroutine G3 ─┤  scheduler    ├── Kernel thread KT3
  Goroutine G4 ─┘                └── Kernel thread KT4
  (N goroutines multiplexed onto M kernel threads, N >> M)
  Pros: lightweight creation (2KB stack vs 8MB), low overhead
  Cons: runtime scheduler complexity; blocking syscalls need wrapping
```

Linux uses the **1:1 model** exclusively. Every `pthread_create` creates a new kernel task via `clone()`, visible in `ps` and `top`. Go runtime uses N:M — you can create 1 million goroutines with modest memory overhead because each starts with a 2KB growable stack.

## Thread Pool Pattern

Creating and destroying threads for every short task is expensive (~10 µs each). Production systems use **thread pools**:

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=8) as pool:
    futures = [pool.submit(process_request, req) for req in requests]
    results = [f.result() for f in futures]
```

The pool creates 8 threads at startup and reuses them for all tasks. No thread creation overhead per task; bounded resource usage; no unbounded thread explosion.

## When to Use Threads vs. Processes

| Criterion | Threads | Processes |
|-----------|---------|-----------|
| Memory overhead | Low — share address space | High — separate address space + page tables |
| Communication speed | Fast — shared memory | Slow — IPC: pipes (~1 µs), sockets (~5–50 µs) |
| Fault isolation | Poor — one thread crash (SIGSEGV) kills all | Strong — one process crash does not affect others |
| Security isolation | Weak — all threads see all memory | Strong — separate address spaces |
| Creation time | Fast (~10 µs for a thread) | Slower (~1–5 ms for fork+exec) |
| Best use case | Parallel computation, I/O concurrency within one program | Browser sandboxing, multi-tenant servers, worker isolation |

**Rule of thumb:**
- Use **threads** for parallelism within a single coherent task (web server request handling, image processing pipeline).
- Use **processes** for strong isolation (browser tabs, database worker processes, microservices).

## Python's GIL and Its Implications

The **CPython Global Interpreter Lock (GIL)** is a mutex in the CPython interpreter that prevents multiple Python threads from executing Python bytecode simultaneously:

```
Timeline on 4-core machine with 4 Python threads:
  Core 0: [Python thread 1 runs] [Thread 2 runs] [Thread 1 runs] ...
  Core 1: idle
  Core 2: idle
  Core 3: idle
  ← Only one thread runs Python bytecode at a time!
```

**Why the GIL exists:** CPython's reference counting is not thread-safe without a global lock. Removing the GIL requires making every object's reference count atomic, which has broad performance implications.

**Implications:**
- **I/O-bound threads** still benefit — the GIL is released during I/O syscalls (`socket.recv`, `time.sleep`, file `read()`).
- **CPU-bound threads** do NOT get true parallelism — use `multiprocessing.Pool` or native extensions (`numpy`, `torch`) that release the GIL.
- **Python 3.13** introduces an "experimental no-GIL" build (PEP 703) — the GIL is becoming optional.

## Asynchronous Programming vs. Threads

Modern Python uses `asyncio` as an alternative to threads for I/O concurrency:

```python
import asyncio

async def fetch(url):
    async with aiohttp.ClientSession() as s:
        async with s.get(url) as r:
            return await r.text()

# 1000 concurrent HTTP requests with a SINGLE thread
async def main():
    urls = [f"https://example.com/{i}" for i in range(1000)]
    results = await asyncio.gather(*[fetch(u) for u in urls])
```

`asyncio` is single-threaded but interleaves coroutines cooperatively at `await` points. No GIL concerns, no lock overhead, very low memory (coroutines are much smaller than threads). The drawback: blocking code (CPU work, non-async libraries) blocks the entire event loop.

## Key Takeaways

- A thread is a unit of execution within a process; threads share the process's address space, files, and globals.
- Each thread has its own **stack** and **register set** — these are never shared.
- Linux uses the **1:1 model** (each pthread is a kernel task via `clone()`).
- Go and Java Virtual Threads use **N:M** (many lightweight threads multiplexed on fewer kernel threads).
- Threads are faster to create and communicate, but offer less fault and security isolation than processes.
- Python's **GIL** limits CPU-bound thread parallelism in CPython; use `multiprocessing` or async for parallelism.
- **Thread pools** amortize thread creation overhead and bound resource consumption.
