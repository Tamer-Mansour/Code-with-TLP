# std::optional, std::variant, and std::any

Three vocabulary types from C++17 replace unsafe C patterns — null pointers, tagged unions, and `void*` casts — with type-safe, value-semantic alternatives.

## `std::optional<T>` — Nullable Value Semantics

An optional either contains a `T` or is empty (`std::nullopt`). No heap allocation; the value is stored inline.

```cpp
#include <optional>

std::optional<int> find_index(const std::vector<int>& v, int target) {
    for (size_t i = 0; i < v.size(); ++i)
        if (v[i] == target) return i;   // implicitly wraps i
    return std::nullopt;                  // empty
}

auto idx = find_index(data, 42);
if (idx) {
    std::cout << "Found at " << *idx << "\n";  // dereference
}
```

### Key API

| Method | Effect |
|--------|--------|
| `opt.has_value()` / `if (opt)` | Check if non-empty |
| `*opt` / `opt.value()` | Access value (UB / throws if empty) |
| `opt.value_or(default)` | Safe access with fallback |
| `opt.reset()` | Make empty |
| `opt.emplace(args...)` | Construct in-place |

### Systems Use: Parsing Register Fields

```cpp
std::optional<uint8_t> read_status_byte(uint32_t addr) {
    if (!is_mapped(addr)) return std::nullopt;
    return *reinterpret_cast<volatile uint8_t*>(addr);
}

auto status = read_status_byte(0x4000'0005);
uint8_t val = status.value_or(0xFF);  // safe fallback
```

## `std::variant<T1, T2, ...>` — Type-Safe Tagged Union

A variant holds exactly one value of one of its listed types. The active type is tracked internally — accessing the wrong type throws `std::bad_variant_access`.

```cpp
#include <variant>

std::variant<int, double, std::string> v;

v = 42;
std::get<int>(v);           // 42
std::get<double>(v);        // throws bad_variant_access

v = "hello";
std::holds_alternative<std::string>(v);  // true
```

### `std::visit` — Pattern Matching

```cpp
std::variant<int, float, std::string> val = 3.14f;

std::visit([](auto&& arg) {
    using T = std::decay_t<decltype(arg)>;
    if constexpr (std::is_same_v<T, int>)
        std::cout << "int: " << arg;
    else if constexpr (std::is_same_v<T, float>)
        std::cout << "float: " << arg;
    else
        std::cout << "string: " << arg;
}, val);
```

### Systems Use: Command Packet

```cpp
struct ReadCmd  { uint32_t addr; };
struct WriteCmd { uint32_t addr; uint32_t val; };
struct ResetCmd {};

using Command = std::variant<ReadCmd, WriteCmd, ResetCmd>;

void dispatch(const Command& cmd) {
    std::visit([](auto&& c) {
        using T = std::decay_t<decltype(c)>;
        if constexpr (std::is_same_v<T, ReadCmd>)
            do_read(c.addr);
        else if constexpr (std::is_same_v<T, WriteCmd>)
            do_write(c.addr, c.val);
        else
            do_reset();
    }, cmd);
}
```

`std::variant` replaces unsafe C unions and eliminates the risk of reading the wrong union member.

## `std::any` — Type-Erased Value

`std::any` holds a value of any copy-constructible type. Access requires knowing the exact type at call time.

```cpp
#include <any>

std::any box = 42;
std::any_cast<int>(box);        // 42
std::any_cast<double>(box);     // throws bad_any_cast

box = std::string{"hello"};
box.type() == typeid(std::string);  // true
```

### When to Use Each

| Need | Use |
|------|-----|
| Optional absence of a single type | `std::optional<T>` |
| One of a fixed set of types | `std::variant<T1, T2, ...>` |
| Unknown type decided at runtime | `std::any` |
| C-style nullable pointer | Avoid — use optional/variant |

`std::any` should be a last resort — it sacrifices type safety and may heap-allocate. Prefer `variant` when the type set is known.

## Comparison: Old vs. Modern

```cpp
// Old C style — error-prone
struct Result { bool ok; union { int value; int error_code; }; };

// Modern C++ — safe, self-documenting
std::variant<int, std::error_code> result = compute();
```

## Worked Example: Device Configuration

```cpp
#include <optional>
#include <variant>
#include <string>

struct UartConfig { uint32_t baud; };
struct SpiConfig  { uint32_t clock_hz; uint8_t mode; };
struct I2cConfig  { uint32_t freq_hz; };

using BusConfig = std::variant<UartConfig, SpiConfig, I2cConfig>;

std::optional<BusConfig> parse_config(const std::string& desc) {
    if (desc == "uart") return UartConfig{115200};
    if (desc == "spi")  return SpiConfig{1'000'000, 0};
    if (desc == "i2c")  return I2cConfig{400'000};
    return std::nullopt;
}

auto cfg = parse_config("spi");
if (cfg) {
    std::visit([](auto&& c){ init_bus(c); }, *cfg);
}
```

> **Interview answer:** "`std::optional` is a nullable value with no heap allocation, replacing sentinel values and nullable pointers. `std::variant` is a type-safe tagged union where `std::visit` provides exhaustive dispatch. `std::any` erases the type entirely and is used only when the type set is truly unknown at compile time."
