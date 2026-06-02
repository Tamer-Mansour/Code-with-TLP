# Error Handling: Exceptions and Error Codes

C++ provides multiple error-handling mechanisms. Choosing the right one is a design decision that affects performance, clarity, and API usability.

## Exceptions

Exceptions are the standard mechanism for propagating errors that cannot be handled at the call site:

```cpp
#include <stdexcept>
#include <iostream>

double safeDivide(double a, double b) {
    if (b == 0.0)
        throw std::invalid_argument("division by zero");
    return a / b;
}

int main() {
    try {
        std::cout << safeDivide(10.0, 2.0) << "\n";   // 5
        std::cout << safeDivide(10.0, 0.0) << "\n";   // throws
    }
    catch (const std::invalid_argument& e) {
        std::cerr << "Error: " << e.what() << "\n";
    }
    catch (const std::exception& e) {
        std::cerr << "Unknown error: " << e.what() << "\n";
    }
}
```

### Standard Exception Hierarchy

| Class | Use for |
|-------|---------|
| `std::exception` | Base class |
| `std::logic_error` | Programmer errors (precondition violation) |
| `std::invalid_argument` | Bad function argument |
| `std::out_of_range` | Index out of range |
| `std::runtime_error` | Runtime failures |
| `std::overflow_error` | Arithmetic overflow |
| `std::bad_alloc` | `new` fails (out of memory) |

Prefer deriving from `std::runtime_error` or `std::logic_error` for custom exceptions:

```cpp
struct DatabaseError : std::runtime_error {
    explicit DatabaseError(const std::string& msg)
        : std::runtime_error("DB: " + msg) {}
};
```

### Exception Safety Guarantees

| Level | What is guaranteed |
|-------|--------------------|
| **No-throw** | Function never throws. Mark with `noexcept`. |
| **Strong** | Either succeeds fully or leaves state unchanged (like a transaction). |
| **Basic** | Object remains in a valid (but possibly changed) state if an exception escapes. |
| **None** | No guarantee — avoid. |

```cpp
void swap(Buffer& a, Buffer& b) noexcept {
    std::swap(a.data_, b.data_);
    std::swap(a.size_, b.size_);
}
```

Mark destructors and move operations `noexcept` whenever possible — it enables important STL optimizations.

## Error Codes (`std::error_code`)

Low-level or performance-critical code often returns error codes instead of throwing:

```cpp
#include <system_error>

std::error_code openFile(const std::string& path) {
    if (path.empty())
        return std::make_error_code(std::errc::invalid_argument);
    return {};   // default-constructed = no error
}

auto ec = openFile("");
if (ec)
    std::cerr << "Error: " << ec.message() << "\n";
```

The standard `<filesystem>` library uses this pattern throughout.

## `std::optional` for "Maybe" Return Values

When a function might not return a value (but that's not an error), use `std::optional<T>`:

```cpp
#include <optional>

std::optional<int> parseInt(const std::string& s) {
    try { return std::stoi(s); }
    catch (...) { return std::nullopt; }
}

if (auto val = parseInt("42"))
    std::cout << "Parsed: " << *val << "\n";
else
    std::cout << "Not a number\n";
```

`std::optional` avoids sentinel values like `-1` or `nullptr`, making the API self-documenting.

## Choosing the Right Mechanism

| Situation | Recommended mechanism |
|-----------|----------------------|
| Truly exceptional failure (IO error, bad alloc) | Exceptions |
| Function that may not find/produce a value | `std::optional` |
| Performance-critical paths; embedded/real-time | Error codes |
| Logic errors (developer bug) | `assert` / exceptions |
| C interop | Return codes + errno |

## `[[nodiscard]]`

Annotate functions whose return value must not be ignored:

```cpp
[[nodiscard]] std::error_code connect(const std::string& host);

connect("db.local");   // ⚠ compiler warning: result discarded
```

This is a lightweight way to prevent "fire and forget" bugs with error returns.
