# std::optional, std::variant, and std::any

C++17 introduced three vocabulary types that replace common error-prone patterns: `std::optional`, `std::variant`, and `std::any`. Each encodes a different kind of "value or something else" relationship.

## std::optional\<T\>

`std::optional<T>` holds either a `T` or nothing (`std::nullopt`). It replaces sentinel values, output parameters, and nullable pointers for value types.

```cpp
#include <optional>
#include <string>

std::optional<std::string> findUser(int id) {
    if (id == 1) return "Alice";
    return std::nullopt;
}

auto name = findUser(1);
if (name) {
    std::cout << *name << "\n";          // dereference
    std::cout << name.value() << "\n";   // same
}

// value_or provides a fallback
std::cout << findUser(99).value_or("unknown") << "\n";  // unknown
```

`std::optional` is stack-allocated (no heap) and has the same size as `T` plus one byte for the "has value" flag.

## std::variant\<T1, T2, ...\>

`std::variant` is a **type-safe union**. It holds exactly one value of one of its listed types at a time:

```cpp
#include <variant>
#include <string>

using Result = std::variant<int, std::string>;

Result divide(int a, int b) {
    if (b == 0) return std::string("division by zero");
    return a / b;
}

Result r = divide(10, 2);

// Access with std::get (throws std::bad_variant_access if wrong type)
if (std::holds_alternative<int>(r))
    std::cout << std::get<int>(r) << "\n";   // 5

// Pattern-matching with std::visit
std::visit([](auto&& val) {
    using T = std::decay_t<decltype(val)>;
    if constexpr (std::is_same_v<T, int>)
        std::cout << "int: " << val << "\n";
    else
        std::cout << "error: " << val << "\n";
}, r);
```

### Result type pattern

`std::variant<Value, Error>` is C++'s version of Rust's `Result<T, E>`:

```cpp
using ParseResult = std::variant<double, std::string>;

ParseResult parseDouble(const std::string& s) {
    try { return std::stod(s); }
    catch (...) { return "invalid number: " + s; }
}
```

## std::any

`std::any` holds a value of **any** copyable type, with type-erased storage. It is a safer replacement for `void*`:

```cpp
#include <any>

std::any a = 42;
a = std::string("hello");
a = 3.14;

// Must know the type to get it back
try {
    double d = std::any_cast<double>(a);
    std::cout << d << "\n";   // 3.14
} catch (const std::bad_any_cast& e) {
    std::cerr << e.what() << "\n";
}

// Check type before casting
if (a.type() == typeid(double))
    std::cout << "It's a double\n";
```

`std::any` stores small objects inline (small-buffer optimization) and larger ones on the heap.

## Comparison Table

| Type | Use case | Type safety | Overhead |
|------|----------|-------------|----------|
| `std::optional<T>` | Value or absent | Compile-time (single T) | ~1 byte |
| `std::variant<Ts...>` | One of several known types | Compile-time | Size of largest T + tag |
| `std::any` | Unknown type at compile time | Runtime check | Heap alloc for large T |

## Structured Bindings with optional

C++17 structured bindings work with types that support `get<N>`:

```cpp
std::map<int, std::string> m = {{1, "one"}, {2, "two"}};

// insert_or_assign returns pair<iterator, bool>
auto [it, inserted] = m.insert_or_assign(3, "three");
std::cout << (inserted ? "new" : "updated") << "\n";
```

## Key Takeaways

- Use `std::optional` to represent "a value that might not be there" without sentinel magic numbers.
- Use `std::variant` when a function can return one of several distinct types — it replaces error-prone unions.
- Use `std::any` sparingly — only when the type is genuinely unknown at compile time (e.g., plugin systems, scripting bridges).
- All three eliminate a class of bugs that come from using `nullptr`, `-1`, or `void*` as "no value" markers.
