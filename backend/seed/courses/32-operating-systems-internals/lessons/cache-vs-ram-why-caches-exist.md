# Cache vs RAM: Why Caches Exist and How They Differ

RAM is millions of times larger than a CPU's registers, but also roughly 100–200x slower. If the CPU had to go to RAM for every instruction and every data read, a 3 GHz processor would effectively run at the speed of memory — around 15–30 MHz. Caches bridge that gap.

## SRAM vs DRAM: The Physics

| Property | SRAM (cache) | DRAM (RAM) |
|---|---|---|
| Storage cell | 6 transistors (flip-flop) | 1 transistor + 1 capacitor |
| Speed | ~1–4 ns | ~60–100 ns |
| Density | Low (large cell) | High (tiny cell) |
| Cost | Expensive | Cheap |
| Refresh needed | No | Yes (capacitor leaks) |
| Location | Inside or very close to CPU die | Off-chip DIMMs |

DRAM stores a bit as a charge on a capacitor. Because capacitors leak, DRAM must be **refreshed** every ~64 ms — during refresh rows are temporarily unavailable, adding latency jitter. SRAM holds state as long as power is on, no refresh needed.

## How a Cache Works

A cache is a hardware-managed associative lookup table. When the CPU requests address `A`:

1. **Cache hit** — the cache contains a valid copy of `A`'s cache line → data returned in ~1–4 ns.
2. **Cache miss** — the cache does not contain `A` → the cache controller fetches the whole **cache line** (typically 64 bytes) from the next level (L2, L3, or RAM), stores it in the cache, and returns the requested bytes.

```
CPU requests byte at address 0x1234
│
├─ L1 hit? ──Yes──► return in ~1 ns
│     No
├─ L2 hit? ──Yes──► return in ~4 ns, fill L1
│     No
├─ L3 hit? ──Yes──► return in ~12 ns, fill L2 + L1
│     No
└─ Go to RAM ──────► return in ~80 ns, fill L3 + L2 + L1
```

## Cache Lines

The unit of transfer between levels is a **cache line**, not a single byte. On x86 this is 64 bytes. This is why spatial locality matters — if you access `arr[0]`, the cache pulls in `arr[0]` through `arr[7]` (for 8-byte doubles) in one shot, so subsequent accesses are free.

```c
// Demonstrates cache line effect
#include <time.h>
#define N 1024*1024

int arr[N];

// Sequential: every element in same or adjacent cache lines
for (int i = 0; i < N; i++) arr[i]++;   // fast

// Strided by 16: every access is a new cache line
for (int i = 0; i < N; i += 16) arr[i]++; // ~16x fewer cache misses, still fast

// Random: cache miss on nearly every access
for (int i = 0; i < N; i++) arr[rand()%N]++; // very slow
```

## Cache Replacement Policies

When a cache is full and a new line must be loaded, the hardware evicts an existing line. Common policies:

- **LRU (Least Recently Used)** — evict the line not accessed for the longest time. Approximated in hardware.
- **Pseudo-LRU** — a simpler tree-based approximation used in most real L1/L2 caches.
- **Random** — surprisingly competitive for large L3 caches; no LRU tracking overhead.

## Write Policies

| Policy | Behavior | Coherence complexity |
|---|---|---|
| **Write-through** | Write updates cache and RAM immediately | Simple; RAM always consistent |
| **Write-back** | Write updates cache only; RAM updated on eviction | Higher throughput; needs dirty-bit tracking |

Most modern CPUs use **write-back** with a **dirty bit** per cache line. The OS must be aware of this when doing DMA or communicating with hardware that bypasses the cache.

## OS Implications

- **Context switches** are expensive partly because they flush or pollute the L1/L2 cache — the next process's data is cold.
- **Cache coloring** — some OS kernels (BSD, older Linux) assign physical pages so that processes competing for the same L2 cache sets are separated.
- **False sharing** — two threads on different cores modify different variables that happen to share a cache line. Each write-back invalidates the other core's copy, causing silent performance collapse.

```c
// False sharing example
struct { int a; int b; } shared;  // a and b are in the same 64-byte line
// Thread 1 writes shared.a, Thread 2 writes shared.b
// → cache line ping-pongs between cores even though they touch different fields
```

> **Interview answer:** Caches exist because DRAM is ~100x slower than the CPU. SRAM cache cells are faster but larger and costlier, so caches are small but positioned on the CPU die. On a cache hit the CPU gets data in nanoseconds; on a miss it waits for the full memory latency. The OS is affected by caches during context switches (cold cache) and must be aware of write-back policies when coordinating with DMA hardware.
