# Stack vs Heap: Allocation, Lifetime, and Speed

Every running process gets two primary memory regions for dynamic data: the **stack** and the **heap**. Understanding where data lives, how long it lives, and how fast it can be allocated is essential knowledge for writing correct and efficient software — and for acing systems interviews.

## The Stack

The stack is a contiguous block of memory managed automatically by the CPU and compiler. When you call a function, the CPU pushes a new **stack frame** onto the stack containing local variables, return addresses, and saved registers. When the function returns, that frame is popped and the memory is instantly reclaimed.

Key characteristics:

- **LIFO discipline** — memory is freed in the reverse order it was allocated.
- **Allocation speed** — essentially a single instruction: decrement the stack pointer (`RSP` on x86-64).
- **Lifetime** — tied to the enclosing scope; the compiler determines this at compile time.
- **Size limit** — typically 1–8 MB per thread (OS-configured). Exceeding it causes a stack overflow.
- **No fragmentation** — grows and shrinks from one end.

```c
void foo(void) {
    int x = 42;        // lives on the stack
    char buf[256];     // also on the stack
}                      // x and buf destroyed here automatically
```

## The Heap

The heap is a large pool of memory managed by the runtime allocator (e.g., `malloc`/`free` in C, `new`/`delete` in C++, or a garbage collector in higher-level languages). The programmer (or GC) explicitly controls allocation and deallocation.

Key characteristics:

- **Manual or GC-managed lifetime** — memory persists until explicitly freed (or GC collects it).
- **Allocation speed** — slower; the allocator must search free lists, merge blocks, and possibly call `mmap`/`sbrk` for more pages.
- **Size** — limited only by available virtual address space (gigabytes).
- **Fragmentation** — both internal (wasted padding) and external (unusable gaps between allocations) can occur.

```c
int *arr = malloc(1000 * sizeof(int));  // on the heap
arr[0] = 99;
free(arr);   // programmer must free it
```

## Side-by-Side Comparison

| Property | Stack | Heap |
|---|---|---|
| Managed by | Compiler / CPU | Programmer / Allocator / GC |
| Speed | O(1), ~1 instruction | Slower (free list search) |
| Size | Small (1–8 MB) | Large (limited by VM) |
| Lifetime | Automatic (scope-bound) | Manual or GC |
| Fragmentation | None | Possible |
| Thread safety | Per-thread (no sharing) | Shared; needs synchronization |
| Overflow risk | Stack overflow | `NULL` return on OOM |

## When to Use Which

Use the **stack** for:
- Small, fixed-size local variables
- Temporary buffers you know won't outlive the function
- Performance-critical code where allocation speed matters

Use the **heap** for:
- Data that must outlive a function call
- Large allocations (arrays, strings, graphs)
- Data whose size is not known at compile time

## Worked Example: Return Pointer Bug

A classic mistake is returning a pointer to a stack-allocated variable:

```c
int *bad_return(void) {
    int local = 5;
    return &local;   // UNDEFINED BEHAVIOR: local is destroyed on return
}

int *good_return(void) {
    int *p = malloc(sizeof(int));
    *p = 5;
    return p;        // OK: heap memory persists after return
}
```

The first function causes undefined behavior because `local` no longer exists after the function returns. This is one of the most common C bugs beginners write.

## Interview Answer

> "The stack is fast, automatic, and scope-bound — allocated by moving the stack pointer — but limited in size. The heap is flexible and long-lived but requires explicit management and is slower to allocate. You use the stack for small temporaries and the heap for large or long-lived data."
