# Why Heap Allocation Is Expensive

Calling `new` or `malloc` looks like a single line of code, but underneath it triggers a chain of work that can cost hundreds of nanoseconds — orders of magnitude slower than a stack allocation.

## Stack vs Heap Allocation Speed

| Operation | Typical cost |
|-----------|-------------|
| Stack allocation (adjust RSP) | ~0 cycles (folded into frame setup) |
| `malloc` / `new` (small object, free list hit) | 20–100 ns |
| `malloc` / `new` (requires `mmap`/`brk`) | 1–10 µs |
| `free` / `delete` | 10–60 ns |

## What the Allocator Must Do

### 1. Find a Free Block (Search)

The allocator maintains free lists or trees keyed by size. A request for 64 bytes might scan a bin of 64-byte blocks. If none exists, it splits a larger block.

```
[Free list for 64 bytes]  ->  [block A] -> [block C] -> NULL
```

### 2. Update Metadata

Every heap block carries a header (size, flags, maybe a checksum). On allocation the header is written; on free it must be read, validated, and the block re-inserted into the correct list.

```
| header (16 B) | user data (N B) | footer / next-block header |
```

### 3. Thread Synchronization

The global heap is shared across threads. Traditional allocators take a mutex on every call — a potential bottleneck in multithreaded code.

Modern allocators (tcmalloc, jemalloc) use **per-thread caches** (thread-local free lists) so that most small allocations never touch a global lock.

### 4. Potential System Call

If the allocator has no memory left, it calls `brk()` or `mmap()` to request pages from the OS. System calls cost thousands of cycles due to the user-to-kernel-to-user transition.

```cpp
// This loop may trigger multiple mmap calls if the heap is empty
std::vector<int*> v;
for (int i = 0; i < 1'000'000; ++i)
    v.push_back(new int(i));
```

## Fragmentation

Even if the total free memory is large, the allocator may not satisfy a request if free blocks are all smaller than what is needed (external fragmentation). This wastes memory and slows future allocations.

```
[used 8B][free 8B][used 8B][free 8B] ...
// request for 16 B fails despite 16+ B of total free space
```

Internal fragmentation also occurs when the allocator rounds allocations up to alignment boundaries.

## Cache Effects

Heap objects are placed wherever the allocator finds space. Unrelated objects created at different times may land in the same cache line, causing **false sharing** in multithreaded code. Related objects may live in different cache lines, causing cache misses on traversal.

```cpp
// Bad: pointer-chasing through the heap
struct Node { int val; Node* next; };
Node* head = build_linked_list(100000);
// Each node likely in a different cache line -> cache miss per step
```

## Mitigation Techniques

- **Arena/pool allocators:** Allocate a large slab once, then hand out fixed-size chunks with a pointer bump. O(1) allocation, zero fragmentation for same-size objects.
- **Stack allocation for small temporaries:** `alloca`, VLAs (GCC extension), or simply declare on the stack.
- **`std::pmr` (C++17):** Polymorphic Memory Resources allow swapping allocators without changing container types.

```cpp
#include <memory_resource>

std::byte buf[4096];
std::pmr::monotonic_buffer_resource pool(buf, sizeof(buf));
std::pmr::vector<int> v(&pool);   // allocates from stack buffer — no heap calls
```

- **Object pools:** Pre-allocate N objects of type T; hand out and return pointers. Common in game engines and embedded systems.

> **Interview answer:** Heap allocation is expensive because the allocator must search free lists, update metadata headers, potentially acquire a lock in multithreaded code, and may issue a system call to obtain more pages. Stack allocation is just a pointer decrement folded into the function prologue.
