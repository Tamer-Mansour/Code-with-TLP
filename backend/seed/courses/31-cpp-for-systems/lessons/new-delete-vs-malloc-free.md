# new/delete vs malloc/free: What Is the Difference?

## The Core Distinction

`malloc` and `free` are C library functions that allocate and release raw bytes. `new` and `delete` are C++ operators that additionally manage object lifetimes by invoking constructors and destructors. This difference is not cosmetic — it is architectural.

```cpp
#include <cstdlib>

struct Widget {
    int id;
    Widget() : id(42) {}    // constructor
    ~Widget() { id = -1; }  // destructor
};

// C way — constructor never called, id is garbage
Widget* w1 = (Widget*)malloc(sizeof(Widget));
free(w1);   // destructor never called

// C++ way — constructor + destructor both run
Widget* w2 = new Widget;
delete w2;
```

## Side-by-Side Comparison

| Feature | `malloc` / `free` | `new` / `delete` |
|---------|-------------------|------------------|
| Language | C (also usable in C++) | C++ only |
| Returns | `void*` — must cast | Correctly typed pointer |
| On failure | Returns `NULL` | Throws `std::bad_alloc` |
| Constructors | Not called | Called automatically |
| Destructors | Not called | Called automatically |
| Resizable | `realloc` available | No built-in equivalent |
| Overloadable | No | Yes (`operator new`) |
| Array form | `malloc(n * sizeof(T))` | `new T[n]` |

## Type Safety

`malloc` returns `void*`, which in C++ must be explicitly cast — a potential source of bugs:

```cpp
// Error-prone C style in C++
int* arr = (int*)malloc(10 * sizeof(int));  // manual sizeof, manual cast
if (!arr) { /* handle NULL */ }

// C++ style — type-safe, no cast, right size automatically
int* arr2 = new int[10];
```

Forgetting to update `sizeof` after changing a type is a classic C bug that `new` eliminates entirely.

## Failure Handling

The different failure modes require different handling strategies:

```cpp
#include <new>
#include <cstdlib>

// malloc — always check the return value
void* raw = malloc(1024);
if (!raw) {
    perror("malloc failed");
    return;
}

// new — catch the exception (or use nothrow variant)
try {
    int* p = new int[256];
    delete[] p;
} catch (const std::bad_alloc& e) {
    std::cerr << "new failed: " << e.what() << "\n";
}

// nothrow new — returns nullptr like malloc
int* p2 = new (std::nothrow) int[256];
if (!p2) { /* handle */ }
```

## Can You Mix Them?

No. You must never mix allocators:

```cpp
int* p = (int*)malloc(sizeof(int));
delete p;    // UNDEFINED BEHAVIOR — wrong deallocation function

int* q = new int;
free(q);     // UNDEFINED BEHAVIOR — wrong deallocation function
```

The internals of `operator new` and `malloc` may use different heap bookkeeping structures. Mixing them corrupts those structures silently or crashes at an unrelated point.

## When `malloc` Is Still Appropriate in C++

- Interfacing with C APIs that call `free` on memory you provide.
- Implementing custom allocators or memory pools that manage raw storage.
- Code that must be `realloc`-able (e.g., a growing buffer).

```cpp
// Growing buffer — realloc has no new/delete equivalent
char* buf = (char*)malloc(64);
buf = (char*)realloc(buf, 128);  // resize in-place if possible
free(buf);
```

## Worked Example: Placement New Bridges the Gap

When you need `malloc`-style raw control but C++ constructors, use placement new:

```cpp
void* mem = malloc(sizeof(Widget));
Widget* w = new (mem) Widget;   // construct in pre-allocated memory
w->~Widget();                   // explicit destructor call
free(mem);                      // free the raw memory
```

This pattern is common in allocator implementations and OS kernels.

## Interview Answer

> **Q: Can you use `free` to release memory allocated with `new`?**
>
> No. `new` and `delete` must be paired together, as must `malloc` and `free`. Mixing them is undefined behavior because they may use different internal bookkeeping structures and because `free` will never call the destructor.
