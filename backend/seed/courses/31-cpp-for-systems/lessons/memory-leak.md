# What Is a Memory Leak and How to Find One

## Definition

A memory leak occurs when a program allocates heap memory and then loses all reachable pointers to it without ever freeing it. The memory remains reserved for the process's lifetime — or until the OS reclaims it at process exit — even though the program can never use it again.

```cpp
void leaky_function() {
    int* p = new int[1000];
    // p goes out of scope — memory is never deleted
}   // 4000 bytes leaked every call
```

Calling `leaky_function()` in a loop will grow the process's resident set until it is killed or the system runs out of memory.

## Why Leaks Matter in Systems Programming

- **Long-running servers and daemons** — a 1 KB/s leak in a server process means gigabytes of waste within hours.
- **Embedded and real-time systems** — fixed RAM, no virtual memory; a leak is fatal.
- **OS kernels and drivers** — the kernel heap is shared by every process; a kernel leak can take down the whole machine.

## Common Leak Patterns

### Early Return Without Cleanup

```cpp
bool process(const char* filename) {
    char* buf = new char[4096];
    if (!open_file(filename)) {
        return false;   // BUG: buf never deleted on this path
    }
    // ... use buf ...
    delete[] buf;
    return true;
}
```

### Exception Escaping Before `delete`

```cpp
void risky() {
    Resource* r = new Resource();
    r->might_throw();   // if this throws, r is leaked
    delete r;
}
```

Fix both patterns with RAII — wrap the pointer in a `std::unique_ptr`:

```cpp
#include <memory>
void safe() {
    auto r = std::make_unique<Resource>();
    r->might_throw();   // exception unwinds; destructor deletes automatically
}
```

### Overwriting a Pointer Before Deleting

```cpp
int* p = new int(1);
p = new int(2);   // original allocation leaked — no pointer left to delete it
delete p;
```

## Finding Leaks: Tooling

### Valgrind (Linux / macOS)

```bash
g++ -g leak_example.cpp -o leak_example
valgrind --leak-check=full --show-leak-kinds=all ./leak_example
```

Output (excerpted):
```
==12345== 4,000 bytes in 1 blocks are definitely lost in loss record 1 of 1
==12345==    at 0x...: operator new[](unsigned long)
==12345==    at 0x...: leaky_function() (leak_example.cpp:3)
```

### AddressSanitizer (GCC / Clang)

```bash
g++ -fsanitize=address -g leak_example.cpp -o leak_example
ASAN_OPTIONS=detect_leaks=1 ./leak_example
```

### Static Analysis

```bash
clang --analyze leak_example.cpp   # Clang Static Analyzer
# or use clang-tidy, cppcheck, PVS-Studio
```

## Leak vs. Lost Pointer: Severity Levels

| Valgrind category | Meaning |
|-------------------|---------|
| Definitely lost | No pointer reachable; true leak |
| Indirectly lost | Reachable only through another leaked block |
| Still reachable | Pointer exists at exit — not a leak per se |
| Possibly lost | Interior pointer (could be real or not) |

## Worked Example: Tracking Allocations

```cpp
#include <cstdlib>
#include <cstdio>

static long g_alloc_count = 0;

void* operator new(std::size_t n) {
    ++g_alloc_count;
    return std::malloc(n);
}
void operator delete(void* p) noexcept {
    --g_alloc_count;
    std::free(p);
}

int main() {
    int* a = new int(1);
    int* b = new int(2);
    delete a;
    // b is leaked
    std::printf("Net allocations at exit: %ld\n", g_alloc_count); // prints 1
}
```

## Interview Answer

> **Q: How would you find a memory leak in a C++ program?**
>
> Run the program under Valgrind (`--leak-check=full`) or compile with AddressSanitizer (`-fsanitize=address`) to get a stack trace pointing to the allocation site; then fix the ownership by using RAII wrappers like `std::unique_ptr` instead of raw `new`/`delete`.
