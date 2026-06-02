# Constructors and Destructors as Resource Bookends

One of C++'s most powerful idioms does not have a flashy algorithm or a clever data structure behind it. It is simply this: **acquire a resource in a constructor, release it in the destructor**. This pattern is called **RAII** — Resource Acquisition Is Initialization.

## The Core Idea

A resource is anything that must be explicitly acquired and released: heap memory, file descriptors, mutex locks, network sockets, GPU command buffers, database connections.

Without RAII, manual resource management is error-prone:

```cpp
// Manual management — fragile
void process(const char* path) {
    FILE* f = fopen(path, "r");
    if (!f) return;

    // ... many lines of code ...
    if (some_error) {
        fclose(f);   // easy to forget
        return;
    }

    fclose(f);   // must remember every exit path
}
```

With RAII, the destructor handles every exit path — including exceptions:

```cpp
class File {
    FILE* fp;
public:
    explicit File(const char* path, const char* mode)
        : fp(fopen(path, mode)) {
        if (!fp) throw std::runtime_error("cannot open file");
    }

    ~File() { if (fp) fclose(fp); }   // always runs

    FILE* get() const { return fp; }

    // Non-copyable, movable
    File(const File&)            = delete;
    File& operator=(const File&) = delete;
};

void process(const char* path) {
    File f(path, "r");
    // ... use f.get() ...
    // ~File() called automatically: scope exit, return, or exception
}
```

## Why It Works: Guaranteed Destruction

The C++ standard guarantees that a fully-constructed object's destructor **will** run when its lifetime ends, regardless of how — normal return, early return, or exception propagation. This guarantee makes the constructor and destructor pair a reliable resource bracket.

```
{ // <-- constructor: acquire
    File f("data.txt", "r");
    parse(f.get());        // may throw
} // <-- destructor: release — even if parse() threw
```

## Standard Library RAII Wrappers

The standard library is built on this idiom:

| Wrapper | Resource managed |
|---|---|
| `std::unique_ptr<T>` | Heap-allocated object (sole owner) |
| `std::shared_ptr<T>` | Heap-allocated object (shared ownership) |
| `std::lock_guard<M>` | Mutex lock |
| `std::unique_lock<M>` | Mutex lock (flexible) |
| `std::fstream` | File stream |
| `std::vector<T>` | Dynamic array memory |

You rarely need to write raw `new`/`delete` in modern C++.

## A Worked Example: Scoped Timer

```cpp
#include <chrono>
#include <iostream>
#include <string>

class ScopedTimer {
    using Clock = std::chrono::steady_clock;
    std::string label;
    Clock::time_point start;
public:
    explicit ScopedTimer(std::string lbl)
        : label(std::move(lbl)), start(Clock::now()) {}

    ~ScopedTimer() {
        auto elapsed = Clock::now() - start;
        auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(elapsed).count();
        std::cout << label << ": " << ms << " ms\n";
    }
};

void expensive_operation() {
    ScopedTimer t("expensive_operation");
    // ... work ...
}   // prints elapsed time automatically
```

## Exception Safety and RAII

RAII is the foundation of exception-safe code. When an exception propagates through a scope, the C++ runtime destroys all fully-constructed objects in that scope in reverse order. Each destructor releases its resource cleanly.

```cpp
void risky() {
    std::lock_guard<std::mutex> lock(g_mutex);  // mutex acquired
    std::unique_ptr<Obj> p = std::make_unique<Obj>();  // heap acquired

    might_throw();  // if this throws...
    // ...both lock and p are released automatically
}
```

Without RAII, an exception anywhere before `unlock()` or `delete` would leak resources.

## Pitfalls

- **Two-phase initialization:** constructors that leave the object in an invalid state and require a separate `init()` call break the RAII guarantee. Prefer throwing an exception from the constructor if the resource cannot be acquired.
- **Naked `new`/`delete`:** every raw `new` creates a potential resource leak. Wrap in `std::unique_ptr` at the point of allocation.
- **Partially-constructed objects:** if a constructor throws, the destructor does **not** run for that object — but the destructors of already-constructed members and base classes do. Design constructors so that all resources are held by member RAII objects, not naked pointers.

## The Bookend Mental Model

```
Constructor ──────────────────── Destructor
    |                                |
    open(file)               close(file)
    lock(mutex)              unlock(mutex)
    new int[n]               delete[] ptr
    connect(socket)          disconnect(socket)
```

Every resource acquired in the constructor has its paired release in the destructor. The C++ lifetime rules enforce that the destructor runs, so the release is guaranteed.

> **Interview answer:** RAII pairs resource acquisition with object construction and resource release with destruction. Because C++ guarantees that a fully-constructed object's destructor runs when its scope ends — including on exception — this idiom makes resource management automatic and exception-safe without any additional bookkeeping.
