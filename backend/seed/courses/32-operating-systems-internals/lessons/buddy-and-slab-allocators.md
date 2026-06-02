# Buddy System and Slab Allocators

The heap allocators discussed so far — first-fit, best-fit — maintain a generic free list. Two specialized allocators dominate operating system kernel internals: the **Buddy System** for large, power-of-two-aligned allocations, and the **Slab Allocator** for repeated small fixed-size kernel object allocations. Both are designed to minimize fragmentation and maximize allocation speed.

## The Buddy System

The Buddy System, developed by Knuth and popularized by Linux's physical memory manager, partitions memory into blocks whose sizes are always **powers of two**.

### Core Idea

- The entire memory pool starts as one block of size `2^k` (e.g., 1 GB = 2^30 bytes).
- To satisfy a request of size `n`, find the smallest `2^m ≥ n`.
- If the exact size block is unavailable, **split** a larger block in half repeatedly until you have the right size. The two halves are each other's "buddies."
- When a block is freed, check if its buddy is also free. If so, **merge** them back into a block of size `2^(m+1)`. Repeat up the chain.

### Split and Merge Example

```
Memory: 64 KB, request for 10 KB (→ round up to 16 KB = 2^14)

Initial state:       [64 KB free]
Split 64 → 2×32:    [32 KB free] [32 KB free]
Split 32 → 2×16:    [16 KB free] [16 KB free] [32 KB free]
Allocate 16 KB:      [16 KB USED] [16 KB free] [32 KB free]

Free the 16 KB block:
Buddy (next 16 KB) is free → merge:  [32 KB free] [32 KB free]
Buddies both free → merge:            [64 KB free]
```

### Finding a Buddy

The buddy of a block at address `A` with size `2^k` is at:

```
buddy_addr = A XOR (1 << k)
```

This XOR trick makes buddy lookup O(1).

### Linux Implementation

Linux uses the buddy system in `mm/page_alloc.c`. The kernel maintains **11 free lists** (order 0 to 10), where order `k` holds blocks of `2^k` pages (4 KB each). `alloc_pages(GFP_KERNEL, order)` allocates from the appropriate list.

```
Order 0: 4 KB blocks
Order 1: 8 KB blocks
Order 2: 16 KB blocks
...
Order 10: 4 MB blocks
```

### Buddy System Properties

| Property | Value |
|---|---|
| Allocation time | O(log n) — walk up the free lists |
| Fragmentation | Internal (rounds up to power of 2), no external |
| Maximum waste | ~50% (a 5 KB request allocates 8 KB, wasting 3 KB) |
| Merging time | O(log n) — propagate merges up the chain |

## The Slab Allocator

The Buddy System works well for page-granularity allocations, but a kernel constantly creates and destroys small fixed-size objects: `task_struct`, `inode`, `file`, `socket`. Allocating and freeing these with the buddy system would waste memory and time. The **Slab Allocator** (introduced by Jeff Bonwick for SunOS, adopted by Linux) pre-allocates caches of objects that stay initialized between uses.

### Three-Level Structure

```
Cache (e.g., "task_struct cache")
  └── Slab (one or more buddy-allocated pages)
        └── Objects (fixed-size, pre-initialized)
```

- **Cache:** Named for the object type. Holds a list of slabs.
- **Slab:** A chunk of physically contiguous pages divided into equal-size slots.
- **Object:** A single pre-initialized instance. When freed, it is returned to the slab — not zeroed — keeping constructor-initialized state intact.

### Allocation Flow

```
1. Look up the cache for the requested object type.
2. Find a slab with a free slot (partial slab → full slab list).
3. Return the pre-initialized object in O(1).

On free:
1. Mark the slot free in the slab's bitmap.
2. If the whole slab is free, optionally return pages to the buddy system.
```

### Why Keep Objects Initialized?

Kernel objects often have expensive constructors: spinlock initialization, list-head setup, reference counter init. The slab allocator avoids re-running constructors on every allocation by keeping the object's invariant state (spinlocks, list pointers) intact after a `free`, only reinitializing the data-specific fields on reuse.

### Slab Variants in Linux

| Allocator | Key Feature |
|---|---|
| SLAB | Original, full-featured, per-CPU caches |
| SLUB | Simplified, default since Linux 2.6.23, better for multi-core |
| SLOB | Minimal memory use for embedded/tiny systems |

`kmalloc()` in Linux uses SLUB internally for arbitrary small allocations.

### Slab Properties

| Property | Value |
|---|---|
| Allocation time | O(1) — index into per-CPU cache |
| Fragmentation | Internal only (fixed slot size); zero external within a slab |
| Overhead | Pre-allocated pool may hold unused initialized objects |
| Cache coloring | Offsets objects within slabs to improve CPU cache line utilization |

## Buddy vs. Slab Comparison

| Feature | Buddy System | Slab Allocator |
|---|---|---|
| Granularity | Pages (powers of 2) | Fixed-size objects (bytes) |
| Primary use | Physical page management | Kernel object caches |
| Fragmentation | Internal (power-of-2 rounding) | Internal (slot size rounding) |
| Speed | O(log n) | O(1) |
| Constructor caching | No | Yes |

**Interview answer:** The Buddy System splits memory into power-of-two blocks, enabling O(log n) allocation and fast merging via XOR buddy addresses — it underpins Linux's physical page allocator. The Slab Allocator maintains caches of pre-initialized fixed-size kernel objects for O(1) allocation, eliminating constructor overhead and reducing internal fragmentation for small objects.
