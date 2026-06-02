# Thread Pools and When to Use Them

Creating a thread for every unit of work is expensive. A thread pool amortizes that cost by keeping a fixed set of threads alive and reusing them across many tasks.

## The Problem Thread Pools Solve

```
Without pool (naive):
  request arrives → pthread_create → work → pthread_join + destroy
  Each request pays: ~10 µs syscall + stack allocation + TCB setup

With pool:
  request arrives → enqueue task → idle thread wakes → work → sleep again
  Steady-state cost: ~200 ns mutex + condvar signal
```

Thread creation overhead on Linux is roughly 10–50 µs. For a server handling 100K req/s that latency alone would consume all CPU time in a naive create-per-request design.

## Thread Pool Architecture

```
         ┌─────────────────────────────┐
producer │   Task Queue (bounded)      │
threads ─→  [T1][T2][T3]...[Tn]       │
         └────────────┬────────────────┘
                      │ (mutex + condvar or lock-free queue)
         ┌────────────▼────────────────┐
         │  Worker Thread 1            │
         │  Worker Thread 2            │
         │  Worker Thread 3  ...       │
         └─────────────────────────────┘
```

Key components:

- **Task queue** — bounded or unbounded queue of work items.
- **Worker threads** — pre-created threads that sleep until work arrives.
- **Submit API** — lets producers enqueue tasks without blocking.
- **Shutdown mechanism** — signals workers to drain the queue and exit.

## Minimal Thread Pool in C (POSIX)

```c
#include <pthread.h>
#include <stdlib.h>

#define POOL_SIZE 4
#define QUEUE_CAP 256

typedef void (*task_fn)(void *);
typedef struct { task_fn fn; void *arg; } task_t;

static task_t     queue[QUEUE_CAP];
static int        head, tail, count;
static pthread_mutex_t mu  = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t  cv  = PTHREAD_COND_INITIALIZER;
static int        shutdown = 0;

static void *worker(void *_) {
    while (1) {
        pthread_mutex_lock(&mu);
        while (count == 0 && !shutdown)
            pthread_cond_wait(&cv, &mu);
        if (shutdown && count == 0) { pthread_mutex_unlock(&mu); return NULL; }
        task_t t = queue[head++ % QUEUE_CAP];
        count--;
        pthread_mutex_unlock(&mu);
        t.fn(t.arg);          // execute task outside the lock
    }
}

void pool_submit(task_fn fn, void *arg) {
    pthread_mutex_lock(&mu);
    queue[tail++ % QUEUE_CAP] = (task_t){fn, arg};
    count++;
    pthread_cond_signal(&cv);
    pthread_mutex_unlock(&mu);
}
```

## Sizing the Pool

| Workload type | Recommended pool size |
|---|---|
| CPU-bound | N = number of logical cores |
| I/O-bound (blocking) | N = 2× to 10× cores (threads spend time waiting) |
| Mixed | Profile first; start with 2× cores |

```python
import os, concurrent.futures

# CPU-bound: match core count
cpu_pool = concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count())

# I/O-bound: more threads than cores
io_pool  = concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count() * 4)
```

## When to Use a Thread Pool

**Use a thread pool when:**

- Tasks are short-lived and numerous (HTTP request handling, DB query processing).
- Task creation rate is high enough that per-task thread creation cost matters.
- You need bounded concurrency to prevent resource exhaustion.

**Do not use a thread pool when:**

- Tasks are long-running and few — just create dedicated threads.
- Tasks require different priorities or scheduling classes — a single pool cannot express this easily.
- You need task cancellation with fine-grained control — prefer an async framework.

## Thread Pool in the Wild

- **Java:** `java.util.concurrent.ThreadPoolExecutor` — the foundation of `ExecutorService`.
- **Python:** `concurrent.futures.ThreadPoolExecutor`.
- **Linux kernel:** `workqueue` subsystem — a kernel-space thread pool for deferred work.
- **Nginx:** uses a small thread pool for `aio` disk reads so the event loop is never blocked.

## Common Pitfall

A pool that is too large does not run tasks faster — it increases context switch overhead and memory usage (each thread has an 8 MB stack). A pool that is too small leaves cores idle. Profile, measure thread utilization, and resize accordingly.

> **Interview answer:** A thread pool pre-creates a fixed number of worker threads and routes incoming tasks through a shared queue. This eliminates per-task thread creation overhead, bounds resource usage, and keeps CPU utilization predictable. Pool size should match the CPU count for CPU-bound work and be larger for I/O-bound work where threads spend time waiting.
