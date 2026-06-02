# Concepts and Constraining Templates (Intro)

Before C++20, a template that received an incompatible type produced notoriously long and cryptic error messages. **Concepts** solve this by attaching readable constraints to template parameters, giving both clearer errors and enforced semantic requirements at the call site.

## The Problem Concepts Solve

```cpp
template <typename T>
T add(T a, T b) { return a + b; }

// Before concepts, passing an incompatible type:
add(std::vector<int>{}, std::vector<int>{});
// Produces a wall of template error text pointing inside add() — not at the call site
```

With concepts the error is one line at the call site: "`T` does not satisfy constraint `Addable`".

## Defining a Concept

A concept is a compile-time boolean predicate on types:

```cpp
#include <concepts>

// Require that T supports operator+
template <typename T>
concept Addable = requires(T a, T b) {
    { a + b } -> std::convertible_to<T>;
};
```

The `requires` expression lists valid operations. The `->` arrow constrains the result type. If the expression is ill-formed for a given `T`, the concept evaluates to `false`.

## Using Concepts to Constrain Templates

Three equivalent syntactic styles — pick whichever is clearest:

```cpp
// Style 1: requires-clause
template <typename T>
    requires Addable<T>
T add(T a, T b) { return a + b; }

// Style 2: abbreviated function template (C++20)
Addable auto add(Addable auto a, Addable auto b) { return a + b; }

// Style 3: constrained template parameter
template <Addable T>
T add(T a, T b) { return a + b; }
```

All three produce the same code; the abbreviated form is the most concise for simple cases.

## Standard Library Concepts

`<concepts>` ships with a rich set of predefined concepts:

| Concept | Meaning |
|---|---|
| `std::integral<T>` | T is an integer type |
| `std::floating_point<T>` | T is a floating-point type |
| `std::copyable<T>` | T can be copy-constructed and copy-assigned |
| `std::movable<T>` | T can be move-constructed and move-assigned |
| `std::equality_comparable<T>` | T supports `==` and `!=` |
| `std::totally_ordered<T>` | T supports all six comparison operators |
| `std::invocable<F, Args...>` | F can be called with Args |
| `std::ranges::range<R>` | R has `begin()` and `end()` |

```cpp
#include <concepts>

template <std::integral T>
T gcd(T a, T b) {
    while (b) { a %= b; std::swap(a, b); }
    return a;
}

gcd(12, 8);        // OK — int satisfies std::integral
// gcd(1.5, 2.5);  // Error: double does not satisfy std::integral
```

## Compound Constraints with `&&` and `||`

```cpp
template <typename T>
concept Numeric = std::integral<T> || std::floating_point<T>;

template <Numeric T>
T square(T x) { return x * x; }
```

Concepts compose cleanly with logical operators.

## Requires Expressions in Depth

```cpp
template <typename T>
concept Printable = requires(T v) {
    { std::cout << v };          // must compile
};

template <typename It>
concept ForwardIter = requires(It i) {
    *i;                           // dereferenceable
    ++i;                          // pre-incrementable
    { i != i } -> std::convertible_to<bool>;
};
```

Each requirement inside `requires { ... }` is tested for compilability — if it fails, the concept is `false` for that type.

## Concept-Driven Overloads

Concepts participate in overload resolution — the most constrained overload wins:

```cpp
template <typename T>
void process(T v) { std::cout << "generic\n"; }

template <std::integral T>
void process(T v) { std::cout << "integer: " << v << "\n"; }

process(42);      // "integer: 42"
process(3.14);    // "generic"
process("hi");    // "generic"
```

## Common Pitfalls

- A concept checks **syntactic** validity, not full semantic correctness. `operator+` existing does not mean addition is associative.
- `requires requires` (double requires) is legal but signals you should extract a named concept.
- Concepts constrain template argument deduction too — an `auto` parameter with a concept constraint will refuse incompatible deductions at the call site.

> **Interview answer:** "Concepts are compile-time predicates that constrain template parameters. They improve error messages, enable concept-based overloading, and document requirements. A concept is defined with `concept Name = requires(T v) { ... };` and used as a constraint in the template parameter list or a requires-clause."
