# C vs C++: What Are the Differences?

C and C++ are siblings, not clones. Nearly every valid C program can be compiled as C++ with minor changes, but the two languages have diverged significantly in design philosophy, type system strictness, and supported idioms. Knowing where they differ is essential for systems work — most OS kernels are written in C, while most high-performance user-space applications are written in C++.

## Historical Relationship

C was created by Dennis Ritchie around 1972 and standardized as C89, C99, C11, and C17. C++ started as a preprocessor layer on top of C and remains backward-compatible at the ABI level in most cases. The two standards bodies are separate; they cooperate, but features added to one do not automatically appear in the other.

## Key Differences at a Glance

| Feature | C | C++ |
|---|---|---|
| Object-oriented programming | Not supported | Classes, inheritance, polymorphism |
| Templates / generics | Macros only | Full template system |
| Function overloading | No | Yes |
| References | No (pointers only) | Yes (`int& r = x;`) |
| Default arguments | No | Yes |
| Namespaces | No | Yes |
| RAII / destructors | Manual | Automatic via destructors |
| `bool` type | `_Bool` (C99) / `stdbool.h` | Built-in `bool` |
| `void*` implicit cast | Allowed | Requires explicit cast |
| `struct` tag usage | Requires `struct Foo` | `Foo` alone is sufficient |

## The `void*` Cast — A Real Compatibility Trap

In C, `malloc` returns `void*` which implicitly converts to any pointer type:

```c
/* Valid C, but NOT valid C++ */
int *p = malloc(sizeof(int) * 10);
```

In C++ you must cast:

```cpp
// Valid C++
int *p = static_cast<int*>(malloc(sizeof(int) * 10));
// Or better, use new:
int *p = new int[10];
```

This one difference causes subtle bugs when C headers are included in C++ translation units without an `extern "C"` guard.

## Name Mangling

C++ supports function overloading, so the linker must distinguish `void print(int)` from `void print(double)`. It does this through **name mangling** — encoding the parameter types into the symbol name. C does not mangle names.

```cpp
void print(int x);    // mangled to something like _Z5printi
void print(double x); // mangled to something like _Z5printd
```

When calling C functions from C++, you must suppress mangling with `extern "C"`:

```cpp
extern "C" {
    #include <some_c_library.h>
}
```

Without this, the linker looks for a mangled symbol that the C library never exported, producing an "undefined reference" error.

## RAII: The Fundamental Philosophical Gap

In C, resources (memory, file handles, locks) must be released manually. A missed `free()` or `fclose()` is a bug. C++ addresses this through **Resource Acquisition Is Initialization (RAII)**: resources are tied to object lifetimes, and destructors run automatically when objects go out of scope.

```cpp
{
    std::ifstream file("data.txt"); // file opened here
    // ... use file ...
}  // destructor runs here — file closed automatically
```

This pattern eliminates entire categories of resource leaks without relying on garbage collection.

## Common Pitfalls

- **Including C headers without `extern "C"`** causes linker errors due to name mangling.
- **Using C-style casts `(int*)p`** instead of `static_cast` hides errors the compiler would otherwise catch.
- **Mixing `new`/`delete` with `malloc`/`free`** is undefined behavior — always pair them correctly.
- **Ignoring the stricter C++ type system** — implicit conversions that compile in C may fail or warn in C++.

## When to Choose C vs C++

Use **C** when:
- Targeting a compiler that only supports C (some microcontrollers).
- Writing code that must be callable from many languages without a C++ ABI.
- Contributing to projects that have a strict C-only policy (Linux kernel).

Use **C++** when:
- You want RAII, templates, or object-oriented design.
- The codebase is already in C++ (e.g., LLVM, Chrome, game engines).

> **Interview answer:** "C++ is a strict superset of C that adds classes, templates, references, function overloading, and RAII. The key practical differences are name mangling (requiring `extern "C"` at C/C++ boundaries), the absence of implicit `void*` casts, and C++'s RAII model that ties resource lifetimes to object scope instead of requiring manual cleanup."
