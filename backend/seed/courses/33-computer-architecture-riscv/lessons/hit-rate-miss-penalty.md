# Hit Rate, Miss Rate, and the Three Cs

Understanding *how* a cache behaves qualitatively is useful; being able to quantify its impact on performance is essential for interviews and real optimisation work. Two metrics — **hit rate** and **miss penalty** — combine into a single equation that predicts memory system performance. The **Three Cs** framework categorises misses to guide architectural decisions.

## Core Definitions

- **Hit rate (h):** Fraction of accesses satisfied by the cache.
- **Miss rate (m):** `m = 1 - h`
- **Hit time (t_hit):** Latency to read from cache on a hit (typically 1–5 cycles for L1).
- **Miss penalty (t_miss):** Additional latency incurred on a miss (to fetch from the next level).

## Average Memory Access Time (AMAT)

The key formula every architecture candidate must know:

```
AMAT = t_hit + m * t_miss
```

For a two-level hierarchy (L1 → RAM):

```
AMAT = L1_hit_time + L1_miss_rate * (L2_hit_time + L2_miss_rate * RAM_latency)
```

### Worked Example

| Parameter     | Value         |
|---------------|---------------|
| L1 hit time   | 4 cycles      |
| L1 miss rate  | 5% (0.05)     |
| L2 hit time   | 12 cycles     |
| L2 miss rate  | 20% (0.20)    |
| RAM latency   | 200 cycles    |

```
AMAT = 4 + 0.05 * (12 + 0.20 * 200)
     = 4 + 0.05 * (12 + 40)
     = 4 + 0.05 * 52
     = 4 + 2.6
     = 6.6 cycles
```

Without cache: AMAT = 200 cycles. With two cache levels: 6.6 cycles — a 30× improvement.

## Sensitivity Analysis

The formula reveals two handles for optimisation:

1. **Reduce miss rate** — better organisation (higher associativity), larger cache, better replacement policy, smarter data layout.
2. **Reduce miss penalty** — deeper cache hierarchy, prefetching, non-blocking (out-of-order) memory requests, faster RAM technology.

Reducing hit time also matters but is constrained by physics (smaller cache = faster access, larger = slower).

## The Three Cs of Cache Misses

Coined by Mark Hill in 1987, the **Three Cs** classify every cache miss into one of three categories:

### 1. Compulsory (Cold) Misses

The first access to any block is always a miss — the block has never been in cache. These are unavoidable regardless of cache size or organisation.

- **Reduced by:** larger cache lines (prefetch more spatial context), hardware prefetchers.
- **Not helped by:** larger cache or higher associativity.

### 2. Capacity Misses

The working set is larger than the cache. Even a fully associative cache of the same size would miss, because the data simply does not fit.

- **Reduced by:** larger cache, better data layout (reducing working set size), loop tiling / blocking.
- **Not helped by:** higher associativity.

```c
// Loop tiling reduces working set for matrix multiplication:
// Instead of accessing full rows/columns, work on B×B tiles
for (int i = 0; i < N; i += B)
  for (int j = 0; j < N; j += B)
    for (int k = 0; k < N; k += B)
      // compute B×B tile — fits in cache
```

### 3. Conflict Misses

Multiple blocks compete for the same cache set and evict each other, even though other sets are empty. Exclusive to direct-mapped and low-associativity caches.

- **Reduced by:** higher associativity, padding arrays to avoid aliasing, victim caches.
- **Not helped by:** larger cache (unless the extra capacity breaks the conflict pattern).

### Summary Table

| Miss type   | Cause                           | Fix                                  |
|-------------|---------------------------------|--------------------------------------|
| Compulsory  | First access ever               | Larger lines, prefetch               |
| Capacity    | Working set > cache size        | Larger cache, loop tiling            |
| Conflict    | Too many blocks → same set      | Higher associativity, array padding  |

A fourth C — **Coherence misses** — is sometimes added for multi-core systems where cache invalidations due to coherence traffic cause misses that would not occur in a single-core setting.

## Quick Mental Model

When analysing cache performance:

1. Start with AMAT — which level has the highest miss rate?
2. Categorise the misses — which of the Three Cs dominates?
3. Apply the right fix — do not add associativity to solve a capacity problem.

> **Interview answer:** AMAT = hit_time + miss_rate × miss_penalty. The Three Cs classify misses as compulsory (first access — unavoidable), capacity (working set too large — needs bigger cache or tiling), and conflict (set competition — needs higher associativity or padding). Identifying which C dominates tells you exactly what to fix.
