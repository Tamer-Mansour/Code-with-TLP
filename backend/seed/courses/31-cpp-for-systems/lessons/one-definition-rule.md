# The One Definition Rule and Why Linkers Complain

The **One Definition Rule (ODR)** is one of C++'s most important — and most quietly violated — rules. It dictates how many times any entity may be defined across a program. Violating it produces either a linker error or, worse, **silent undefined behavior** that is nearly impossible to debug.

## The Rule in Plain English

The ODR has two parts:

1. **Within a single translation unit:** every variable, function, class, enum, or template may be defined at most once.
2. **Across all translation units in a program:** every non-inline function and non-inline variable may be defined in at most one TU. Classes, inline functions, and templates may be defined in multiple TUs, but all definitions must be **identical** (token for token).

```cpp
// file1.cpp
int compute(int x) { return x * 2; }   // definition #1

// file2.cpp
int compute(int x) { return x * 2; }   // definition #2 → ODR violation
```

The linker sees two definitions of `compute` with external linkage and refuses to link (or silently picks one — behavior is undefined).

## What Triggers a Linker "multiple definition" Error?

The most common cause: placing a **non-inline function definition** in a header and including it in more than one `.cpp` file.

```cpp
// utils.h — WRONG
int add(int a, int b) { return a + b; }   // full definition, not inline
```

```cpp
// main.cpp
#include "utils.h"   // add defined here

// server.cpp
#include "utils.h"   // add defined here again → linker error
```

```
/usr/bin/ld: server.o: multiple definition of 'add(int, int)'
```

**Fix:** mark it `inline`, or move the definition to a `.cpp` file.

```cpp
// utils.h — CORRECT
inline int add(int a, int b) { return a + b; }
```

## The Silent ODR Violation

The ODR also forbids having two **different** definitions of the same class across TUs — even if neither produces a linker error. This happens when:

- A header is included in two TUs but one TU has a `#define` that changes the class layout.
- The same class name is defined differently in two `.cpp` files (rare but catastrophic).

```cpp
// version A (in one TU due to a macro)
struct Config {
    int debug;
    int level;
};

// version B (in another TU)
struct Config {
    int level;
    int debug;   // fields swapped!
};
```

Both TUs link fine because the symbol names match, but passing a `Config` across the boundary produces wrong field reads — a silent, data-corrupting bug.

## ODR and Class Definitions in Headers

The ODR explicitly **permits** class definitions to appear in multiple TUs, provided all copies are identical. This is why classes can (and must) be defined in headers:

```cpp
// point.h
#pragma once

struct Point {    // same definition in every TU that includes this
    int x, y;
};
```

If the include guard is absent and the header is included twice in one TU, the compiler will catch the redefinition within that TU.

## ODR and Templates

Template definitions must appear in every TU that instantiates them, so they live in headers. The ODR allows this: as long as all instantiations of the same template with the same arguments are identical, the rule is satisfied.

## Rules Summary Table

| Entity | One definition per TU? | One definition per program? |
|---|---|---|
| Non-inline function | Yes | Yes |
| `inline` function | Yes | No (all must be identical) |
| Variable with external linkage | Yes | Yes |
| `inline` variable (C++17) | Yes | No (all must be identical) |
| Class / struct | Yes (in one TU) | No (all must be identical) |
| Template | Yes (in one TU) | No (all instantiations must be identical) |

## Diagnosing ODR Violations

- **Linker error "multiple definition of"** → a definition appears in more than one `.o` file. Check for non-inline definitions in headers.
- **No linker error but wrong behavior** → two different definitions silently coexist. Use address sanitizer or LTO (link-time optimization) — modern compilers with `-flto` can detect some silent ODR violations.

```bash
g++ -std=c++17 -O2 -flto main.cpp server.cpp -o program
```

> **Interview answer:** "The ODR says every non-inline function and variable must be defined exactly once across the whole program. Classes and inline functions can be defined in multiple TUs but all copies must be identical. Violations either produce linker 'multiple definition' errors or, for inconsistent class layouts, silent undefined behavior that corrupts data at runtime."
