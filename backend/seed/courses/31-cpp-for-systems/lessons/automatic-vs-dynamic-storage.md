# Automatic, Static, and Dynamic Storage Duration

C++ classifies every variable by its *storage duration* — the rule that determines when memory is allocated and when it is released. There are four categories; three are critical for systems programming.

## Storage Duration Summary

| Duration | Keyword / Context | Allocation | Deallocation |
|----------|-------------------|------------|--------------|
| **Automatic** | Local variable inside a function | Function entry | Function exit (scope end) |
| **Static** | `static` or at namespace scope | Program start | Program end |
| **Dynamic** | `new` / `malloc` | Explicit call | Explicit `delete` / `free` |
| **Thread-local** | `thread_local` | Thread start | Thread exit |

## Automatic Storage Duration

The most common duration. The compiler reserves the memory on the stack frame; no runtime call is needed.

```cpp
void foo(int n) {
    int x = 10;           // automatic
    double arr[8] = {};   // automatic — size must be known at compile time (C++)
    // x and arr are destroyed here automatically
}
```

**Variable-length arrays (VLAs)** with runtime sizes are not standard C++. Use `std::vector` instead.

```cpp
void bar(int n) {
    // int vla[n];  // NOT standard C++ (GCC extension only)
    std::vector<int> v(n);  // correct C++: heap data, automatic vector object
}
```

## Static Storage Duration

Variables with static storage duration are allocated once at program startup (before `main`) and destroyed in reverse order at program exit (after `main` returns).

```cpp
int global = 42;              // static duration, Data segment

void counter() {
    static int calls = 0;    // static duration, initialized once
    ++calls;
    printf("called %d times\n", calls);
}
```

**Pitfall — static initialization order fiasco:** The order in which objects in *different* translation units are initialized is unspecified. If one global depends on another in a different `.cpp` file, you may read an uninitialized object.

```cpp
// file_a.cpp
int A = 10;

// file_b.cpp
extern int A;
int B = A * 2;  // A might not be initialized yet — undefined behaviour
```

The fix: wrap the dependency in a function with a local `static`:

```cpp
int& get_A() {
    static int A = 10;   // initialized on first call — safe
    return A;
}
```

## Dynamic Storage Duration

Objects created with `new` live until `delete` is called, regardless of scope.

```cpp
int* p = new int(99);
// p survives beyond any scope boundary
delete p;   // programmer is responsible
```

Dynamic allocation is essential when:
- The size is not known at compile time.
- The object must outlive the creating function.
- You need fine-grained control over object lifetime.

Modern C++ wraps dynamic allocations in smart pointers to restore deterministic destruction:

```cpp
#include <memory>

std::unique_ptr<int> p = std::make_unique<int>(99);
// automatically deleted when p goes out of scope
```

## Thread-Local Storage Duration

Each thread gets its own copy of the variable. Useful for per-thread caches, error codes, or random-number state.

```cpp
thread_local int thread_id = 0;   // separate instance per thread
```

## Interaction with Constructors and Destructors

Storage duration directly controls when constructors and destructors run:

```cpp
struct Log {
    Log()  { puts("Log created");  }
    ~Log() { puts("Log destroyed"); }
};

Log g;           // static: ctor before main, dtor after main
void f() {
    Log local;   // automatic: ctor on entry, dtor on exit
    Log* d = new Log;   // dynamic: ctor now, dtor on delete
    delete d;
}
```

> **Interview answer:** Automatic storage is stack-based and scope-bound; static storage lasts the entire program and is initialized before `main`; dynamic storage lives on the heap and must be manually managed (or wrapped in a smart pointer).
