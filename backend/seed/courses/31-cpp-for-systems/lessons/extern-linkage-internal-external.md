# Internal vs External Linkage and extern

**Linkage** determines whether a name declared in one translation unit can be referred to from a different translation unit. Getting linkage wrong causes either silent shadowing bugs or linker errors. Understanding it is essential for writing correct multi-file C++ programs.

## What Is Linkage?

Every name in a C++ program has one of three linkage categories:

| Linkage | Meaning |
|---|---|
| **External** | The name is visible to the linker; other TUs can reference it. |
| **Internal** | The name is visible only within its own translation unit. |
| **No linkage** | Local variables, function parameters, type names — not visible to the linker at all. |

## External Linkage (the Default)

By default, functions and non-`const` global variables defined at namespace scope have **external linkage**. The linker can match them across translation units.

```cpp
// config.cpp
int max_connections = 100;       // external linkage — visible to linker
void init_server() { /* ... */ } // external linkage
```

Any other TU that declares these names can refer to the same objects:

```cpp
// main.cpp
extern int max_connections;      // declaration — no new object
extern void init_server();       // declaration — no new function

int main() {
    init_server();
    return max_connections;
}
```

## Internal Linkage with `static` and Anonymous Namespaces

Use **internal linkage** to restrict a name to its own translation unit. This prevents naming collisions in large projects and makes helper functions invisible to the rest of the program.

### Method 1 — `static` at namespace scope

```cpp
// utils.cpp
static int helper_counter = 0;      // internal linkage
static void reset_counter() {       // internal linkage
    helper_counter = 0;
}
```

The `static` keyword at namespace scope means "this name is private to this translation unit." It will not clash with a `helper_counter` in another `.cpp` file.

### Method 2 — Anonymous namespaces (preferred in modern C++)

```cpp
// utils.cpp
namespace {
    int helper_counter = 0;         // internal linkage
    void reset_counter() {          // internal linkage
        helper_counter = 0;
    }
}
```

Anonymous namespaces are the idiomatic C++ way to get internal linkage. They work for types as well, which `static` cannot do for types at namespace scope.

## `const` Variables Have Internal Linkage by Default

In C++ (unlike C), a `const` global variable has **internal linkage** by default:

```cpp
// constants.h
const int BUFFER_SIZE = 4096;    // internal linkage in each TU that includes this
```

This is why it is safe to put `const` variables in headers — each TU gets its own copy with no ODR conflict. If you need a single shared `const` object, use `extern const`:

```cpp
// constants.h
extern const int SHARED_SIZE;    // declaration only

// constants.cpp
extern const int SHARED_SIZE = 4096;   // definition — one copy, external linkage
```

In C++17, `inline const` is the cleaner alternative:

```cpp
// constants.h
inline const int SHARED_SIZE = 4096;  // one definition, safe in a header
```

## The `extern` Keyword — Two Distinct Roles

`extern` is overloaded with two meanings:

### Role 1: Declare without defining (explicit external linkage)

```cpp
extern int g_counter;   // "g_counter is defined elsewhere"
```

This is a declaration. No storage is allocated. The linker resolves it to the definition in another TU.

### Role 2: `extern "C"` — suppress name mangling

```cpp
extern "C" {
    void c_callback(int event);   // use C linkage (no mangling)
}
```

Used at C/C++ boundaries. Without this, C++ mangles the function name and the linker cannot find the symbol exported by a C library.

## Worked Example — Shared Global Counter

```cpp
// counter.h
#pragma once
extern int g_count;   // declaration — tells every TU the variable exists

// counter.cpp
#include "counter.h"
int g_count = 0;      // definition — one copy, external linkage

// worker.cpp
#include "counter.h"
void do_work() { ++g_count; }   // modifies the shared counter

// main.cpp
#include "counter.h"
#include <iostream>
int main() {
    do_work();
    std::cout << g_count << "\n";  // prints 1
}
```

## Common Pitfalls

- **Defining a non-const global in a header** — every TU that includes it creates its own definition → "multiple definition" linker error.
- **Forgetting `extern` in the header** — `int g_count;` in a header is a **definition**, not a declaration. Including it in two TUs causes a linker error.
- **Expecting `static` inside a function to give internal linkage** — `static` inside a function means "static storage duration" (persists across calls), not "internal linkage". The two meanings of `static` are context-dependent.

> **Interview answer:** "External linkage means a name is visible across translation units; internal linkage means it is private to the current TU. Functions and non-const globals have external linkage by default. You can force internal linkage with `static` at namespace scope or an anonymous namespace. `extern` on a variable declaration means 'this is defined elsewhere' — it creates a declaration without a definition. `extern \"C\"` suppresses C++ name mangling for interoperability with C code."
