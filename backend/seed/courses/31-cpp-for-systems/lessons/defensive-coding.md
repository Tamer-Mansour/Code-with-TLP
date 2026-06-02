# Defensive Coding and Bounds Checking

Defensive coding means writing code that is correct under all valid inputs and that fails loudly — not silently — when invariants are violated. In systems programming this is not optional; bugs that corrupt memory silently are orders of magnitude harder to debug than bugs that crash immediately.

## Principle 1: Validate at the Boundary

Check inputs once, at the point they enter your system. Internal functions can then trust their preconditions.

```cpp
// BAD: spreads checks everywhere, easy to miss one
void internal_write(char* buf, size_t len, size_t offset, uint8_t val) {
    if (offset < len) buf[offset] = val;   // repeated everywhere
}

// GOOD: validate at the boundary, assert internally
void safe_write(char* buf, size_t len, size_t offset, uint8_t val) {
    assert(offset < len);   // catches programmer errors in debug
    buf[offset] = val;
}
```

## Principle 2: Prefer Bounds-Checked Containers

| Unsafe | Safe equivalent |
|---|---|
| `T arr[N]` | `std::array<T, N>` + `.at(i)` |
| `T*` + manual size | `std::vector<T>` + `.at(i)` |
| `char buf[N]` + `strcpy` | `std::string` |
| `span` raw pointer | `std::span<T>` (C++20) |

```cpp
std::vector<int> v = {10, 20, 30};
v.at(5);   // throws std::out_of_range — loud failure
v[5];      // UB — silent
```

Use `.at()` during development and testing; switch to `operator[]` only in proven-hot paths.

## Principle 3: Use Assertions for Invariants

`assert` is compiled out in release builds (`-DNDEBUG`). Use it for conditions that *must* be true if the program is correct, not for runtime error handling.

```cpp
#include <cassert>

int binary_search(const int* arr, int len, int target) {
    assert(arr != nullptr);
    assert(len >= 0);
    // ...
}
```

For conditions that must be checked in release builds, use explicit error handling:

```cpp
if (ptr == nullptr) {
    throw std::invalid_argument("ptr must not be null");
}
```

## Principle 4: Avoid Unbounded Operations

```cpp
// BAD
char name[32];
scanf("%s", name);        // no length limit

// GOOD
char name[32];
scanf("%31s", name);      // one less than buffer for null terminator

// BEST
std::string name;
std::cin >> name;         // no fixed limit, no overflow possible
```

## Principle 5: Integer Arithmetic Safety

Before computing a size or index, check for overflow:

```cpp
#include <stdint.h>
#include <limits.h>

// Safe addition: returns false on overflow
bool safe_add(size_t a, size_t b, size_t* result) {
    if (b > SIZE_MAX - a) return false;   // would overflow
    *result = a + b;
    return true;
}

// GCC/Clang built-in
size_t total;
if (__builtin_add_overflow(count, extra, &total)) {
    abort();   // or return error
}
```

## Principle 6: Initialize Everything

```cpp
// C++ style: value-initialize
int arr[16]{};           // all zeros
struct Point p{};        // all zeros

// Or use designated initializers (C++20)
Point q{.x = 1, .y = 2};
```

## Toolchain Hardening Flags

```bash
# Compile-time hardening
g++ -Wall -Wextra -Werror          \
    -fstack-protector-strong       \  # stack canaries
    -D_FORTIFY_SOURCE=2            \  # glibc bounds checking
    -pie -fPIE                     \  # position-independent (works with ASLR)
    -Wformat -Wformat-security     \  # format string checks
    prog.cpp -o prog
```

## Sanitizers in the Development Loop

```bash
# During development and CI
g++ -fsanitize=address,undefined -g -O1 prog.cpp -o prog_san
./prog_san

# Memory sanitizer (clang only, catches uninitialized reads)
clang++ -fsanitize=memory -g prog.cpp -o prog_msan
```

## Key Takeaway

> **Interview answer:** Defensive coding means validating inputs at boundaries, using bounds-checked containers like `std::vector::at()`, asserting invariants explicitly, avoiding unbounded functions like `strcpy`, and enabling compiler hardening flags and sanitizers. The goal is to make errors loud and local rather than silent and propagating.
