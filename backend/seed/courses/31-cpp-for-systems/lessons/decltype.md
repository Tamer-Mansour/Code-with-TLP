# decltype and decltype(auto)

While `auto` deduces a type by stripping qualifiers, `decltype` asks: "what is the exact declared type of this expression, including references and cv-qualifiers?" It is an unevaluated context — the expression is never executed.

## Basic `decltype`

```cpp
int x = 0;
decltype(x) y = x;       // int (named variable → declared type)

const int ci = 0;
decltype(ci) z = ci;     // const int

int& r = x;
decltype(r) s = x;       // int& (reference preserved)
```

The key rule: if the operand is a **named variable**, `decltype` gives its declared type exactly.

## Expression vs. Variable

When the operand is an expression (not just a name), `decltype` applies extra rules based on the expression's value category:

| Expression kind | Result |
|-----------------|--------|
| Named variable `x` | declared type of `x` |
| lvalue expression `(x)` | `T&` |
| xvalue expression | `T&&` |
| prvalue expression | `T` |

```cpp
int x = 5;
decltype(x)   a = x;   // int   (named var)
decltype((x)) b = x;   // int&  (parenthesized → lvalue expression)
decltype(x+0) c = x;   // int   (prvalue expression)
```

The `(x)` vs `x` distinction is a famous pitfall — extra parentheses change the result.

## Trailing Return Types with `decltype`

Before C++14, `auto` return deduction didn't exist. `decltype` filled the gap:

```cpp
template<typename A, typename B>
auto add(A a, B b) -> decltype(a + b) {
    return a + b;
}
```

This deduces the exact type of `a + b`, including whether it is a reference.

## `decltype(auto)` — Best of Both Worlds (C++14)

`decltype(auto)` says: "use `decltype` rules on the initializing expression, but let the compiler figure it out."

```cpp
int x = 42;
int& ref = x;

auto         a = ref;          // int  (auto strips reference)
decltype(auto) b = ref;        // int& (decltype rules preserve reference)
```

This is particularly powerful for perfect forwarding of return types:

```cpp
template<typename F, typename... Args>
decltype(auto) call(F&& f, Args&&... args) {
    return std::forward<F>(f)(std::forward<Args>(args)...);
}
```

If `f` returns `int&`, `call` returns `int&`. If `f` returns `int`, `call` returns `int`. No information is lost.

## Systems Engineering Use Cases

### Generic wrappers that preserve value category

```cpp
// Memoize any callable, preserving its exact return type
template<typename Fn>
decltype(auto) cached_call(Fn&& fn) {
    static auto result = fn();
    return result;  // decltype(auto) keeps result's type exact
}
```

### Interoperating with hardware register accessors

```cpp
volatile uint32_t MMIO_REG = 0;

decltype(MMIO_REG) shadow = 0;  // volatile uint32_t — exact match
```

Using `auto` here would silently drop `volatile`, causing the compiler to optimize away reads — a catastrophic bug in embedded code.

## Common Pitfalls

- **Extra parentheses**: `decltype(x)` vs `decltype((x))` — both compile, different types.
- **`decltype(auto)` in a lambda**: can cause surprising reference lifetimes.
- **`volatile` stripping**: always use `decltype` (not `auto`) when mirroring hardware register types.

## Worked Example

```cpp
#include <cstdint>

volatile uint32_t* const CONTROL_REG =
    reinterpret_cast<volatile uint32_t*>(0x4000'0000);

// Safe: shadow has type volatile uint32_t
decltype(*CONTROL_REG) shadow = 0;

// Dangerous: auto strips volatile — reads may be elided by optimizer
// auto shadow = *CONTROL_REG;   // DON'T DO THIS
```

> **Interview answer:** "`decltype(expr)` yields the exact declared type of a named variable, or applies value-category rules for expressions (lvalue→`T&`, xvalue→`T&&`, prvalue→`T`). `decltype(auto)` uses those same rules for variable initialization and return-type deduction, unlike plain `auto` which strips references and cv-qualifiers."
