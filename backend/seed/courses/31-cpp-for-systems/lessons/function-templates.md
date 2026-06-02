# Function Templates and Argument Deduction

A **function template** is a blueprint the compiler uses to generate a family of functions — one for each unique combination of template arguments. The generated functions are called **instantiations**, and the process of creating them is **instantiation**.

## Defining a Function Template

```cpp
template <typename T>
T max_of(T a, T b) {
    return (a > b) ? a : b;
}

// Usage
int   i = max_of(3, 5);        // instantiates max_of<int>
double d = max_of(1.2, 3.4);   // instantiates max_of<double>
```

`typename` and `class` are interchangeable in template parameter lists; `typename` is preferred for clarity.

## Template Argument Deduction

The compiler **deduces** template arguments from the types of function call arguments, so you rarely need to write them explicitly.

```cpp
template <typename T>
void print(const T& val) {
    std::cout << val << "\n";
}

print(42);          // T deduced as int
print(3.14);        // T deduced as double
print("hello");     // T deduced as char[6] (array type, not std::string!)
```

### Deduction Rules to Know

- The compiler strips top-level references and const from the argument before deduction.
- `T` cannot be deduced from a return type alone — only from parameters.
- Deduction fails when two arguments imply conflicting types: `max_of(1, 2.0)` is a compile error because `T` cannot simultaneously be `int` and `double`.

```cpp
// Fix: explicit instantiation
double r = max_of<double>(1, 2.0);

// Or: use two independent type parameters
template <typename T, typename U>
auto max_two(T a, U b) -> decltype(a > b ? a : b) {
    return (a > b) ? a : b;
}
```

## Non-Type Template Parameters

Templates can also accept values, not just types:

```cpp
template <int N>
void print_n_times(const char* msg) {
    for (int i = 0; i < N; ++i)
        std::cout << msg << "\n";
}

print_n_times<3>("hello");   // prints 3 times
```

Non-type parameters must be compile-time constants. Common uses: fixed-size arrays, compile-time loop counts, bit-flags.

## Variadic Templates

C++11 introduced **parameter packs** for templates that accept any number of arguments:

```cpp
#include <iostream>

template <typename... Args>
void log(Args... args) {
    (std::cout << ... << args) << "\n";   // C++17 fold expression
}

log(1, " + ", 2, " = ", 3);   // prints: 1 + 2 = 3
```

The `...` expands the pack. Fold expressions (`(op ... pack)`) make pack operations concise in C++17.

## Worked Example: Generic Clamp

```cpp
template <typename T>
const T& clamp(const T& val, const T& lo, const T& hi) {
    if (val < lo) return lo;
    if (val > hi) return hi;
    return val;
}

int   x = clamp(15, 0, 10);       // 10
double y = clamp(-1.5, 0.0, 1.0); // 0.0
```

This is essentially `std::clamp` from C++17. The template works for any type with `operator<` and `operator>`.

## Inline and Linkage

Function templates are implicitly `inline` — each translation unit that uses a given instantiation will have its own copy, and the linker merges duplicates. This means templates are usually defined in header files, not `.cpp` files. Putting the definition in a `.cpp` and only declaring it in the header leads to **linker errors** (undefined reference) unless you use **explicit instantiation**.

## Common Pitfalls

- **Type promotion surprises**: `max_of(1, 2U)` — signed vs unsigned mismatch causes a deduction conflict.
- **Reference collapsing**: `template <typename T> void f(T&& x)` — here `T&&` is a *forwarding reference*, not an rvalue reference. This is a distinct concept (perfect forwarding) covered separately.
- **Template code in headers**: forgetting to put template definitions in the header is the most common beginner linker error.

> **Interview answer:** "A function template lets the compiler generate type-specific instantiations from a single generic definition. Template argument deduction infers `T` from the call's argument types automatically; explicit angle-bracket syntax overrides deduction when needed."
