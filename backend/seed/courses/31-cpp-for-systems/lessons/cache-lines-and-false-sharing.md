# Cache Lines, Padding, and False Sharing

Even when every struct member is correctly aligned, poor data layout relative to CPU cache lines can obliterate multithreaded performance. Understanding cache-line granularity turns a theoretical alignment discussion into a concrete performance engineering skill.

## What Is a Cache Line?

The CPU does not transfer individual bytes or words between RAM and the cache. It transfers fixed-size **cache lines** — almost universally **64 bytes** on modern x86, x64, and ARM64 processors. When any byte in a cache line is read or written, the entire 64-byte block is loaded into the cache.

```
Physical memory:
Address:  0    8    16   24   32   40   48   56   64   72 ...
          [-------- cache line 0 (64 bytes) ----------][--- cache line 1 ---]
```

## False Sharing — The Invisible Bottleneck

**False sharing** occurs when two threads write to different variables that happen to reside in the **same cache line**. From the program's point of view the variables are independent; from the cache's point of view every write by one thread invalidates the line in every other core's cache.

```
Thread 0  writes counter_a  →  invalidates cache line on Core 1
Thread 1  writes counter_b  →  invalidates cache line on Core 0
  (both variables are in the same 64-byte block)
Result: cores constantly bounce the line → serial throughput, not parallel
```

### Minimal Reproducer

```cpp
#include <atomic>
#include <thread>

struct Counters {
    std::atomic<long> a;   // likely offset 0
    std::atomic<long> b;   // likely offset 8 — same cache line as a!
};

Counters g;

void inc_a() { for (int i = 0; i < 1'000'000; ++i) g.a.fetch_add(1, std::memory_order_relaxed); }
void inc_b() { for (int i = 0; i < 1'000'000; ++i) g.b.fetch_add(1, std::memory_order_relaxed); }

// Two threads running inc_a and inc_b are NOT truly independent —
// they fight over the same cache line.
```

On a modern server this can be **5–10× slower** than a correctly padded version.

## The Fix: Cache-Line Padding

Pad each hot field to a full 64-byte cache line so no two independently-written values share a line.

```cpp
struct alignas(64) PaddedCounter {
    std::atomic<long> value;
    // 56 bytes of implicit tail padding to reach 64 bytes total
};

struct Counters {
    PaddedCounter a;   // occupies cache line 0
    PaddedCounter b;   // occupies cache line 1
};
```

Or use a padding member explicitly for clarity:

```cpp
static constexpr std::size_t CACHE_LINE = 64;

struct Counters {
    alignas(CACHE_LINE) std::atomic<long> a;
    char _pad0[CACHE_LINE - sizeof(std::atomic<long>)];

    alignas(CACHE_LINE) std::atomic<long> b;
    char _pad1[CACHE_LINE - sizeof(std::atomic<long>)];
};
```

C++17 provides a standard constant:

```cpp
#include <new>
// std::hardware_destructive_interference_size — the minimum stride
// between two objects to avoid false sharing (typically 64)
alignas(std::hardware_destructive_interference_size) std::atomic<long> a;
```

## Constructive Interference — The Other Side

**Constructive interference** (true sharing) is when data that is always read together is placed on the **same** cache line. This minimises cache misses for read-heavy structures.

```cpp
#include <new>
// std::hardware_constructive_interference_size — max offset such that
// two objects are guaranteed on the same cache line (typically 64 too)
struct ReadHot {
    // Pack frequently co-read fields tightly
    int   key;
    int   value;
    // These 8 bytes are very likely on one cache line together
};
```

## Identifying False Sharing

```bash
# Linux perf — look for cache-line bouncing (LLC misses, HITM events)
perf c2c record ./my_app
perf c2c report

# Intel VTune: "Memory Access" analysis → "True/False Sharing" view
```

## Rules of Thumb

- **Hot per-thread data**: one cache line per thread — use thread-local storage or per-thread arrays.
- **Read-mostly shared data**: pack tightly for spatial locality.
- **Write-heavy shared counters**: one cache line per counter, pad aggressively.
- **Lock/mutex objects**: place locks and the data they protect on the **same** cache line to avoid a second cache miss when acquiring.

> **Interview answer:** False sharing occurs when two threads independently write to variables that share a 64-byte cache line, causing the CPU cache coherence protocol to bounce that line between cores on every write. The fix is to pad each independently-written hot variable to fill a full cache line, using `alignas(64)` or `std::hardware_destructive_interference_size`.
