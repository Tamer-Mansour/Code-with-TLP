# When to Allocate on the Stack vs the Heap

Choosing where a variable lives is one of the first decisions you make as a systems programmer. The wrong choice either wastes performance or causes bugs. Here is a crisp decision framework.

## Decision Flowchart

```
Is the size known at compile time?
  NO  ──► Heap (std::vector, std::make_unique)
  YES ──►
        Is the size small (< ~16 KB rule of thumb)?
          NO  ──► Heap
          YES ──►
                Must the object outlive the current scope?
                  YES ──► Heap
                  NO  ──► Stack
```

## Stack — Prefer When:

- **Size is small and compile-time known.** Scalars, small structs, small fixed arrays.
- **Object lifetime matches the scope.** No need to share across threads or return from the function.
- **Performance is critical.** Stack allocation is free; no allocator overhead or fragmentation.
- **You want guaranteed destruction.** RAII types on the stack always call their destructor.

```cpp
// All stack — correct and fast
int x = 42;
Point p{1.0, 2.0};
std::array<int, 8> small_buf{};
```

## Heap — Prefer When:

- **Size is runtime-determined.**
- **Object must outlive its creating scope** (returned to caller, shared with another thread).
- **Object is large** (avoid blowing the stack).
- **Polymorphism via base-class pointer** (virtual dispatch requires a pointer/reference anyway).

```cpp
// Heap — necessary cases
std::vector<int> v(n);                    // n is runtime
auto widget = std::make_unique<Widget>(); // polymorphic, returned to caller
```

## The RAII Pattern — Best of Both Worlds

Store the *management object* on the stack and let it own heap memory. You get heap capacity with stack lifetime safety.

```cpp
void process(int n) {
    std::vector<double> data(n);    // data on heap, vector metadata on stack
    std::unique_ptr<File> f = open_file("log.txt");  // heap File, ptr on stack
    // Both are automatically released when process() returns or throws
}
```

## Performance Rules of Thumb

| Scenario | Recommendation |
|----------|---------------|
| Small, short-lived buffer (< 4 KB) | Stack |
| Buffer size known only at runtime | `std::vector` (heap) |
| Fixed-size buffer, performance-critical, size > stack budget | `std::make_unique<T[]>` |
| Lots of same-size objects in a hot loop | Pool allocator |
| Large tree/graph nodes | Heap with arena allocator |

## Pitfalls to Avoid

**Do not return a pointer to a stack variable:**

```cpp
int* bad() {
    int x = 5;
    return &x;  // x is gone after return
}
```

**Do not allocate huge arrays on the stack:**

```cpp
void risky() {
    int matrix[2048][2048]; // 16 MB — almost certain stack overflow
}
// Fix:
void safe() {
    auto matrix = std::make_unique<int[]>(2048 * 2048);
}
```

**Do not skip `delete` for raw heap allocations:**

```cpp
void leak() {
    int* p = new int(42);
    // no delete — memory leaked
}
// Fix: use std::make_unique<int>(42)
```

## Quick Reference Card

```
Small + short-lived + known size  =>  Stack
Large or runtime size             =>  Heap (vector / unique_ptr)
Shared across scopes/threads      =>  Heap (shared_ptr)
Performance-critical many objects =>  Pool / arena allocator
```

> **Interview answer:** Use the stack for small, scope-bound, compile-time-sized objects because allocation is free and destruction is automatic. Use the heap for large objects, runtime-sized objects, or anything that must outlive its creating scope. Wrap heap allocations in RAII types to avoid leaks.
