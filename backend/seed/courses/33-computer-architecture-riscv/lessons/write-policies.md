# Write-Through vs Write-Back, Write Allocate

Every cache must answer two questions about writes: **where does the written data go immediately?** (the write policy) and **what happens on a write miss?** (the write-allocate policy). Getting these wrong is a common source of subtle bugs in systems programming and a favourite interview topic.

## Write-Through

On every store, data is written to **both the cache line and RAM simultaneously**.

```
CPU writes to address X
    → update cache line (if present)
    → immediately write to RAM
```

**Advantages:**
- RAM is always up-to-date. A downstream cache or DMA controller always sees fresh data.
- No dirty bit needed — every cache line always matches RAM.
- Cache flush on eviction is trivial: just discard the line, no write-back required.

**Disadvantages:**
- Every store generates a RAM write, consuming memory bus bandwidth even for temporary values.
- Effective bandwidth for write-intensive loops is limited by the RAM write speed, not the cache speed.

**Used in:** L1 caches on some simpler embedded processors; situations where cache coherence simplicity outweighs bandwidth cost.

A **write buffer** is typically added to absorb the RAM writes and let the CPU continue without stalling:

```
CPU → cache (write-through) → write buffer → RAM (async)
```

## Write-Back

On a store, data is written **only to the cache line**. A **dirty bit** marks that the line differs from RAM. The updated data is written to RAM only when the dirty line is evicted.

```
CPU writes to address X
    → update cache line
    → set dirty bit
    (RAM is NOT updated yet)

On eviction of dirty line:
    → write line to RAM
    → clear dirty bit
    → replace with new block
```

**Advantages:**
- Multiple writes to the same cache line (e.g., incrementing a counter in a loop) generate only one RAM write.
- Write-intensive loops run at cache speed, not RAM speed.
- Bandwidth to RAM is dramatically lower for typical write-heavy workloads.

**Disadvantages:**
- RAM may hold stale data at any point. An I/O device doing DMA must flush or bypass cache.
- Eviction is more complex: must check dirty bit and conditionally write back.
- Cache coherence in multi-core systems is more complex (MESI protocol manages dirty states).

**Used in:** Nearly all modern L1, L2, and L3 caches.

## Side-by-Side Comparison

| Property             | Write-Through         | Write-Back            |
|----------------------|-----------------------|-----------------------|
| RAM always up-to-date| Yes                   | No (stale until evict)|
| Dirty bit needed     | No                    | Yes                   |
| Write bandwidth      | High (every store)    | Low (only on evict)   |
| Complexity           | Simple                | More complex          |
| Typical use          | Small embedded caches | Modern CPUs (L1-L3)   |

## Write-Allocate (Fetch on Write)

Write-allocate answers the question: **what happens on a write miss?**

- **Write-allocate (fetch on write):** On a write miss, fetch the block from RAM into cache, then perform the write in cache. Subsequent reads to the same line hit in cache.
- **No-write-allocate (write around):** On a write miss, write directly to RAM without loading the block into cache.

These two pair naturally with the above policies:

| Write policy   | Typical write-miss policy |
|----------------|--------------------------|
| Write-back     | Write-allocate           |
| Write-through  | No-write-allocate        |

The pairing makes sense: write-back caches want writes to land in cache (to batch up RAM writes), so they allocate on a miss. Write-through caches write to RAM on every store anyway, so fetching the block first would waste bandwidth.

## Worked Example: Write-Back + Write-Allocate

```c
int arr[16384];  // 64 KB, all cache misses initially

for (int i = 0; i < 16384; i++)
    arr[i] = i * 2;   // pure write loop
```

With **write-back + write-allocate**:
1. `arr[0]` write miss → fetch 64-byte line (16 ints) from RAM into cache.
2. Write `arr[0]` in cache, set dirty bit.
3. `arr[1]` through `arr[15]` → hits in cache (same line).
4. When the line is evicted → one write-back to RAM.

Result: 1 cache line fetch + 1 write-back per 16 elements = excellent bandwidth efficiency.

With **write-through + no-write-allocate**:
- Every `arr[i]` write goes to RAM immediately.
- No lines are allocated.
- RAM write for every single element — limited by RAM bandwidth.

## Common Pitfall: Cache Flushing for DMA

In write-back systems, before initiating a DMA transfer from a memory buffer, the programmer (or OS) must **flush** the dirty cache lines to RAM so the DMA controller sees the updated data. Forgetting this is a classic embedded systems bug.

```c
// Before DMA read (device reads from RAM)
__flush_cache_range(buffer, size);  // write dirty lines back to RAM
dma_start_transfer(buffer, size);
```

> **Interview answer:** Write-through sends every store to RAM immediately — simple but bandwidth-hungry. Write-back marks the line dirty and writes to RAM only on eviction — efficient for write-heavy loops but requires dirty-bit tracking and cache flushing before DMA. Write-back is almost always paired with write-allocate: on a write miss, fetch the block first, write in cache, and batch the RAM update.
