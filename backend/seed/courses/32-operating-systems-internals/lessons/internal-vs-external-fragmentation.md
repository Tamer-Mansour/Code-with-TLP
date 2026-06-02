# Internal vs External Fragmentation

Fragmentation is the enemy of memory efficiency. It describes memory that is wasted — either because it belongs to a process that cannot use it, or because it sits between allocations in pieces too small to satisfy any new request. There are two distinct varieties, and confusing them in an interview is a common mistake.

## Internal Fragmentation

**Internal fragmentation** occurs when the allocator gives a process *more* memory than it requested — and the extra bytes are wasted inside the allocated block.

### Why It Happens

Fixed-size allocation units cause internal fragmentation. If a system allocates memory in 4 KB pages and a process needs 6 KB, it receives two pages (8 KB). The extra 2 KB are mapped to the process but cannot be used for anything else — they are "internal" to that allocation.

```
Request: 6 KB
Allocated: 8 KB (2 pages × 4 KB)
Internal fragmentation: 2 KB
```

Slab allocators and fixed-partition memory schemes also suffer from this. A slab for 64-byte objects will waste `64 - actual_size` bytes per object if objects are smaller than 64 bytes.

### Internal Fragmentation Formula

```
internal_fragmentation = allocated_size - requested_size
```

Total internal fragmentation across all allocations = Σ (allocated_i - requested_i).

## External Fragmentation

**External fragmentation** occurs when there is enough total free memory to satisfy a request, but that memory is scattered in small, non-contiguous chunks that cannot be combined without moving existing allocations.

### Why It Happens

Variable-size allocation creates external fragmentation. When processes are loaded and freed in varying sizes, the free space is divided into holes of different sizes scattered throughout physical (or virtual) memory.

```
Memory layout (each cell = 1 MB):
[P1:4MB][FREE:2MB][P2:3MB][FREE:1MB][P3:5MB][FREE:3MB]

New request: 5 MB
Total free = 2 + 1 + 3 = 6 MB  ✓ enough
But largest contiguous block = 3 MB  ✗ request fails
→ External fragmentation!
```

### The 50-Percent Rule

Donald Knuth showed empirically that with random allocations and frees, roughly **one-third of memory** ends up as unusable external fragments — meaning about half of all free memory is lost to fragmentation. This is why allocation algorithms matter.

## Side-by-Side Comparison

| Property | Internal Fragmentation | External Fragmentation |
|---|---|---|
| Location of waste | Inside an allocated block | Between allocated blocks |
| Cause | Fixed/rounded allocation sizes | Variable-size allocations and frees |
| Measurement | allocated - requested | total free - largest contiguous free |
| Primary schemes affected | Paging, slab, fixed partitions | Segmentation, buddy system (partially), heap allocators |
| Mitigation | Smaller allocation units | Compaction, coalescing, better fit strategies |

## Which Scheme Causes Which?

- **Pure paging** → internal fragmentation (the last page of any allocation is often partially used), zero external fragmentation.
- **Pure segmentation** → external fragmentation (variable-length segments leave holes), zero internal fragmentation.
- **Segmented paging** → small internal fragmentation (last page of each segment), zero external fragmentation.

## Worked Example

A 64 MB physical memory system uses variable-length allocation. After several alloc/free cycles:

| Region | State | Size |
|---|---|---|
| 0x00 – 0x3F | Process A | 64 MB... |

More practically:

```
[USED 10MB][FREE 3MB][USED 7MB][FREE 2MB][USED 15MB][FREE 8MB]
```

A request for 10 MB arrives:
- Total free = 3 + 2 + 8 = 13 MB (enough in aggregate)
- Largest contiguous = 8 MB (not enough for 10 MB)
- Result: external fragmentation causes allocation failure even with 13 MB free.

## Common Pitfalls

- Saying paging "has no fragmentation" — it has internal fragmentation on the last page of every allocation.
- Saying segmentation "has no fragmentation" — it has severe external fragmentation.
- Forgetting that 32-byte malloc overhead per object is a form of internal fragmentation imposed by the allocator's header.

**Interview answer:** Internal fragmentation is wasted space inside an allocated block when the allocator rounds up to a fixed unit size. External fragmentation is wasted space between allocations — enough total free memory exists but it is not contiguous. Paging causes internal fragmentation; segmentation causes external fragmentation.
