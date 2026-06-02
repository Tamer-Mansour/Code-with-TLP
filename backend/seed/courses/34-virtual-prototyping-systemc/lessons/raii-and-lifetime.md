# RAII and Object Lifetime

**RAII** stands for *Resource Acquisition Is Initialisation*. It is arguably the most important C++ idiom, and it underpins how SystemC manages the lifetime of modules, channels, and processes without a garbage collector.

## The Core Idea

Tie the lifetime of a resource (memory, file handle, mutex lock, simulation object) to the lifetime of a C++ object:

- **Acquire** the resource in the constructor.
- **Release** the resource in the destructor.
- The language guarantees the destructor runs when the object goes out of scope — even if an exception is thrown.

```cpp
class FileGuard {
    FILE* fp;
public:
    FileGuard(const char* path) {
        fp = fopen(path, "r");
        if (!fp) throw std::runtime_error("open failed");
    }
    ~FileGuard() {
        if (fp) fclose(fp);   // always runs
    }
    FILE* get() { return fp; }
};

void readLog() {
    FileGuard f("sim.log");   // file opened
    // ... use f.get() ...
}   // destructor runs here — file closed, even if exception thrown
```

## Object Lifetime in C++

An object's lifetime begins when its constructor finishes and ends when its destructor starts.

| Storage class | Lifetime |
|---------------|----------|
| Local (stack) | Start of enclosing block to end of block |
| `static` local | First call through the declaration to program end |
| Heap (`new`) | `new` expression to matching `delete` |
| Member | Same as the containing object |

The destructor order is the **reverse** of construction order — members are destroyed last-in-first-out, and base-class destructors run after derived-class destructors.

## Smart Pointers as RAII

Standard smart pointers are the most common RAII wrappers in modern C++:

```cpp
#include <memory>

{
    auto ptr = std::make_unique<int[]>(1024);   // heap allocation
    ptr[0] = 42;
    // ... work ...
}   // unique_ptr destructor: delete[] runs automatically
```

`std::lock_guard` applies the same pattern to mutexes:

```cpp
std::mutex mtx;

void criticalSection() {
    std::lock_guard<std::mutex> lock(mtx);   // mutex locked
    // ... protected work ...
}   // lock_guard destructor: mutex unlocked
```

## SystemC Module Lifetime

In SystemC, elaboration constructs the module hierarchy. The simulator calls constructors top-down. The destructors run when `sc_stop()` is called and the `sc_core` infrastructure unwinds.

```cpp
SC_MODULE(Dut) {
    sc_in<bool>   clk;
    sc_out<int>   out;

    int* scratchpad;

    SC_CTOR(Dut) {
        scratchpad = new int[128];   // acquire
        SC_THREAD(run);
    }

    ~Dut() {
        delete[] scratchpad;         // release
    }

    void run() { /* ... */ }
};
```

With RAII (preferred):

```cpp
SC_MODULE(Dut) {
    sc_in<bool>  clk;
    sc_out<int>  out;

    std::unique_ptr<int[]> scratchpad;

    SC_CTOR(Dut)
        : scratchpad(std::make_unique<int[]>(128))
    {
        SC_THREAD(run);
    }
    // No destructor needed

    void run() { /* ... */ }
};
```

## Exception Safety and RAII

Without RAII, an early return or exception leaves resources dangling:

```cpp
// BAD — leak if exception thrown between new and delete
int* buf = new int[N];
process(buf);   // throws?
delete[] buf;   // may never run
```

With RAII, every exit path is safe:

```cpp
// GOOD — unique_ptr destructor always runs
auto buf = std::make_unique<int[]>(N);
process(buf.get());
```

## Common Pitfalls

- **Returning a local by reference** — the local is destroyed at function exit, the reference dangles immediately.
- **Circular `shared_ptr` ownership** — two objects holding `shared_ptr` to each other form a cycle; neither destructor runs. Break cycles with `std::weak_ptr`.
- **Copying a `unique_ptr`** — `unique_ptr` is move-only; accidentally copying it is a compile error (a feature, not a bug).
- **Using an object after `std::move`** — after a move, the source is in a valid but unspecified state; reading it is typically wrong.

## RAII Checklist for SystemC Models

1. Prefer member-variable sub-modules over heap-allocated modules when possible (avoids manual `delete`).
2. When heap allocation is needed, wrap in `unique_ptr` and initialise in the member-initialiser list.
3. Any resource opened in `start_of_simulation()` should be closed in `end_of_simulation()` — these are virtual hooks in `sc_module` designed exactly for this pattern.

> **Interview answer:** RAII binds resource lifetime to object lifetime so that resources are automatically released when a destructor runs, regardless of how the enclosing scope is exited. In SystemC it means wrapping heap-allocated sub-modules in `unique_ptr` so that the module hierarchy teardown at `sc_stop()` never leaks memory, even if the simulation terminates abnormally.
