# Uniform Initialization and Narrowing

C++11 introduced brace initialization `{}` — also called uniform initialization — as a single consistent syntax for initializing any type. It also introduces **narrowing checks** that older `()` and `=` syntax did not enforce.

## The Problem with Old Initialization

Pre-C++11 had four different syntaxes that behaved inconsistently:

```cpp
int a = 5;        // copy-initialization
int b(5);         // direct-initialization
int arr[] = {1,2,3}; // aggregate initialization (braces only here)
// No single syntax worked everywhere
```

## Uniform Brace Initialization

`{}` works everywhere and consistently:

```cpp
int a{5};
double d{3.14};
std::string s{"hello"};
std::vector<int> v{1, 2, 3};

struct Point { int x, y; };
Point p{10, 20};   // aggregate init
```

This syntax works for built-in types, aggregates, STL containers, and user-defined types — hence "uniform."

## Narrowing Conversion Detection

The most safety-critical feature: brace initialization **rejects implicit narrowing conversions** at compile time.

```cpp
int  i  = 3.9;    // OK (silent truncation to 3)
int  j  {3.9};    // ERROR: narrowing conversion from double to int

float f = 1e40;   // UB (overflow), no warning by default
float g {1e40};   // ERROR at compile time

uint8_t  byte = 300;   // silent truncation to 44
uint8_t  safe {300};   // ERROR: value doesn't fit
```

This is invaluable in systems programming where buffer sizes, register widths, and DMA lengths must be exact.

### What Counts as Narrowing?

| Conversion | Narrowing? |
|-----------|-----------|
| `double` → `int` | Yes |
| `int` → `double` | No (all ints representable) |
| `int` → `float` | Yes (precision loss possible) |
| `unsigned` → `int` (same width) | Yes (sign change) |
| constant that fits | No (e.g., `int{2u}` OK) |

## `std::initializer_list` Gotcha

When a constructor takes `std::initializer_list`, brace-init prefers it over other constructors:

```cpp
std::vector<int> v1(3, 0);  // three zeros: {0, 0, 0}
std::vector<int> v2{3, 0};  // two elements: {3, 0}
```

This surprises many developers. The rule: if any constructor takes `initializer_list`, braces prefer it.

## Value Initialization

Empty braces `{}` perform value initialization — zero for scalars, default constructor for class types:

```cpp
int  x{};     // 0
double d{};   // 0.0
char* p{};    // nullptr

struct Packet { uint32_t len; uint8_t data[64]; };
Packet pkt{}; // all bytes zeroed
```

This is safer than `int x;` (indeterminate) and idiomatic in embedded/systems code.

## Default Member Initializers

Brace syntax works for in-class initializers:

```cpp
struct Config {
    uint32_t baud_rate{115200};
    uint8_t  stop_bits{1};
    bool     parity{false};
};
```

## Aggregates (C++17 and Later)

C++17 relaxed aggregate rules — a class with base classes (no virtual functions, no user-declared constructors) can still be aggregate-initialized:

```cpp
struct Base { int x; };
struct Derived : Base { int y; };

Derived d{1, 2};  // x=1, y=2 in C++17
```

## Worked Example: Safe Hardware Configuration

```cpp
#include <cstdint>

struct UartConfig {
    uint32_t baud{9600};
    uint8_t  data_bits{8};
    uint8_t  stop_bits{1};
    bool     parity_enable{false};
};

void init_uart(const UartConfig& cfg);

int main() {
    // Narrowing error caught at compile time:
    // UartConfig bad{9600, 256, 1, false};  // ERROR: 256 doesn't fit uint8_t

    UartConfig cfg{115200, 8, 1, false};    // OK
    init_uart(cfg);
}
```

> **Interview answer:** "Brace initialization is uniform — it works for all types — and adds compile-time narrowing checks that `=` and `()` initialization do not. Empty braces `{}` zero-initialize scalars and call default constructors, making it the safest way to initialize variables in systems code."
