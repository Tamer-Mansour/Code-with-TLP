# Move Semantics and Perfect Forwarding in Modern C++

Move semantics, introduced in C++11, are the single most important performance feature in modern C++. Understanding them precisely — not just "move is faster than copy" — is essential for writing efficient systems code.

## Value Categories: lvalue, rvalue, xvalue

Every C++ expression belongs to a value category:

| Category | Meaning | Example |
|---|---|---|
| **lvalue** | Has a persistent address; can appear on left of `=` | `x`, `obj.member`, `*ptr` |
| **rvalue** | Temporary; no persistent address | `42`, `x + y`, `std::string("hi")` |
| **xvalue** | "eXpiring" — lvalue cast to rvalue reference | `std::move(x)` |

The compiler uses value category to decide whether to call the copy constructor or the move constructor.

## What `std::move` Actually Does

`std::move` is a cast, not a function that moves anything:

```cpp
template<typename T>
std::remove_reference_t<T>&& move(T&& t) noexcept {
    return static_cast<std::remove_reference_t<T>&&>(t);
}
```

It converts an lvalue to an rvalue reference, giving the compiler permission to call the move constructor instead of the copy constructor. The actual resource transfer happens in the constructor body.

## The Move Constructor Pattern

```cpp
class Buffer {
    char* data_;
    size_t size_;
public:
    // Move constructor: steal resources from other
    Buffer(Buffer&& other) noexcept
        : data_(other.data_), size_(other.size_) {
        other.data_ = nullptr;  // leave source in valid but empty state
        other.size_ = 0;
    }
};
```

After the move, `other` is in a **valid but unspecified state** — safe to destroy, unsafe to use.

## Perfect Forwarding

Perfect forwarding solves the problem of writing generic wrappers that pass arguments to another function without paying copy costs:

```cpp
template<typename T, typename... Args>
std::unique_ptr<T> make(Args&&... args) {
    return std::unique_ptr<T>(new T(std::forward<Args>(args)...));
}
```

`std::forward<Args>(args)` preserves the value category of each argument: if the caller passed an lvalue, it arrives as an lvalue; if an rvalue, as an rvalue. Without `std::forward`, the named parameter `args` inside the function would always be an lvalue, defeating the purpose.

## Key Corrections

A common myth is that `std::shared_ptr` is a drop-in replacement for raw pointers everywhere. It is not. The [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines) rule **R.21** states:

> Prefer `unique_ptr` over `shared_ptr` unless you need to share ownership.

`unique_ptr` has exactly zero overhead compared to a raw owning pointer — its move constructor is a single pointer assignment. `shared_ptr` incurs an atomic reference count increment on every copy.

## Practical Rules

1. **Rule of Five:** if you define any of destructor, copy constructor, copy assignment, move constructor, or move assignment, define or explicitly delete all five.
2. **Mark move operations `noexcept`:** `std::vector` and other containers will only use your move constructor during reallocation if it is `noexcept`. Without the annotation, they fall back to copying.
3. **Prefer `make_unique` and `make_shared`:** avoids separate heap allocations for the control block.

## Further Reading

- *A Tour of C++* by Bjarne Stroustrup: [https://isocpp.org/files/papers/5-Tour-Util.pdf](https://isocpp.org/files/papers/5-Tour-Util.pdf) — Chapter on move semantics and utilities.
- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines), section R (Resource Management).
