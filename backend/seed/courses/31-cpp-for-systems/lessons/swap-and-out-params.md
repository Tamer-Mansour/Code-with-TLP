# Implementing swap and Output Parameters

Two of the most practical applications of pass-by-reference are `swap` and output parameters. Both patterns appear constantly in systems code and library design. Understanding them solidifies your grasp of reference semantics.

## Implementing swap

`swap` exchanges the values of two objects. Without references (or pointers), you cannot write a general swap — you would only be swapping copies:

```cpp
// Wrong: swaps copies, caller unchanged
void badSwap(int a, int b) {
    int tmp = a; a = b; b = tmp;
}

// Correct: references alias the caller's variables
void swap(int& a, int& b) {
    int tmp = a;
    a = b;
    b = tmp;
}

int main() {
    int x = 10, y = 20;
    swap(x, y);
    std::cout << x << " " << y;  // 20 10
}
```

### Generic swap with Templates

The standard library's `std::swap` is a function template:

```cpp
template<typename T>
void swap(T& a, T& b) {
    T tmp = std::move(a);
    a     = std::move(b);
    b     = std::move(tmp);
}
```

Using `std::move` avoids a potentially expensive copy for large types — the three operations become three moves instead of three copies. For a `std::vector`, this is O(1) regardless of element count.

### The Copy-and-Swap Idiom

`swap` is foundational to the **copy-and-swap** assignment operator, a pattern that achieves exception safety with minimal code:

```cpp
class Buffer {
    char* data_;
    size_t size_;
public:
    friend void swap(Buffer& a, Buffer& b) noexcept {
        using std::swap;
        swap(a.data_, b.data_);
        swap(a.size_, b.size_);
    }
    Buffer& operator=(Buffer rhs) {  // rhs is a copy (value parameter)
        swap(*this, rhs);            // exchange internals
        return *this;                // rhs destructor cleans up old data
    }
};
```

## Output Parameters

An output parameter is a reference (or pointer) argument that the function writes to instead of (or in addition to) returning a value.

### Reference Output Parameter

```cpp
void divide(int numerator, int denominator,
            int& quotient, int& remainder) {
    quotient  = numerator / denominator;
    remainder = numerator % denominator;
}

int main() {
    int q, r;
    divide(17, 5, q, r);
    std::cout << q << " remainder " << r;  // 3 remainder 2
}
```

Two outputs with one function call, no struct needed for a quick utility.

### Pointer Output Parameter (Optional)

```cpp
bool tryDivide(int num, int den, int* quotient, int* remainder) {
    if (den == 0) return false;
    if (quotient)  *quotient  = num / den;
    if (remainder) *remainder = num % den;
    return true;
}
```

The pointer form lets callers opt out of receiving an output they do not need.

## When to Prefer Output Parameters vs Return Values

| Scenario | Prefer |
|---|---|
| Single result | Return by value (NRVO/RVO elides the copy) |
| Two or three tightly related results | Output references or `std::tuple` / `std::pair` |
| Optional output | Pointer parameter or `std::optional<T>` (C++17) |
| Error + value | `std::expected<T, E>` (C++23) or bool + out param |

Modern C++ leans toward returning `std::pair`, `std::tuple`, or a named struct over output parameters for new APIs. Output parameters remain useful for performance-critical code and C interoperability.

## Worked Example: In-Place String Transform

```cpp
#include <string>
#include <algorithm>
#include <iostream>

// Modifies the string in-place via reference
void toUpperInPlace(std::string& s) {
    for (char& c : s) {
        c = static_cast<char>(std::toupper(static_cast<unsigned char>(c)));
    }
}

// Returns a new string (caller's string unchanged)
std::string toUpperCopy(const std::string& s) {
    std::string result = s;
    toUpperInPlace(result);
    return result;
}

int main() {
    std::string original = "hello";
    toUpperInPlace(original);
    std::cout << original << "\n";                   // HELLO

    std::string copy = toUpperCopy("world");
    std::cout << copy << "\n";                       // WORLD
}
```

Both patterns are common. In-place is more efficient when the caller already has the data. Returning a copy is safer when the original must not be touched.

## Common Pitfalls

- **Uninitialized output parameter.** If the function returns early on error without writing to the output reference, the caller reads garbage. Always initialize output variables or document that they are valid only on success.
- **Confusing in-out and pure-out parameters.** A function may both read *and* write through a reference (in-out). Document the contract clearly.
- **Overusing output parameters.** Returning a struct or `std::pair` is often cleaner than three output reference parameters.

> **Interview answer:** `swap` uses non-const references to alias the caller's variables, exchanging their values through a temporary. Output parameters use the same mechanism: the function writes to the caller's variable via a reference or pointer, enabling multiple return values without heap allocation.
