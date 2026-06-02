# The Memory Hierarchy: Registers to Disk

No single memory technology is simultaneously fast, large, and cheap. The memory hierarchy solves this tension by layering storage types, keeping frequently used data in fast (expensive) layers and infrequently used data in slow (cheap) layers. The OS is the primary manager of the lower layers.

## The Layers at a Glance

| Level | Technology | Typical Size | Typical Latency | Managed by |
|---|---|---|---|---|
| Registers | Flip-flops in the CPU | 16–32 × 64-bit | ~0.3 ns (1 cycle) | Compiler / hardware |
| L1 Cache | SRAM, on-die | 32–64 KB | ~1 ns (4 cycles) | CPU hardware |
| L2 Cache | SRAM, on-die | 256 KB – 1 MB | ~4 ns (12 cycles) | CPU hardware |
| L3 Cache | SRAM, shared on-die | 4 – 64 MB | ~10–30 ns | CPU hardware |
| Main Memory (RAM) | DRAM DIMMs | 4 – 512 GB | ~60–100 ns | OS (virtual memory) |
| NVMe SSD | Flash, PCIe | 512 GB – 8 TB | ~100 µs | OS (file system / block I/O) |
| HDD / Network | Magnetic or remote | TB – PB | ~5–10 ms | OS / distributed layer |

Latency increases roughly **10x per level**. That gap is why caches matter so much.

## Why the OS Cares

The OS directly manages two layers:

**Main memory (RAM)** — The OS decides which process gets which physical RAM pages, implements virtual memory so each process has its own address space, and swaps pages to disk when RAM is full (paging/swapping).

**Secondary storage** — The OS file system controls how data is organized and cached in disk buffers. The **page cache** (also called buffer cache) keeps recently read disk blocks in RAM so repeated reads are fast.

## Temporal and Spatial Locality

Hardware caches exploit two properties that most programs exhibit:

- **Temporal locality** — if a location was accessed recently, it will likely be accessed again soon (loops, counters).
- **Spatial locality** — if a location was accessed, nearby locations will likely be accessed soon (arrays, sequential code).

```c
// Good spatial locality — accesses array sequentially
for (int i = 0; i < N; i++)
    sum += arr[i];          // cache line loaded once, reused for ~8–16 elements

// Poor spatial locality — column-major access on a row-major array
for (int j = 0; j < N; j++)
    sum += matrix[0][j];    // every access strides past the next cache line
```

## The Working Set

A process's **working set** is the set of pages it actively uses during a time window. If the working set fits in RAM, the process runs quickly. If it does not, the OS must page data in and out of disk — causing **thrashing**, where the system spends more time swapping than executing.

OS schedulers use working-set information to decide when to suspend a process: keeping a process whose working set fits cleanly in cache is more efficient than constantly evicting other processes' pages.

## Capacity vs Speed Trade-off

```
  Speed  ▲  Registers
         │  L1 Cache
         │  L2 Cache
         │  L3 Cache
         │  RAM
         │  SSD
  Slow  ▼  HDD
         └───────────────► Size / Cost per bit
                            (small/expensive → large/cheap)
```

Registers: ~$0 per bit of useful compute time. RAM: ~$0.000000003 per bit. HDD: ~$0.0000000001 per bit. The pyramid shape captures both the size progression and the cost inversion.

## Common Pitfalls

- Treating RAM as "fast" — compared to disk it is, but compared to L1 cache it is ~100x slower. Cache misses are a primary source of real-world performance loss.
- Ignoring NUMA (Non-Uniform Memory Access) — on multi-socket servers, RAM attached to socket 0 is slower for a core on socket 1. The OS scheduler tries to keep threads on the same NUMA node as their memory.
- Forgetting that the page cache is RAM — `free -h` on Linux shows "available" memory, not just truly "free" memory, because the OS can reclaim cache pages on demand.

> **Interview answer:** The memory hierarchy arranges storage in layers from registers (fastest, smallest) down to disk (slowest, largest). Each layer is ~10x slower but ~1000x larger than the layer above. The OS manages RAM via virtual memory and paging, and manages disk access via the file system and page cache, exploiting temporal and spatial locality to keep hot data in fast layers.
