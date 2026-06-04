# Value Categories: lvalue, rvalue, xvalue

Every C++ expression has two independent properties: a **type** and a **value category**. Understanding value categories is essential to understanding move semantics, perfect forwarding, and why `std::move` works the way it does.

## The Full Taxonomy

C++11 introduced a refined hierarchy:

```
       expression
      /           \
  glvalue        rvalue
  /     \       /     \
lvalue  xvalue prvalue
```

| Category | Has identity? | Can be moved from? | Examples |
|----------|---------------|-------------------|---------|
| **lvalue** | Yes | No | `x`, `obj.field`, `*ptr`, `getRef()` |
| **prvalue** | No | Yes | `42`, `true`, `MyClass()`, `getValue()` |
| **xvalue** | Yes | Yes | `std::move(x)`, `static_cast<T&&>(x)` |
| **glvalue** | Yes | — | lvalue or xvalue |
| **rvalue** | — | Yes | prvalue or xvalue |

The terms "lvalue" and "rvalue" come from C: lvalues can appear on the **l**eft of an assignment; rvalues only on the **r**ight. Modern C++ extends this with xvalues ("expiring values").

## Named Variables are Always lvalues

This is the most commonly misunderstood rule. Even a variable declared as an rvalue reference is itself an **lvalue** when you use its name:

```cpp
int x = 42;        // x is an lvalue
int&& r = 42;      // r is declared as rvalue reference
                   // but: r itself is an LVALUE (it has a name)

void consume(int&& val); // takes rvalue reference

consume(r);            // ERROR: r is an lvalue!
consume(std::move(r)); // OK: std::move(r) is an xvalue
```

This is why `std::forward` is necessary in forwarding references — you must re-cast to preserve the original value category.

## std::move is a Cast, Not an Operation

`std::move` does **not** move anything. It is equivalent to:

```cpp
template <typename T>
constexpr std::remove_reference_t<T>&& move(T&& t) noexcept {
    return static_cast<std::remove_reference_t<T>&&>(t);
}
```

It casts its argument to an xvalue (rvalue reference). The actual data transfer happens in the **move constructor** or **move assignment operator** that is subsequently invoked. If no move constructor exists, the copy constructor is called instead.

```cpp
std::string a = "hello";
std::string b = std::move(a);  // std::move casts; String move-ctor does the work
// a is now valid but unspecified (typically empty)
```

## T&& in Templates: Forwarding References

There is a critical distinction between rvalue references and **forwarding references** (also called universal references):

```cpp
// Rvalue reference — T is concrete, non-deduced
void sink(std::string&& s);

// Forwarding reference — T is deduced in a template
template <typename T>
void wrapper(T&& arg);   // T&& here is a forwarding reference!
```

In the template case, `T&&` uses **reference collapsing** rules:
- If you pass an lvalue of type `U`, then `T = U&` and `T&& = U& && = U&` (lvalue ref)
- If you pass an rvalue of type `U`, then `T = U` and `T&& = U&&` (rvalue ref)

This is why `std::forward<T>(arg)` correctly forwards the value category:

```cpp
template <typename T>
void forward_example(T&& arg) {
    target(std::forward<T>(arg));  // lvalue if arg was lvalue; rvalue if arg was rvalue
}
```

## Return Value Optimization (RVO and NRVO)

A critical performance note: **do not write `return std::move(local_var);`** when returning a local variable. Modern compilers apply mandatory copy elision (**RVO**) and named return value optimization (**NRVO**) to eliminate the copy entirely. Adding `std::move` to a return statement can actually *prevent* NRVO and force a move instead of full elision, resulting in slower code.

```cpp
std::string make_string() {
    std::string result = "hello";
    return result;          // NRVO applies — no copy, no move
    // return std::move(result);  // WRONG: prevents NRVO, forces move instead
}
```

## Further Reading

- **C++ Core Guidelines** — [F.48: Don't return std::move(local)](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#Rf-return-move-local) explains why returning with `std::move` is an anti-pattern.
- **Modern C++ Tutorial (Changkun Ou)** — Chapter 3 covers rvalue references and move semantics with worked examples: https://changkun.de/modern-cpp/pdf/modern-cpp-tutorial-en-us.pdf
