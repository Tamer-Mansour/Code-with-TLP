# False Sharing and Its Performance Impact

Cache coherence operates at the granularity of **cache lines** (typically 64 bytes), not individual variables. This creates a subtle performance hazard: two threads writing to entirely different variables can still cause coherence traffic if those variables happen to reside in the same cache line. This phenomenon is called **false sharing**.

## What False Sharing Looks Like

Suppose two threads each maintain their own counter:

```c
// Naive layout — two counters in the same cache line
struct {
    long counter_a;  // offset 0  (bytes 0–7)
    long counter_b;  // offset 8  (bytes 8–15)
} counters;

// Thread 0 (Core 0)
void thread0() {
    for (int i = 0; i < 100000000; i++)
        counters.counter_a++;
}

// Thread 1 (Core 1)
void thread1() {
    for (int i = 0; i < 100000000; i++)
        counters.counter_b++;
}
```

`counter_a` and `counter_b` share a single 64-byte cache line. Every increment by Core 0 invalidates Core 1's copy and vice versa. The line bounces between caches in **Modified** state continuously — hundreds of millions of times.

### Measured Impact

On a modern x86 processor:

| Scenario | Time (approx) |
|---|---|
| Two threads, false sharing | ~2000 ms |
| Two threads, padded (no false sharing) | ~200 ms |
| One thread doing both counters | ~180 ms |

The false-sharing case is nearly **10x slower** than the single-threaded version, and even slower than single-threaded! Parallelism made performance *worse*.

## Diagnosing False Sharing

The cache-line bounce appears in performance counters as high `LLC_MISS` or `HITM` (hit-in-modified-state) rates:

```bash
# Linux perf — look for high HITM ratio
perf c2c record -- ./my_program
perf c2c report

# Output shows hot cache lines with high remote hitm count:
# Shared Data Cache Line Table
#     Total   Rmt  Rmt HITM  ...  Symbol
#    1000000  999980     ...  counters.counter_a/counter_b
```

Intel's VTune and AMD's uProf show similar heat maps.

## Fix 1: Padding to Cache Line Boundaries

Ensure each hot variable occupies its own cache line:

```c
// Padded to 64 bytes each
struct {
    long counter_a;
    char pad_a[64 - sizeof(long)];  // 56 bytes of padding
    long counter_b;
    char pad_b[64 - sizeof(long)];
} counters;
```

In C11/C++11, use `alignas`:

```c
#include <stdalign.h>

struct {
    alignas(64) long counter_a;
    alignas(64) long counter_b;
} counters;
```

In Java, the `@Contended` annotation (JDK 8+) does this automatically.

## Fix 2: Thread-Local Storage

If threads can accumulate results locally and merge at the end, eliminate sharing entirely:

```c
// Thread-local accumulator — no sharing during computation
_Thread_local long local_count = 0;

void worker() {
    for (int i = 0; i < 100000000; i++)
        local_count++;  // Stays in this core's L1 cache
}

// Merge phase (done once, synchronized)
void merge() {
    // Collect local_count from each thread
}
```

This pattern is used in high-performance counters, histograms, and accumulators.

## Fix 3: Per-Core Data Structures

Operating system kernels use **per-CPU variables** extensively:

```c
// Linux kernel per-CPU counter
DEFINE_PER_CPU(long, my_counter);

// Increment on current CPU — no coherence traffic
this_cpu_inc(my_counter);

// Read global total
long total = 0;
for_each_possible_cpu(cpu)
    total += per_cpu(my_counter, cpu);
```

Each CPU has its own counter instance in its own cache line. The cross-CPU read (sum) happens infrequently.

## True Sharing vs False Sharing

| Type | Variables involved | Cache line involved | Solution |
|---|---|---|---|
| **True sharing** | Same variable | Same line | Synchronization (locks, atomics) |
| **False sharing** | Different variables | Same line | Padding, thread-local data, reorganize layout |

True sharing requires actual synchronization. False sharing requires only data layout changes — no algorithm change is needed.

## Producer-Consumer Queue Example

Ring buffer falsely shared between producer and consumer:

```c
// BAD: head and tail in same cache line
struct ring_buffer {
    int head;   // Written by consumer, read by producer
    int tail;   // Written by producer, read by consumer
    int data[1024];
};

// GOOD: separate cache lines
struct ring_buffer {
    alignas(64) int head;   // Consumer's cache line
    alignas(64) int tail;   // Producer's cache line
    int data[1024];
};
```

Separating `head` and `tail` onto different cache lines eliminates the ping-pong between producer and consumer cores.

## Key Numbers to Remember

- Typical cache line size: **64 bytes** (x86, ARM, RISC-V reference designs)
- L1 cache hit: ~4 cycles
- Remote L3 / cross-socket: ~200–400 cycles
- Coherence-induced miss (HITM): can approach remote memory latency (~200 cycles) every single operation in worst case

## Interview Answer

> "False sharing occurs when two threads write to different variables that happen to occupy the same 64-byte cache line. The coherence protocol sees writes to that line from multiple cores and continuously invalidates and retransfers it — even though the threads are logically independent. The fix is to pad or align hot per-thread variables to cache-line boundaries so each thread's data sits in its own exclusive line. Tools like `perf c2c` or Intel VTune's memory access analysis identify false sharing by showing high HITM (hit-in-modified-state) rates on specific cache lines."
