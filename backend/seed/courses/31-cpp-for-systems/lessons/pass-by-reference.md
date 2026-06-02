# Pass by Reference and const Reference

Passing by reference gives a function direct access to the caller's object — no copy, no null-check boilerplate, and no dereference syntax. Adding `const` to the reference is the standard way to accept a large object efficiently while promising not to modify it.

## Plain (Non-const) Reference

A non-const reference parameter signals: "I will read *and* modify the caller's object."

```cpp
void triple(int& n) {
    n *= 3;   // modifies caller's variable
}

int main() {
    int x = 4;
    triple(x);
    std::cout << x;  // 12
}
```

The call site `triple(x)` looks identical to a pass-by-value call. This lack of visible `&` at the call site is why some style guides prefer pointers for output parameters — but within a codebase with consistent conventions, references are idiomatic.

## const Reference

A `const T&` parameter says: "I need access to the object without copying it, but I will not change it."

```cpp
void printLength(const std::string& s) {
    std::cout << s.size() << "\n";
    // s += "x";  // compile error — const reference
}
```

Benefits:
- **Zero copy** — no heap allocation for strings, no element duplication for vectors.
- **Compiler-enforced immutability** — accidental modification is a compile error.
- **Accepts temporaries** — unlike a non-const reference, a `const T&` binds to rvalues.

```cpp
printLength("hello");              // temporary std::string — OK with const&
printLength(std::string("world")); // also OK
```

## When to Use Each Form

| Parameter form | Use when |
|---|---|
| `T` (by value) | Cheap to copy (scalar, small POD) or function is a sink |
| `T&` (mutable reference) | Function must modify caller's object; always provided |
| `const T&` (const reference) | Large/expensive object; read-only access; always provided |
| `T*` (pointer) | Optional (nullable) argument; pointer arithmetic; C interop |
| `const T*` (const pointer) | Same as above but read-only |

## Worked Example: Accumulate Into a Result

```cpp
#include <vector>
#include <numeric>
#include <iostream>

// const ref for input (no copy of the vector)
// non-const ref for output (writes the result back to caller)
void sumVector(const std::vector<int>& v, long long& total) {
    total = std::accumulate(v.begin(), v.end(), 0LL);
}

int main() {
    std::vector<int> data = {1, 2, 3, 4, 5};
    long long result = 0;
    sumVector(data, result);
    std::cout << result;  // 15
}
```

## const Reference and Temporaries

A const reference can extend the lifetime of a temporary (see the dedicated lesson), which makes it useful for accepting both lvalues and rvalues in a single overload:

```cpp
void log(const std::string& msg) {
    std::cout << "[LOG] " << msg << "\n";
}

log("system started");         // temporary — bound to const&
std::string s = "connected";
log(s);                        // lvalue — also fine
```

## Common Pitfalls

- **Returning a non-const reference to a local.** The local is destroyed; the caller holds a dangling reference — undefined behavior.
- **Modifying through a const reference.** Impossible by design — the compiler prevents it. If you accidentally strip const with a cast, you have undefined behavior.
- **Non-const reference won't bind to a temporary.** This is a feature: it stops you from losing the modification silently.

```cpp
void inc(int& n) { n++; }
inc(5);   // error: 5 is not an lvalue
```

- **Over-using const ref for small types.** `const int&` is worse than `int` — it forces a memory indirection for no benefit.

## Key Rule

> For large objects: prefer `const T&` for read-only, `T&` for in-out. For cheap types: prefer `T` by value.

> **Interview answer:** A const reference avoids copying a large object while guaranteeing the function will not modify it. A non-const reference is used when the function must write to the caller's variable. Both are guaranteed non-null, unlike pointers.
