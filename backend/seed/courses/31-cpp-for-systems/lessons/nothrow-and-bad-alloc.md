# Allocation Failure: bad_alloc and nothrow new

## The Default Behavior

When `new` cannot satisfy an allocation request — because the system is out of memory, or the request is impossibly large — it throws `std::bad_alloc`. This exception propagates up the call stack until caught or, if uncaught, terminates the program via `std::terminate`.

```cpp
#include <new>
#include <iostream>

int main() {
    try {
        // Try to allocate several terabytes
        char* p = new char[1'000'000'000'000LL];
        delete[] p;
    } catch (const std::bad_alloc& e) {
        std::cerr << "Allocation failed: " << e.what() << "\n";
        // e.what() typically returns "std::bad_alloc"
    }
}
```

`std::bad_alloc` inherits from `std::exception`, so it is also caught by `catch (const std::exception&)`.

## The nothrow Variant

Sometimes throwing an exception is undesirable — for example in signal handlers, interrupt service routines, or performance-critical inner loops. The `std::nothrow` tag selects an overload of `operator new` that returns `nullptr` on failure instead of throwing:

```cpp
#include <new>

int* p = new (std::nothrow) int[1'000'000];
if (p == nullptr) {
    // handle allocation failure without exceptions
}
delete[] p;   // still uses ordinary delete[] — nothrow only affects allocation
```

The `nothrow` variant internally catches `bad_alloc` and converts it to a null return. It is slightly slower than checking the result of a throw (because exception infrastructure may still be involved), but it avoids the overhead of stack unwinding if failure is common.

## Comparison Table

| Behavior | `new T` | `new (std::nothrow) T` |
|----------|---------|------------------------|
| On failure | Throws `std::bad_alloc` | Returns `nullptr` |
| On success | Returns valid pointer | Returns valid pointer |
| Null check needed? | No (but catch needed) | Yes — always check |
| Use in signal handlers | Unsafe | Safer |
| Deallocation | `delete` | `delete` (same) |

## The new-handler

Before throwing `bad_alloc`, the runtime calls a user-installable callback called the **new-handler**. This lets you attempt recovery (e.g., release a cache) before the exception fires:

```cpp
#include <new>
#include <cstdlib>
#include <iostream>

void my_new_handler() {
    std::cerr << "Out of memory! Releasing emergency reserve.\n";
    // release some previously reserved memory, then return
    // if you cannot free anything, call std::set_new_handler(nullptr)
    // to restore the default (throw) behavior, then return.
    std::set_new_handler(nullptr);  // next allocation will throw
}

int main() {
    std::set_new_handler(my_new_handler);
    // Now all new-expressions will call my_new_handler before throwing
    try {
        char* p = new char[1'000'000'000'000LL];
        delete[] p;
    } catch (const std::bad_alloc&) {
        std::cerr << "Allocation ultimately failed.\n";
    }
}
```

If the new-handler returns without freeing enough memory and without changing the handler, `operator new` retries — leading to an infinite loop. Always either free memory, install a different handler, or call `std::set_new_handler(nullptr)`.

## Practical Guidance

- **Application code** — use the throwing form and catch `bad_alloc` at a recovery boundary (e.g., reject a request, log, continue serving). Do not check every single allocation.
- **Kernel / embedded code** — use `new (std::nothrow)` or a custom operator; exceptions may be disabled entirely (`-fno-exceptions`).
- **Library code** — document whether your library can throw `bad_alloc` and let the caller decide how to handle it.

```cpp
// Systems library pattern: explicit OOM handling
bool system_alloc(void** out, std::size_t n) {
    *out = new (std::nothrow) char[n];
    return *out != nullptr;
}
```

## Interview Answer

> **Q: What is the difference between `new` and `new (std::nothrow)` on allocation failure?**
>
> Standard `new` throws `std::bad_alloc` so you can handle it with a catch block anywhere up the call stack; `new (std::nothrow)` returns `nullptr` instead, which you must check immediately after the call — useful in signal handlers or environments where exceptions are disabled.
