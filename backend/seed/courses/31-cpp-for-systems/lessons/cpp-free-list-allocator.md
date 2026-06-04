# Memory Allocator: Free List Simulation

This advanced exercise puts you inside the allocator — the layer that every `new`, `malloc`, and `std::vector` growth operation ultimately calls. Implementing a first-fit free-list allocator from scratch reveals why heap allocation is expensive, why fragmentation matters, and how real allocators like jemalloc and tcmalloc are designed to avoid these problems.

## What You Are Building

Manage a fixed-size byte array as a heap. Maintain a sorted list of free regions. On each `ALLOC`, scan for the first region large enough (first-fit), carve it out, and print the address range. On each `FREE`, return the region and immediately merge it with any adjacent free regions (coalescing).

See the prompt for full input/output specification.

## Core Data Structures

```python
# List of (start, end) tuples for free regions, kept sorted by start address
free_list = [(0, heap_size)]

# Map from handle name to (start, end) of allocated block
allocated = {}
```

## First-Fit Placement

Scan `free_list` from lowest address upward. Use the first region where `end - start >= size`. This is O(n) per allocation in the worst case, which is why production allocators use size-segregated free lists (tcmalloc) or buddy systems (Linux kernel) instead.

## Immediate Coalescing

After returning a block to the free list, merge adjacent free regions:

```python
def coalesce(fl):
    fl.sort()
    merged = []
    for seg in fl:
        if merged and merged[-1][1] == seg[0]:
            merged[-1] = (merged[-1][0], seg[1])
        else:
            merged.append(list(seg))
    return [tuple(s) for s in merged]
```

Without coalescing, freed blocks become isolated fragments that cannot satisfy large requests even when the total free bytes would be sufficient. This is **external fragmentation**.

## Why This Matters in Systems Programming

| Allocator concern | Cause | Solution used by real allocators |
|---|---|---|
| External fragmentation | Freed blocks split by live allocations | Coalescing + compaction |
| Internal fragmentation | Block size rounded up to alignment | Size classes (tcmalloc) |
| Allocation speed | First-fit O(n) scan | Per-size free lists, O(1) dequeue |
| Thread contention | Global free list needs a lock | Per-thread caches (jemalloc) |

For deeper reading on heap allocator internals, see *Effective Programming in C and C++* (MIT 6.S096) at [https://ocw.mit.edu/courses/6-s096-effective-programming-in-c-and-c-january-iap-2014/](https://ocw.mit.edu/courses/6-s096-effective-programming-in-c-and-c-january-iap-2014/).

The [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines) rule **R.10** explains why custom allocators are sometimes necessary:

> Avoid `malloc()` and `free()`. Use `new`/`delete` or RAII resource wrappers.

But guideline **Per.7** notes that for performance-critical code, a custom pool allocator that avoids the general-purpose heap entirely can be the right tool.
