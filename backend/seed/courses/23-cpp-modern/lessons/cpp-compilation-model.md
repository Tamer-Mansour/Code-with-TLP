# The C++ Compilation Model

Understanding how the C++ toolchain turns source code into a running program is essential for debugging linker errors, managing build times, and writing correct multi-file projects.

## Translation Units

Every `.cpp` file is compiled independently into an **object file** (`.o` / `.obj`). This unit of compilation is called a **translation unit**. Header files (`.h` / `.hpp`) are textually pasted by the preprocessor — they are not compiled on their own.

```
main.cpp  ──► preprocessor ──► compiler ──► main.o ─┐
utils.cpp ──► preprocessor ──► compiler ──► utils.o ─┴──► linker ──► program
```

## The One Definition Rule (ODR)

The ODR states:
- Every entity must be **defined exactly once** across all translation units.
- It may be **declared** any number of times (that's what headers are for).

```cpp
// math.h  — declaration only
#pragma once
int add(int a, int b);   // OK to include in many .cpp files

// math.cpp — one definition
int add(int a, int b) { return a + b; }
```

Violating the ODR — for example, defining `add` in two different `.cpp` files — produces a linker error about duplicate symbols.

## Header Guards and `#pragma once`

Without a guard, including a header twice in the same translation unit causes redefinition errors. Two equivalent solutions:

```cpp
// Traditional guard
#ifndef MY_HEADER_H
#define MY_HEADER_H
// ... contents ...
#endif

// Modern shorthand (non-standard but universally supported)
#pragma once
// ... contents ...
```

Prefer `#pragma once` in new code — it is shorter and avoids naming collisions.

## Inline Functions and Templates

Functions defined in headers must be marked `inline` (or be templates) to avoid ODR violations when the header is included in multiple translation units:

```cpp
// header.h
#pragma once
inline int square(int x) { return x * x; }   // OK in headers
template<typename T>
T cube(T x) { return x * x * x; }            // templates are implicitly inline
```

## Compilation Flags That Matter

| Flag | Effect |
|------|--------|
| `-std=c++20` | Enable C++20 features |
| `-O2` / `-O3` | Optimization level |
| `-Wall -Wextra` | Enable most warnings |
| `-g` | Include debug info |
| `-c` | Compile only, do not link |
| `-I<dir>` | Add include search path |
| `-L<dir>` | Add library search path |
| `-l<name>` | Link against `lib<name>` |

## Linking

The linker resolves symbols across object files:

```bash
g++ -std=c++20 -O2 -c main.cpp   -o main.o
g++ -std=c++20 -O2 -c utils.cpp  -o utils.o
g++            main.o utils.o    -o program
```

Or in one step:

```bash
g++ -std=c++20 -O2 main.cpp utils.cpp -o program
```

## C++20 Modules (Preview)

Modules replace the textual-inclusion model with proper semantic imports:

```cpp
// math.ixx (module interface unit)
export module math;
export int add(int a, int b) { return a + b; }

// main.cpp
import math;
int main() { return add(1, 2); }
```

Modules dramatically reduce compile times by eliminating redundant header re-parsing. Compiler support (GCC 11+, Clang 16+, MSVC 2019+) is good but CMake integration is still maturing.

## Key Takeaways

- Source files become translation units; headers are copy-pasted by the preprocessor.
- The ODR forbids multiple definitions of the same symbol in a program.
- Use `#pragma once` on every header to prevent double-inclusion.
- Template and `inline` function definitions belong in headers.
- Modules are the future but headers remain the safe default for now.
