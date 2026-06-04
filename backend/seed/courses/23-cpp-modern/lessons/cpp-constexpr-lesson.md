# Compile-Time Programming: constexpr, consteval, and constinit

Modern C++ moves computation from runtime to compile time. This catches errors earlier, produces faster binaries, and enables powerful metaprogramming — all without macros or external code generators.

## constexpr Functions

A `constexpr` function **can** be evaluated at compile time when all arguments are compile-time constants, but it is not **required** to be:

```cpp
constexpr int square(int x) { return x * x; }

constexpr int a = square(5);   // compile-time: a = 25
int n = 7;
int b = square(n);             // runtime: n is not constexpr
```

The same function serves both contexts. The compiler decides which path to take based on how the result is used.

## When is Compile-Time Evaluation Required?

Only contexts that **demand a constant expression** force compile-time evaluation:

```cpp
constexpr int N = square(5);       // required — constexpr variable
int arr[square(4)];                // required — array size
template <int V> struct Tag {};
Tag<square(3)> tag;               // required — template non-type argument
static_assert(square(2) == 4);    // required — static_assert
```

Without such a context, `square` may run at runtime even with constant arguments — it is implementation-defined.

## consteval (C++20): Guaranteed Compile-Time

`consteval` makes compile-time evaluation **mandatory**. If the compiler cannot evaluate it at compile time, it is a hard error:

```cpp
consteval int must_be_compile_time(int x) { return x * x; }

constexpr int a = must_be_compile_time(5);  // OK
int n = 7;
int b = must_be_compile_time(n);           // ERROR: n is not a constant expression
```

Use `consteval` when you are writing a compile-time computation that must never fall back to runtime.

## constinit (C++20): Guaranteed Compile-Time Initialization

`constinit` ensures a variable is initialized at compile time but does **not** make it const. It solves the "static initialization order fiasco":

```cpp
constinit int global_value = compute_at_compile_time();  // OK
constinit int mutable_counter = 0;                       // OK — can be modified later
```

Contrast with `constexpr` variables, which are always `const`.

## static_assert: Compile-Time Assertions

```cpp
static_assert(sizeof(int) == 4, "This code assumes 32-bit int");
static_assert(std::is_trivially_copyable_v<MyStruct>);
```

`static_assert` fires at compile time with a clear message. It is the compile-time equivalent of `assert`.

## Fibonacci Example

```cpp
constexpr long long fib(int n) {
    if (n <= 1) return n;
    return fib(n - 1) + fib(n - 2);
}

// Evaluated at compile time:
constexpr long long f10 = fib(10);  // = 55

// Evaluated at runtime:
int k;
std::cin >> k;
long long result = fib(k);  // runtime — k is not constexpr
```

## Key Distinction: constexpr vs consteval vs const

| Keyword | Meaning |
|---------|---------|
| `const` | Value cannot change after initialization (may be runtime) |
| `constexpr` | Can be compile-time; falls back to runtime if context does not require it |
| `consteval` | Must be compile-time; error if not possible |
| `constinit` | Must be initialized at compile time; value may change at runtime |

## Further Reading

- **Modern C++ Tutorial (Changkun Ou)**, Chapter 4: Constant expressions and constexpr — https://changkun.de/modern-cpp/pdf/modern-cpp-tutorial-en-us.pdf
- **C++ Core Guidelines** — [Con.5: Use constexpr for values that can be computed at compile time](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#Rconst-constexpr)
- **Federico Busato's Modern C++ Programming (GitHub)** — Slides on compile-time programming, constexpr, and TMP: https://github.com/federico-busato/Modern-CPP-Programming
