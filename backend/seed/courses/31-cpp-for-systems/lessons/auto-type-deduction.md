# auto and Type Deduction Rules

Type deduction lets the compiler infer the type of a variable from its initializer. The `auto` keyword, introduced in C++11, eliminates verbose type annotations without sacrificing type safety.

## Basic Usage

```cpp
auto x = 42;          // int
auto y = 3.14;        // double
auto z = "hello";     // const char*
auto w = std::string{"hi"}; // std::string
```

The compiler inspects the right-hand side at compile time and substitutes the concrete type. There is zero runtime cost.

## Template Argument Deduction — The Foundation

`auto` follows the same rules as template argument deduction. Think of `auto` as a placeholder `T` in:

```cpp
template<typename T>
void f(T param);
```

Three cases matter:

### Case 1: `auto` (value, drops cv-qualifiers and references)

```cpp
const int ci = 10;
auto a = ci;   // int, not const int — qualifiers stripped
auto b = ci;   // int
```

### Case 2: `auto&` (reference, preserves cv-qualifiers)

```cpp
const int ci = 10;
auto& r = ci;  // const int& — cv kept because we asked for a ref
```

### Case 3: `auto&&` (universal/forwarding reference)

```cpp
int x = 5;
auto&& ur1 = x;   // int& (lvalue → lvalue ref)
auto&& ur2 = 42;  // int&& (rvalue → rvalue ref)
```

## Common Pitfalls

| Pitfall | What happens | Fix |
|---------|-------------|-----|
| `auto` with braced initializer `{}` | Deduces `std::initializer_list<T>` in C++11/14 | Use `= value` or `auto x{42}` (C++17 deduces `int`) |
| Losing `const` | `const int* p; auto q = p;` → `q` is `const int*` but `*q` is still const — pointer itself is non-const | Be explicit: `const auto q = p;` |
| `auto` for proxy types | `auto row = matrix[0]` may capture a proxy object, not a real row | Use `auto&` or the concrete type |
| `auto` and `std::initializer_list` | `auto il = {1,2,3};` deduces `std::initializer_list<int>` | Rarely what you want in systems code |

## `auto` in Function Return Types (C++14)

```cpp
auto add(int a, int b) {
    return a + b;  // deduces int
}
```

All return paths must produce the same deduced type; the compiler errors otherwise.

## Trailing Return Types (C++11)

Useful when the return type depends on parameters:

```cpp
auto multiply(double a, int b) -> double {
    return a * b;
}
```

## Systems Engineering Perspective

In driver and OS code, `auto` shines when dealing with complex iterator or STL types:

```cpp
std::map<uint32_t, DeviceDescriptor> devices;

// Without auto:
std::map<uint32_t, DeviceDescriptor>::iterator it = devices.find(id);

// With auto:
auto it = devices.find(id);
```

It also prevents silent narrowing bugs because the inferred type exactly matches the expression — no implicit truncation.

## Worked Example: Iterating a Register Map

```cpp
#include <cstdint>
#include <vector>

struct Register {
    uint32_t address;
    uint32_t value;
};

void dump_registers(const std::vector<Register>& regs) {
    for (const auto& reg : regs) {   // const auto& avoids copy, preserves const
        // reg.address and reg.value are accessible
    }
}
```

Using `const auto&` here is the idiomatic pattern for read-only iteration — it avoids copying, preserves `const`-correctness, and adapts to any element type.

> **Interview answer:** "`auto` deduces the type of a variable from its initializer using the same rules as template argument deduction — it strips top-level cv-qualifiers and references unless you write `auto&` or `const auto&`. It has zero runtime cost and is preferred over repeating verbose types."
