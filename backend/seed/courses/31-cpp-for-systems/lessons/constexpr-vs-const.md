# constexpr vs const: Compile-Time vs Read-Only

Both `const` and `constexpr` restrict mutation, but they differ fundamentally in *when* the value is known.

## The Core Distinction

| Qualifier | Value known at | Can appear in array size, template arg, switch case? |
|---|---|---|
| `const` | Run time (or compile time if initializer is literal) | Only if initialized from a constant expression |
| `constexpr` | Compile time (guaranteed) | Always |

```cpp
int n = get_user_input();       // runtime value
const int a = n;                // const but NOT constexpr
// int arr[a];                  // ERROR — a is not a constant expression

constexpr int MAX = 1024;       // compile-time constant
int arr[MAX];                   // OK
```

## constexpr Variables

A `constexpr` variable must be initialized with a **constant expression** — one that the compiler can fully evaluate during translation.

```cpp
constexpr double PI   = 3.14159265358979;
constexpr int    MASK = 0xFF00'0000;          // compile-time bitmask
constexpr size_t BUF  = 4 * 1024;            // 4 KiB, evaluated at compile time
```

All `constexpr` variables are implicitly `const`.

## constexpr Functions

A `constexpr` function can be evaluated at compile time when all its arguments are constant expressions, and at run time otherwise.

```cpp
constexpr int round_up_power_of_two(int n) {
    int p = 1;
    while (p < n) p <<= 1;
    return p;
}

constexpr int BUF_SIZE = round_up_power_of_two(300);  // evaluated at compile time: 512
int dynamic = round_up_power_of_two(get_input());      // evaluated at run time
```

In C++20 and later, `consteval` forces compile-time-only evaluation; `constinit` guarantees a variable is initialized at compile time (but remains mutable).

## Why This Matters in Systems Code

Compile-time constants eliminate magic numbers and prevent runtime overhead for fixed parameters:

```cpp
// Embedded: IRQ table size must be a compile-time constant for static allocation
constexpr int IRQ_COUNT = 256;
void (*irq_handlers[IRQ_COUNT])(void) = {};  // zero-initialized at compile time
```

Template parameters require constant expressions — `constexpr` bridges user-defined logic into templates:

```cpp
template<size_t N>
struct RingBuffer { /* ... */ };

constexpr size_t RING_SIZE = 64;
RingBuffer<RING_SIZE> uart_rx;  // OK
```

## Common Pitfall: const Does Not Guarantee Compile-Time

```cpp
const int x = std::rand();   // const but runtime — cannot use as template arg
constexpr int y = 42;        // compile-time — safe to use anywhere
```

Another pitfall is using `constexpr` with types that have non-trivial constructors in older standards. C++20 greatly relaxed these rules, allowing `constexpr` constructors, destructors, and `std::string` / `std::vector` inside `constexpr` functions.

## Worked Example: Bitmask Helpers

```cpp
constexpr uint32_t make_mask(int start, int len) {
    return ((1u << len) - 1u) << start;
}

constexpr uint32_t STATUS_BITS = make_mask(4, 3);  // bits [6:4], evaluated at compile time
// STATUS_BITS == 0x70

uint32_t extract(uint32_t reg) {
    return (reg & STATUS_BITS) >> 4;
}
```

The compiler computes `STATUS_BITS = 0x70` during translation; no runtime cost.

> **Interview answer:** "`const` means the value cannot be changed after initialization, but it may be determined at runtime. `constexpr` guarantees compile-time evaluation, which is required for array sizes, template arguments, and zero-overhead embedded constants."
