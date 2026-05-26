# The Memory Hierarchy

No single memory technology simultaneously delivers high capacity, high speed, and low cost. The memory hierarchy solves this with a cascade of progressively larger and slower levels, each transparently caching the level below.

## The Levels and Their Characteristics

```
Level          Latency    Bandwidth    Capacity      Technology
-----------  ---------  ----------  -----------  ----------------
Registers      0.3 ns     > 1 TB/s   32–256 B     Flip-flops (CMOS)
L1 Cache       1–2 ns   ~1.5 TB/s   32–64 KB     SRAM (6T/bit)
L2 Cache       4–8 ns   ~500 GB/s   256 KB–1 MB  SRAM
L3 Cache      10–30 ns  ~200 GB/s   8–64 MB      SRAM (denser)
Main Memory   50–80 ns   ~50 GB/s   8–128 GB     DRAM (1T-1C/bit)
NVMe SSD     ~100 µs    ~7 GB/s    256 GB–4 TB  Flash (NAND)
HDD          ~5 ms      ~200 MB/s  1–20 TB      Magnetic spinning
```

Each level is 10–100× larger and 5–15× slower than the one above it. Despite the seemingly modest size of caches, they dramatically reduce average memory access time when programs exhibit **locality**.

## Why Hierarchies Work: Locality of Reference

### Temporal Locality

A recently accessed memory location is likely to be accessed again soon. Loops are the canonical example:

```python
total = 0
for i in range(1_000_000):
    total += data[i]   # 'total' accessed 1,000,000 times — held in register
```

The variable `total` (in a register) and the loop counter `i` are accessed on every iteration. Caching them at the highest level (register) costs zero cycles.

### Spatial Locality

If a location is accessed, nearby locations are likely to be accessed soon. Arrays and sequential code have strong spatial locality:

```c
// Iterating an int array: addresses 0x1000, 0x1004, 0x1008, 0x100C, ...
for (int i = 0; i < N; i++) sum += a[i];
```

When `a[0]` is fetched (cache miss), a 64-byte cache line containing `a[0]` through `a[15]` is loaded. The next 15 accesses are cache hits at no cost.

### The Working Set

The **working set** at time T is the set of distinct pages/cache lines accessed in the last W references. Programs with working sets that fit in cache run efficiently; programs whose working sets exceed the cache suffer high miss rates.

## Cache Lines and Block Transfer

Data moves between levels in fixed-size **cache lines** (blocks), not individual bytes:

```
Typical cache line: 64 bytes (16 four-byte integers)

Request for a[0] (address 0x1000, in an empty cache):
  Cache miss → fetch 64 bytes from next level:
  0x1000 – 0x103F (a[0] through a[15]) loaded into one cache line
  
Next access to a[1] (0x1004):
  Cache HIT — same line is still in cache
  
Next access to a[15] (0x103C):
  Cache HIT — still in same 64-byte line
```

The **cache line size** is a design tradeoff:
- Larger lines → better spatial locality exploitation, fewer tag bits needed.
- Larger lines → longer fill time on a miss, more pollution if spatial locality is poor.
- 64 bytes is the near-universal sweet spot for current general-purpose CPUs.

## Cache Hits and Misses

**Hit**: data found in the cache. Served in the cache's latency (1–30 cycles).
**Miss**: data not in cache. Must fetch from a lower level (the **miss penalty**).

### The Three Cs (Miss Classification)

1. **Compulsory miss (cold miss)**: the first access to any cache line. Unavoidable on the first reference; can be hidden by prefetching.

2. **Capacity miss**: the active working set is larger than the cache. Even a fully associative cache of the same size would miss. The only fix is a larger cache or a smaller working set.

3. **Conflict miss**: two or more addresses that the cache's indexing maps to the same set, causing **thrashing** — each evicts the other repeatedly. Specific to direct-mapped and low-associativity caches.

### Example: Conflict Miss with Direct-Mapped Cache

Cache: 4 lines of 16 bytes. An access to address X maps to set `(X / 16) mod 4`.

```
Address 0x00 → set 0
Address 0x40 → set 0  ← same set as 0x00!
Address 0x80 → set 0  ← same set!

Access sequence: 0x00, 0x40, 0x00, 0x40, ...
  Access 0x00: miss (cold), load set 0 with tag 0
  Access 0x40: miss (conflict), evict tag 0, load tag 1
  Access 0x00: miss (conflict), evict tag 1, load tag 0
  Access 0x40: miss (conflict), evict tag 0, load tag 1
→ Every access is a miss despite only 2 distinct addresses!
```

