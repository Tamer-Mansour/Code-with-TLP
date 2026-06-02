# The Heap, malloc/free, and Allocators

The **heap** is the memory region from which programs request variable-sized, long-lived allocations at runtime. It is managed by a **memory allocator** — a library layer sitting between your code and the OS. Understanding how allocators work explains why `malloc` is slow, why fragmentation happens, and how to write memory-efficient programs.

## How malloc Works at a High Level

When you call `malloc(n)`, the allocator:

1. Looks in its **free list** for a block of at least `n` bytes.
2. If found, removes that block from the free list and returns a pointer to it.
3. If not found, requests more memory from the OS via `sbrk()` or `mmap()`.
4. Returns a pointer to the usable region; stores metadata (size, flags) just before or after it.

```c
int *p = malloc(4 * sizeof(int));   // allocate 16 bytes on the heap
if (p == NULL) { /* handle OOM */ }
p[0] = 1;
p[3] = 99;
free(p);                            // return memory to the allocator
p = NULL;                           // best practice: null the pointer
```

## The Free List and Block Headers

Most allocators store a small **header** immediately before each allocation:

```
[ size | flags | ... ] [ user data ............. ] [ optional footer ]
^-- header (hidden)    ^-- pointer returned to you
```

When you call `free(p)`, the allocator steps back by `sizeof(header)` bytes to read the block size, then inserts the block back into the free list.

## Fragmentation

Two kinds of fragmentation reduce effective memory utilization:

- **Internal fragmentation** — the allocator rounds up requests to alignment boundaries, wasting space inside blocks (e.g., a 17-byte request might get a 24-byte block).
- **External fragmentation** — after many allocations and frees, the free list becomes a patchwork of small, non-contiguous blocks. A large request may fail even when total free bytes are sufficient.

```
[ used 8B ] [ free 4B ] [ used 8B ] [ free 4B ] [ used 8B ]
   Total free = 8 B, but largest contiguous = 4 B
```

## Common Allocator Strategies

| Strategy | Description | Trade-off |
|---|---|---|
| First-fit | Use first block that's big enough | Fast, may fragment |
| Best-fit | Use smallest block that fits | Less waste, slower search |
| Buddy system | Split/merge powers-of-two blocks | Fast merge, internal waste |
| Slab allocator | Fixed-size pools per object type | Zero fragmentation for known sizes |

Linux's **glibc** allocator (`ptmalloc`) uses a combination of bins (size-segregated free lists) and arenas (per-thread caches) to reduce lock contention in multi-threaded programs. Modern alternatives like **jemalloc** and **tcmalloc** further improve multi-threaded throughput.

## calloc and realloc

```c
// calloc: allocate and zero-initialize
int *arr = calloc(100, sizeof(int));   // 400 bytes, all zeroes

// realloc: resize an existing allocation
arr = realloc(arr, 200 * sizeof(int)); // may move the data!
```

`realloc` may return a **different pointer** if it must move the block. Never assign back to the same pointer without saving the old one first — if `realloc` returns `NULL`, the original allocation is still valid and you'll have a leak.

```c
int *tmp = realloc(arr, new_size);
if (tmp == NULL) { /* handle error, arr still valid */ }
else arr = tmp;
```

## The OS Perspective: sbrk vs mmap

For small allocations, the allocator extends the heap with `sbrk()`, moving the **program break** (end of data segment) upward. For large allocations (typically >128 KB in glibc), it uses `mmap()` to get an anonymous page, which can be returned to the OS immediately with `munmap()` on `free`. Small blocks returned to the free list are never given back to the OS unless explicitly trimmed with `malloc_trim()`.

## Interview Answer

> "`malloc` searches a free list of previously freed blocks, returning a pointer to a usable region with hidden size metadata. If no block fits, it asks the OS for more memory via `sbrk` or `mmap`. `free` reads that metadata to reinsert the block. External fragmentation arises when free blocks become non-contiguous."
