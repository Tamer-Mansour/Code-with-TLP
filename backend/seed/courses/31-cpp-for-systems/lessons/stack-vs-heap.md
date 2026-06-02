# Stack vs Heap: What Is the Difference?

The stack and heap are both regions of RAM, but they differ in ownership, speed, size limits, and the kind of problems they cause when misused.

## Side-by-Side Comparison

| Property | Stack | Heap |
|----------|-------|------|
| Allocation mechanism | Move stack pointer (one instruction) | Allocator search + bookkeeping |
| Typical size | 1–8 MB per thread | Virtual memory limit (GBs) |
| Fragmentation | Never | Grows over time |
| Lifetime | Tied to scope/function | Until `delete`/`free` |
| Thread safety | Each thread has its own | Shared; allocator must lock |
| Failure mode | Stack overflow (guard page) | `nullptr` / `std::bad_alloc` |

## Stack Allocation

When you declare a local variable, the compiler reserves space by adjusting the stack pointer (RSP on x86-64). No system call is needed. The pointer moves back when the function returns, effectively "freeing" everything in one step.

```cpp
void compute() {
    int a = 1;          // RSP -= 4 (conceptually)
    double b = 3.14;    // RSP -= 8
    char buf[64];       // RSP -= 64
    // ... on return, RSP is restored — all gone
}
```

The compiler knows every size at compile time, so it lays the frame out statically. Access is a single `[rbp - offset]` memory reference — blazingly fast.

## Heap Allocation

`new` / `malloc` calls into an allocator (e.g., `ptmalloc`, `jemalloc`, `tcmalloc`). The allocator:

1. Searches a free-list for a block of suitable size.
2. Updates metadata (size headers, linked-list pointers).
3. May call `mmap` or `brk` to ask the OS for more pages.
4. Returns a pointer to the caller.

```cpp
int* arr = new int[1000];   // heap — survives beyond this scope
// ...
delete[] arr;               // must be paired manually
```

Because the object outlives its creating scope, it can be shared across threads and returned from functions safely — but it must be explicitly released.

## Cache Performance Implications

Stack memory is used sequentially and is often already hot in L1/L2 cache. Heap objects can be scattered across physical pages, causing cache misses.

```cpp
// Cache-friendly: contiguous stack array
int stack_arr[64];
for (int i = 0; i < 64; ++i) stack_arr[i] = i;

// Potentially cache-unfriendly: many small heap objects
std::vector<int*> ptrs;
for (int i = 0; i < 64; ++i) ptrs.push_back(new int(i));
```

## Common Pitfalls

**Returning a pointer to a stack variable (dangling pointer):**

```cpp
int* bad() {
    int x = 42;
    return &x;   // UB: x is destroyed when bad() returns
}
```

**Stack overflow from over-large locals:**

```cpp
void explode() {
    int matrix[1024][1024];  // 4 MB on the stack — likely stack overflow
}
```

**Memory leak (heap object never freed):**

```cpp
void leak() {
    int* p = new int(5);
    // forgot delete p; — object leaks
}
```

## Modern C++ Guidance

Use RAII types (`std::vector`, `std::unique_ptr`, `std::string`) instead of raw `new`/`delete`. They live on the stack themselves but manage heap memory automatically, giving you the lifetime safety of the stack with the unlimited size of the heap.

```cpp
void safe() {
    std::vector<int> v(1000);   // buffer on heap, metadata on stack
    // v is destroyed automatically when safe() returns
}
```

> **Interview answer:** Stack allocation is a single pointer adjustment — O(1) and cache-friendly — but space is limited and lifetime is tied to the scope. Heap allocation is slower due to allocator bookkeeping, but objects can be arbitrarily large and long-lived.
