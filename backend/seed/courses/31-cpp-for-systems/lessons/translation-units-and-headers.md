# Translation Units, Headers, and Include Guards

The C++ compiler never sees your whole project at once. It processes one **translation unit** at a time, and the linker assembles the pieces later. Understanding this model explains why headers exist, why you must guard them, and why some errors only appear at link time.

## What Is a Translation Unit?

A **translation unit (TU)** is the unit of compilation: a single `.cpp` file after the preprocessor has run — meaning all `#include`d headers have been pasted in and all macros expanded.

```
main.cpp   ──►  preprocessor  ──►  translation unit  ──►  main.o
util.cpp   ──►  preprocessor  ──►  translation unit  ──►  util.o
```

Each TU is compiled independently. The compiler does not look at `util.cpp` while compiling `main.cpp`. Any name used in `main.cpp` must be **declared** in that TU — either directly or via an included header.

## Why Headers Exist

Headers are a mechanism to share **declarations** across multiple TUs without duplicating code. A header typically contains:

- Function declarations (prototypes).
- Class definitions.
- Inline function bodies.
- Template definitions.
- Constants and type aliases.

```cpp
// math_utils.h  — declarations only
#pragma once

int add(int a, int b);
double square(double x);
```

```cpp
// math_utils.cpp — definitions
#include "math_utils.h"

int add(int a, int b) { return a + b; }
double square(double x) { return x * x; }
```

```cpp
// main.cpp — uses the declarations
#include "math_utils.h"
#include <iostream>

int main() {
    std::cout << add(3, 4) << "\n";
}
```

The compiler trusts the declaration in the header. The linker later finds the actual definition in `math_utils.o`.

## The Double-Include Problem

Because `#include` is pure text substitution, including the same header twice in the same TU pastes its content twice. For a class definition, this violates the One Definition Rule and causes a compile error:

```cpp
// Dangerous — if two different headers both include "types.h"
#include "types.h"
#include "types.h"   // paste again → redefinition error
```

## Include Guards

The traditional solution is an **include guard** — a macro that prevents re-inclusion:

```cpp
// types.h
#ifndef TYPES_H
#define TYPES_H

struct Point { int x; int y; };

#endif // TYPES_H
```

On the first inclusion, `TYPES_H` is not defined, so the body is processed and the macro is set. On any subsequent inclusion in the same TU, the preprocessor skips the body entirely.

**Naming convention:** the guard macro should be unique across the entire project. Common patterns:

- `PROJECTNAME_FILENAME_H`
- `MYLIBRARY_MATH_UTILS_H`

## `#pragma once` — The Modern Alternative

Most modern compilers support `#pragma once` as a non-standard but universally supported alternative:

```cpp
#pragma once

struct Point { int x; int y; };
```

It tells the compiler to include this file at most once per TU, using the file's identity rather than a macro. It is shorter, avoids macro name collisions, and cannot be accidentally broken by `#undef`. The only downside is that it is not part of the ISO C++ standard (though all major compilers — GCC, Clang, MSVC — support it).

| Approach | Standard? | Collision-safe? | Risk |
|---|---|---|---|
| `#ifndef` guard | Yes | Only if name is unique | Guard macro can be `#undef`'d |
| `#pragma once` | No (but universal) | Yes | Rare issues with symlinked files |

## What Should NOT Be in a Header

Placing **definitions** (not just declarations) of non-inline, non-template functions in a header causes multiple-definition linker errors when the header is included in more than one TU:

```cpp
// BAD: function definition in a header
// utils.h
int multiply(int a, int b) { return a * b; }  // ← do NOT do this
```

If included in both `main.cpp` and `server.cpp`, the linker sees two definitions of `multiply` and refuses to link.

**Exceptions — definitions are fine in headers when:**
- The function is marked `inline`.
- It is a template function or class template.
- It is a `constexpr` function.

## Common Pitfall

Circular includes: `a.h` includes `b.h` and `b.h` includes `a.h`. Include guards prevent infinite recursion, but the types may still be incomplete when needed. The fix is to use **forward declarations** instead of full includes wherever only a pointer or reference to a type is needed.

```cpp
// Forward declaration — no need to include "Foo.h"
class Foo;

void process(Foo* f);   // pointer is fine with a forward decl
```

> **Interview answer:** "A translation unit is one `.cpp` file after preprocessing. Headers share declarations across TUs. Include guards (`#ifndef`/`#pragma once`) prevent the same header from being pasted twice into the same TU, which would cause redefinition errors. Definitions of non-inline functions should live in `.cpp` files, not headers, to avoid multiple-definition linker errors."
