# Copy Elision and Return Value Optimization

Copy elision is a compiler optimisation — and since C++17, a **mandatory language rule** in certain cases — that eliminates unnecessary copy or move operations by constructing the object directly in its final destination. Understanding it prevents over-engineering and explains why your copy constructor sometimes is never called.

## What Is Copy Elision?

Without elision, returning an object by value creates a temporary, then copies (or moves) it into the caller's variable:

```cpp
Buffer make() {
    Buffer tmp(10);
    return tmp;           // conceptually: copy tmp into caller's variable
}

Buffer b = make();        // conceptually: copy the returned temporary into b
```

With copy elision, the compiler constructs `tmp` **directly in the storage for `b`**, skipping all copy/move operations entirely. No destructor runs for the eliminated temporaries.

## Return Value Optimisation (RVO) vs Named RVO (NRVO)

### RVO (unnamed temporary)

```cpp
Buffer make() {
    return Buffer(10);    // RVO: construct directly in caller's slot
}
```

The object has no name inside `make`; the compiler always elides this copy. This is **mandatory** in C++17 (and was already performed by virtually every compiler since C++03 as an optional optimisation).

### NRVO (named object)

```cpp
Buffer make() {
    Buffer tmp(10);       // named local variable
    return tmp;           // NRVO: may elide copy
}
```

NRVO is **optional** — the compiler is permitted to elide it but is not required to. Most optimising compilers (GCC, Clang, MSVC) apply NRVO in straightforward cases.

## When NRVO Cannot Apply

The compiler may not be able to apply NRVO when:

- There are multiple `return` statements returning different variables.
- The returned variable is a function parameter.
- The returned variable is chosen conditionally.

```cpp
Buffer make(bool flag) {
    Buffer a(5), b(10);
    return flag ? a : b;   // compiler can't know which to elide at compile time
}
```

Here the compiler falls back to the move constructor (C++11 and later) rather than a copy.

## Mandatory Elision in C++17

C++17 guarantees elision for **prvalue** (pure rvalue) expressions in two contexts:

1. Initialising a variable from a prvalue: `Buffer b = Buffer(10);`
2. Returning a prvalue: `return Buffer(10);`

In these cases the copy/move constructor need not even be accessible or defined.

```cpp
class NonCopyable {
    NonCopyable(const NonCopyable&) = delete;
    NonCopyable(NonCopyable&&)      = delete;
public:
    NonCopyable() = default;
};

NonCopyable make() {
    return NonCopyable();   // OK in C++17: mandatory elision, no copy needed
}
NonCopyable x = make();     // Also OK
```

In C++14 or earlier, this would fail to compile because the deleted copy/move constructors are conceptually needed even if not called.

## Observing Elision

You can verify elision by adding a print to the copy constructor:

```cpp
Buffer(const Buffer& other) {
    std::cout << "Copy constructor called\n";
    // ...
}
```

```cpp
Buffer b = make();   // often prints nothing — elision in effect
```

Compile with `-fno-elide-constructors` (GCC/Clang) to disable elision and observe the copy constructor calls that elision normally suppresses.

## Practical Implications

- **Return local objects by value** without fear. The compiler elides copies in the common case.
- **Do not prematurely `std::move` a return value.** Writing `return std::move(tmp)` actually **prevents** NRVO by converting the named local into an xvalue, forcing a move instead of elision.

```cpp
Buffer make() {
    Buffer tmp(10);
    return std::move(tmp);  // BAD: disables NRVO, forces move constructor
    // return tmp;           // GOOD: allows NRVO
}
```

- Even when elision does not occur (multiple return paths), the compiler uses the **move constructor** (not copy constructor) for named locals in return statements — per C++11's implicit move rules.

## Summary

| Scenario | C++03 | C++11/14 | C++17 |
|---|---|---|---|
| `return T();` (prvalue) | Optional elision | Optional elision | Mandatory elision |
| `return namedVar;` | Optional NRVO | Optional NRVO + implicit move | Optional NRVO + implicit move |
| `return std::move(x);` | Copy | Move | Move (no elision) |

> **Interview answer:** Copy elision (including RVO and NRVO) allows the compiler to construct a returned object directly in the caller's storage, eliminating the copy/move entirely. Since C++17, elision of prvalues is mandatory and the copy/move constructor need not even exist. You should return local variables by name without `std::move` to enable NRVO.
