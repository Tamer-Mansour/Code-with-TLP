# constexpr, enum class, and Strongly Typed Constants

Three features — `constexpr`, `enum class`, and `nullptr` — address longstanding weaknesses in C-era constant handling. Together they make compile-time computation safer and type-checked.

## `nullptr` — Replacing NULL and 0

`NULL` is `0` or `(void*)0` — an integer, not a pointer. This causes ambiguity:

```cpp
void f(int);
void f(char*);

f(NULL);    // calls f(int) — surprising!
f(nullptr); // calls f(char*) — correct
```

`nullptr` has type `std::nullptr_t`. It implicitly converts to any pointer type but not to integer types. Always use `nullptr` in modern C++.

```cpp
int* p = nullptr;
if (p == nullptr) { /* safe */ }

// nullptr_t can be a function parameter:
void f(std::nullptr_t) { /* called only with nullptr */ }
```

## `constexpr` — Compile-Time Computation

`constexpr` marks a variable or function as evaluable at compile time. The value is embedded in the binary as a constant — no load, no memory access at runtime.

### `constexpr` Variables

```cpp
constexpr int CACHE_LINE = 64;
constexpr size_t MAX_DEVS = 256;
constexpr double PI = 3.14159265358979;
```

Prefer `constexpr` over `#define` — it is typed, scoped, and debuggable.

| Feature | `#define` | `const` | `constexpr` |
|---------|-----------|---------|-------------|
| Type-safe | No | Yes | Yes |
| Scoped | No | Yes | Yes |
| Compile-time | Yes (text) | Sometimes | Yes |
| Usable in `switch`/template | No | Sometimes | Yes |

### `constexpr` Functions (C++11/14/17 progressively relaxed)

```cpp
constexpr int factorial(int n) {
    return (n <= 1) ? 1 : n * factorial(n - 1);
}

constexpr int f5 = factorial(5);  // computed at compile time: 120
```

C++14 allowed local variables and loops inside `constexpr` functions. C++17 added `constexpr if`. C++20 added `constexpr` containers.

### `constexpr` in Systems Code

```cpp
constexpr uint32_t BIT(int n) { return 1u << n; }
constexpr uint32_t GPIO_PIN_5 = BIT(5);  // compile-time: 0x00000020

// Used in a switch:
uint32_t reg = read_gpio();
switch (reg & GPIO_PIN_5) { /* legal because GPIO_PIN_5 is constexpr */ }
```

## `enum class` — Scoped, Strongly Typed Enumerations

Old `enum` has two problems: enumerators leak into the enclosing scope, and they implicitly convert to `int`.

```cpp
enum Color { Red, Green, Blue };
enum Direction { Left, Right, Up, Down };

int x = Red;     // silent conversion to int
bool same = (Red == Left);  // compares across enums — no error!
```

`enum class` fixes both:

```cpp
enum class Color { Red, Green, Blue };
enum class Direction { Left, Right };

Color c = Color::Red;   // must scope
// int x = c;           // ERROR: no implicit conversion
// bool b = (c == Direction::Left); // ERROR: different types
```

### Underlying Type Control

```cpp
enum class Status : uint8_t {
    OK    = 0,
    Error = 1,
    Busy  = 2,
};

static_assert(sizeof(Status) == 1);  // guaranteed
```

This is critical in protocol buffers, wire formats, and memory-mapped registers where the byte width matters.

### Combining `constexpr` and `enum class`

```cpp
enum class Interrupt : uint8_t {
    Timer   = 0,
    UART    = 1,
    GPIO    = 2,
    DMA     = 3,
};

constexpr uint8_t irq_priority(Interrupt irq) {
    switch (irq) {
        case Interrupt::Timer: return 0;  // highest
        case Interrupt::DMA:   return 1;
        default:               return 2;
    }
}

constexpr uint8_t timer_prio = irq_priority(Interrupt::Timer); // 0
```

## Worked Example: Register Bit Manipulation Without Magic Numbers

```cpp
#include <cstdint>

enum class GpioMode : uint8_t { Input = 0, Output = 1, AltFunc = 2 };
enum class GpioSpeed : uint8_t { Low = 0, Medium = 1, High = 2, VeryHigh = 3 };

constexpr uint32_t gpio_moder(uint8_t pin, GpioMode mode) {
    return static_cast<uint32_t>(mode) << (pin * 2);
}

constexpr uint32_t PA5_OUTPUT = gpio_moder(5, GpioMode::Output);
// Compiler computes 0x00000400 — no runtime cost
```

> **Interview answer:** "`constexpr` computes values at compile time with full type safety, replacing `#define` macros. `enum class` scopes enumerators and prevents implicit integer conversion, catching cross-enum comparisons at compile time. `nullptr` has type `std::nullptr_t` — it overload-resolves correctly and never silently converts to `int`."
