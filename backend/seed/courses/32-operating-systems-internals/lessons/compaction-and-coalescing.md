# Compaction and Free-Block Coalescing

External fragmentation accumulates over time no matter which allocation strategy is used. Two complementary techniques fight it: **coalescing** merges adjacent free blocks immediately when they are freed, and **compaction** relocates live allocations to eliminate all holes at once. They operate at different costs and are used in different contexts.

## Free-Block Coalescing

**Coalescing** (also called *merging*) detects when a newly freed block is physically adjacent to another free block and merges them into one larger free block.

### Why It Matters

Without coalescing:

```
After freeing block B:
[FREE 8KB: A] [FREE 4KB: B] [FREE 6KB: C]
→ Three separate holes; a 10 KB request fails.
```

With coalescing:

```
Free B → merge A+B+C → [FREE 18KB]
→ One 18 KB hole; 10 KB request succeeds.
```

### When to Coalesce

| Strategy | Description |
|---|---|
| **Immediate coalescing** | Merge adjacent free blocks the moment a block is freed. Simple; prevents fragmentation from building up. |
| **Deferred coalescing** | Batch free blocks and coalesce lazily. Can be faster in allocation-heavy workloads at the cost of temporarily fragmented state. |

Most real allocators (glibc `malloc`, jemalloc) use **immediate coalescing** because the latency of checking two neighbors during a `free()` call is trivial.

### Boundary Tags (Knuth's Trick)

To coalesce efficiently in O(1), each block stores its size at both ends — a **header** and a **footer** (boundary tag):

```
+--------+------------------+--------+
| size|A |    payload ...   | size|A |
+--------+------------------+--------+
  header                      footer
```

- `A` = allocated bit (1 = in use, 0 = free)
- When freeing a block, read the **footer of the previous block** and the **header of the next block** in O(1) — no list traversal needed.

```c
// Pseudocode: coalesce on free
void coalesce(Block* b) {
    bool prev_free = prev_block(b)->footer.free;
    bool next_free = next_block(b)->header.free;

    if (!prev_free && !next_free) return;          // no merge
    if (!prev_free && next_free)  merge(b, next_block(b));
    if (prev_free  && !next_free) merge(prev_block(b), b);
    if (prev_free  && next_free)  merge(prev_block(b), b, next_block(b));
}
```

## Memory Compaction

**Compaction** physically relocates all live (in-use) allocations to one end of the address space, gathering all free space into a single large contiguous block.

```
Before compaction:
[P1:10MB][FREE:3MB][P2:7MB][FREE:2MB][P3:5MB][FREE:8MB]

After compaction:
[P1:10MB][P2:7MB][P3:5MB][FREE:13MB]
```

Now a 12 MB request that would have failed can succeed.

### Requirements for Compaction

Compaction is only safe when the system uses **relocatable addresses** — typically logical/virtual addresses that are translated through a hardware register (base register or page table). The OS can:

1. Pause the process.
2. Copy its memory to a new physical location.
3. Update the process's base register or page table.
4. Resume the process — it sees the same logical addresses, now backed by different physical frames.

In systems with **physical addresses hard-coded into programs** (early embedded or real-mode DOS programs), compaction is impossible without corrupting the program.

### Cost of Compaction

Compaction is expensive:

- **Time:** O(total live memory) — every byte of live data must be copied.
- **Downtime:** The process (or the whole system) must be paused during copying.
- **Frequency:** Cannot be done on every allocation; typically triggered when free space drops below a threshold.

```
Cost example:
System RAM: 4 GB
Live data:  3 GB
Compaction must copy 3 GB at ~10 GB/s → ~300 ms pause time
```

### Compaction in Practice

- **Java GC (G1, ZGC):** Compaction is a key phase of garbage collection. ZGC performs *concurrent compaction* using load barriers to avoid stop-the-world pauses.
- **Linux kernel:** The kernel does not compact physical memory for user processes (it uses paging instead). However, `MADV_FREE` and `khugepaged` perform a form of page-level rearrangement.
- **Defragmentation:** Storage-level analogs (disk defrag, ext4 online defrag) apply the same principle to file extents.

## Coalescing vs. Compaction

| Property | Coalescing | Compaction |
|---|---|---|
| When applied | At every `free()` call | Periodically / on demand |
| Cost | O(1) per free | O(live memory) |
| Scope | Merges adjacent free blocks | Moves all live data |
| Requires relocation? | No | Yes |
| Eliminates all external fragmentation? | No (non-adjacent holes remain) | Yes |

## Common Pitfalls

- Forgetting that coalescing only merges **adjacent** blocks — non-adjacent holes remain separate until compaction.
- Assuming compaction is always possible — it requires relocatable addresses.
- Overlooking the **stop-the-world** cost of compaction in latency-sensitive applications.

**Interview answer:** Coalescing merges adjacent free blocks when memory is released, preventing fragmentation from accumulating — it runs in O(1) using boundary tags. Compaction physically moves all live allocations to one end, creating a single large free region — it eliminates all external fragmentation but requires relocatable addresses and incurs high copying cost.
