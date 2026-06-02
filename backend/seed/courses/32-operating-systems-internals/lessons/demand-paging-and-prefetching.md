# Demand Paging and Prefetching

Demand paging is the OS strategy of deferring physical memory allocation until the very moment a page is first accessed. Combined with prefetching — the proactive loading of pages before they are needed — it forms the backbone of modern virtual memory performance.

## The core idea of demand paging

When a process is loaded, the OS does *not* copy the entire program image into RAM. Instead it:

1. Creates a virtual address space and populates the page table with mappings pointing to the executable file on disk.
2. Sets the *present bit* to 0 for every page.
3. Allows the CPU to start executing from the entry point.

The first instruction access triggers a page fault. The kernel reads only *that* page from disk, maps it, and the process continues. Every other code and data page is loaded on demand — only when first touched.

```
Process starts   → 0 pages in RAM
First instruction → 1 page fault → load code page 0
First data write  → 1 page fault → zero-fill anonymous heap page
Global array init → 1 page fault → load data segment page
...
After 60 seconds  → only ~40 of 200 code pages ever touched
```

## Benefits of demand paging

- **Faster startup** — a program that needs 50 MB of code can start running after loading just the first 4 KB page.
- **Lower memory footprint** — pages never touched (dead code paths, error handlers) consume no physical RAM.
- **Efficient `fork()`** — child processes share all parent pages via Copy-on-Write; no copying happens at all until a write occurs.
- **Overcommit support** — the OS can promise more virtual memory than physical RAM exists, betting that not all of it will be touched simultaneously.

## The cost of pure demand paging

Every cold start triggers a burst of major page faults. Each fault blocks the thread briefly. A program with 200 pages that needs 180 of them before it can respond will suffer 180 major faults — potentially hundreds of milliseconds of startup latency even on SSD.

## Prefetching (read-ahead)

Prefetching proactively loads pages the OS predicts will be needed soon, before the fault actually occurs.

### Spatial prefetching (read-ahead)

When a page fault occurs on page N, the kernel speculatively reads pages N+1 through N+k into the page cache at the same time. This amortizes disk seeks and greatly reduces the number of actual fault events for sequential access patterns.

```
Fault on page 5 →  kernel issues I/O for pages 5–12
Process accesses 6 → already in cache (minor fault, ~2 µs)
Process accesses 7 → already in cache (minor fault, ~2 µs)
```

Linux controls this via `/proc/sys/vm/page-cluster` and the `madvise` syscall.

### `madvise` — application-guided prefetching

```c
#include <sys/mman.h>

// Tell the kernel: "I'll access this range sequentially — prefetch it"
madvise(ptr, length, MADV_SEQUENTIAL);

// "I'll need this region soon — prefetch it now"
madvise(ptr, length, MADV_WILLNEED);

// "I'm done with this region — you may evict it"
madvise(ptr, length, MADV_DONTNEED);
```

`MADV_WILLNEED` is commonly used by databases and JVMs to warm up memory regions before a query or GC cycle.

### `mlock` — pin pages in RAM

For latency-critical code (real-time audio, HFT), you can lock pages so they are never swapped and require no faults:

```c
mlock(ptr, length);   // pin; subsequent accesses have zero fault overhead
```

## Demand paging vs eager loading comparison

| Strategy | Startup time | Memory usage | Best for |
|---|---|---|---|
| Demand paging | Fast | Low | General-purpose apps |
| Eager loading | Slow | High | Real-time / predictable latency |
| Prefetch + demand | Balanced | Moderate | Sequential data workloads |

## Worked example: Python script startup

```bash
strace -e trace=mmap,read python3 hello.py 2>&1 | head -30
# You'll see dozens of mmap() calls setting up pages with PROT_READ,
# then page faults bring in only the code paths actually executed.
```

A Python 3 process maps ~15 MB of shared libraries but typically faults in only 3–5 MB on a simple script.

**Interview answer:** Demand paging loads pages from disk only on first access, reducing startup time and memory usage; prefetching proactively loads predicted pages (via sequential read-ahead or `madvise`) to reduce the burst of faults during access.