A 2-way set-associative cache would hold both addresses simultaneously, turning every access after the first two into a hit.

## Cache Placement Policies

### Direct-Mapped Cache

Each memory block maps to exactly one cache set:

```
set_index = (block_number) mod (number_of_sets)
```

- **Pro**: simple hardware (one comparator per set), fast lookup.
- **Con**: susceptible to conflict misses.
- **Usage**: sometimes used for I$ (instruction cache) where conflicts are less common.

### N-Way Set-Associative Cache

Each memory block can occupy any of N slots within its set. Hardware checks all N tags in parallel:

```
set_index = (block_number) mod (number_of_sets)
within the set: any of the N "ways" can hold this block
```

Common configurations:
- L1: 4-way or 8-way (32–64 KB)
- L2: 8-way (256 KB–1 MB)
- L3: 16-way or higher (8–64 MB)

Increasing associativity reduces conflict misses but increases hardware cost (N comparators per set, N-input MUX to select hit way).

### Fully Associative Cache

A block can go anywhere in the entire cache. No conflict misses possible, but hardware must check all tags in parallel — expensive. Used only for small structures: TLBs (~64 entries), victim caches, prefetch buffers.

## Eviction Policies

When a set is full and a new line must be loaded, one existing line must be **evicted**:

| Policy | Description | Pro | Con |
|--------|-------------|-----|-----|
| LRU (Least Recently Used) | Evict the line not accessed for the longest time | Near-optimal for most workloads | Complex tracking hardware |
| Pseudo-LRU | Approximate LRU with fewer bits | Simple | Slightly suboptimal |
| Random | Evict a random way | Very simple hardware | ~10% worse than LRU in practice |
| FIFO | Evict the oldest loaded line | Simple | Poorer than LRU |
| NMRU (Not Most Recently Used) | Do not evict the most recently used | Simple | Good enough for high-associativity |

## Performance Impact: Row vs Column Traversal

In C, 2D arrays are stored in **row-major order**: `a[i][j]` is at address `base + i*N*4 + j*4`. Columns of the same row are adjacent in memory.

```c
int a[1024][1024];  // 4 MB array

// Cache-friendly (row-major scan, stride = 4 bytes):
for (i=0; i<1024; i++)
  for (j=0; j<1024; j++)
    sum += a[i][j];
// Each cache line (16 ints) is loaded once and fully used.
// Miss rate ≈ 1/16 = 6.25%

// Cache-hostile (column-major scan, stride = 4096 bytes = 1024 ints):
for (j=0; j<1024; j++)
  for (i=0; i<1024; i++)
    sum += a[i][j];
// Every access is to a different cache line.
// For a 32 KB L1 with 512 lines: each column scan evicts all lines.
// Miss rate ≈ 100%
// Measured slowdown: 10–50× on large matrices
```

**Cache blocking (tiling)**: reorder loops so a sub-matrix fits in cache, dramatically improving locality for matrix multiplication and similar operations. This is why NumPy/BLAS use hand-tuned blocking.

## AMAT (Average Memory Access Time)

```
AMAT = Hit_time_L1 + Miss_rate_L1 × (Hit_time_L2 + Miss_rate_L2 × Miss_penalty_memory)
```

For a two-level hierarchy:

```
L1 hit time:    1 cycle
L1 miss rate:   5%
L2 hit time:    10 cycles
L2 miss rate:   20%
Memory penalty: 100 cycles

AMAT = 1 + 0.05 × (10 + 0.20 × 100)
     = 1 + 0.05 × (10 + 20)
     = 1 + 0.05 × 30
     = 1 + 1.5 = 2.5 cycles
```

Without the L2 cache, AMAT = 1 + 0.05 × 100 = 6 cycles — the L2 cuts it by more than half.

## Prefetching

Hardware prefetchers detect access patterns and proactively load lines **before** they are requested:

- **Sequential prefetch**: detects stride-1 patterns (array scans). Works well for loops.
- **Stride prefetch**: detects constant-stride patterns (e.g., column access, every-other element).
- **Stream buffer**: a separate FIFO that issues prefetches ahead of sequential access.
- **Pointer prefetch**: harder to detect; linked-list traversal cannot be prefetched effectively.

Software can explicitly prefetch with `__builtin_prefetch(addr, rw, locality)` in GCC/Clang.
