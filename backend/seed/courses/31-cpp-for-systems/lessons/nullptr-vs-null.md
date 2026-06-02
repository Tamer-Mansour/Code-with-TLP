# nullptr vs NULL vs 0: What Is the Difference?

All three can represent a "no pointer" value, but they differ in type safety, overload resolution, and clarity. In modern C++ (C++11 and later) `nullptr` is always the right choice.

## The Three Options

### `0` — The Historical Way

In C, `0` is the canonical null pointer constant. C++ inherited this. Any integer constant expression that evaluates to zero is implicitly convertible to any pointer type.

```cpp
int* p = 0;   // legal — 0 converts to null pointer
```

Problem: `0` is also a perfectly valid `int`. This causes overload-resolution ambiguity:

```cpp
void foo(int  n) { std::cout << "int\n"; }
void foo(int* p) { std::cout << "ptr\n"; }

foo(0);   // calls foo(int) — might not be what you intended
```

### `NULL` — The C Macro

`NULL` is defined in `<cstddef>` (and `<stddef.h>`). In C it is typically `((void*)0)`, but in C++ it is usually just `0` or `0L` because `void*` does not implicitly convert to typed pointers in C++.

```cpp
#include <cstddef>
int* p = NULL;   // equivalent to int* p = 0;
```

`NULL` has the same overload ambiguity as `0` and additionally — on some compilers — `NULL` expands to `0L` (a `long`), which can trigger unexpected warnings or ambiguities with `long` overloads.

### `nullptr` — The Modern Way (C++11)

`nullptr` is a keyword of type `std::nullptr_t`. It converts to any pointer type and to `bool` (`false`), but it does **not** convert to an integer type.

```cpp
int* p = nullptr;   // clear intent: null pointer
```

Overload resolution is now unambiguous:

```cpp
void foo(int  n) { std::cout << "int\n"; }
void foo(int* p) { std::cout << "ptr\n"; }

foo(nullptr);   // calls foo(int*) — correct and unambiguous
foo(0);         // calls foo(int) — may be a surprise
```

## Comparison Table

| Feature | `0` | `NULL` | `nullptr` |
|---------|-----|--------|-----------|
| Type | `int` | implementation-defined (usually `int` or `long`) | `std::nullptr_t` |
| Converts to pointer | yes (implicit) | yes (implicit) | yes |
| Converts to integer | yes | yes | **no** |
| Overload safe | no | no | yes |
| Available since | always | C89 / C++98 | C++11 |
| Recommended | no | no | yes |

## Null Pointer Checks

All three compare equal to a null pointer of any type:

```cpp
int* p = nullptr;

if (p == nullptr) { }   // explicit — preferred
if (p == NULL)    { }   // works but dated
if (p == 0)       { }   // works but confusing
if (!p)           { }   // idiomatic — pointer converts to bool
```

## `std::nullptr_t` in Templates

`nullptr_t` becomes important when writing generic code that must handle null pointers specially:

```cpp
#include <cstddef>

template <typename T>
void handle(T* ptr) { /* ... */ }

template <>
void handle(std::nullptr_t) {
    std::cout << "got null\n";
}
```

Without `nullptr_t`, you could not distinguish a `nullptr` argument from a zero integer in a template.

## Worked Example: Preventing a Common Bug

```cpp
// C-style API that returns NULL on failure
char* find(const char* haystack, char needle);

// Bad old code — passes 0 accidentally?
char* result = find("hello", 0);   // 0 is a valid char (NUL), not a null ptr

// With nullptr the intent is clear when the pointer overload exists
void process(char* data);
void process(std::nullptr_t);  // explicit "no data" path

process(nullptr);  // unambiguous
```

## Common Pitfalls

- **Comparing function return to `NULL` in C++ code** — works, but static analyzers may warn; prefer `nullptr`.
- **Passing `nullptr` where an integer is expected** — the compiler will reject this, which is the safety feature, not a bug.
- **`if (p = nullptr)`** — accidentally assigns instead of comparing; always use `==` for comparison.

> **Interview answer:** `0` and `NULL` are integer constants that implicitly convert to pointers, causing overload-resolution ambiguity. `nullptr` (C++11) has type `std::nullptr_t`, converts to any pointer but never to an integer, making overloads unambiguous. Always use `nullptr` in modern C++.
