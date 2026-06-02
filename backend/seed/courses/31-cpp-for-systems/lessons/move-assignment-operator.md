# The Move Assignment Operator

The **move assignment operator** transfers resources from one *existing* object to another. Unlike the move constructor, the destination already owns resources that must be released before the transfer occurs.

## Signature

```cpp
ClassName& operator=(ClassName&& other) noexcept;
```

The return type is `ClassName&` — consistent with copy assignment — so chained assignments work: `a = b = std::move(c)`.

## The Three-Phase Pattern

Every move assignment operator follows the same sequence:

1. **Guard against self-assignment** (optional but safe).
2. **Release** the current object's resources.
3. **Steal** the source's resources and nullify the source.

```cpp
class DynamicArray {
    int*   data_;
    size_t size_;

public:
    DynamicArray& operator=(DynamicArray&& other) noexcept {
        if (this == &other) return *this;  // self-assignment guard

        delete[] data_;          // release existing resource

        data_       = other.data_;  // steal
        size_       = other.size_;
        other.data_ = nullptr;      // nullify source
        other.size_ = 0;

        return *this;
    }
};
```

## Self-Assignment with Move

Self-move-assignment (`a = std::move(a)`) is technically undefined behavior before C++17 for standard library types, but for user-defined types the guard `if (this == &other)` makes it safe. The guard is cheap and eliminates a subtle bug where you delete your own data before stealing it.

## Worked Example: Full RAII Class

```cpp
#include <iostream>
#include <utility>

class Buffer {
    char*  data_;
    size_t capacity_;

public:
    explicit Buffer(size_t cap)
        : data_(new char[cap]()), capacity_(cap) {
        std::cout << "Construct(" << cap << ")\n";
    }

    ~Buffer() {
        delete[] data_;
        std::cout << "Destroy\n";
    }

    // Move constructor
    Buffer(Buffer&& o) noexcept
        : data_(o.data_), capacity_(o.capacity_) {
        o.data_     = nullptr;
        o.capacity_ = 0;
        std::cout << "Move-construct\n";
    }

    // Move assignment
    Buffer& operator=(Buffer&& o) noexcept {
        if (this == &o) return *this;
        delete[] data_;
        data_       = o.data_;
        capacity_   = o.capacity_;
        o.data_     = nullptr;
        o.capacity_ = 0;
        std::cout << "Move-assign\n";
        return *this;
    }

    size_t capacity() const { return capacity_; }
};

int main() {
    Buffer a(1024);
    Buffer b(512);

    b = std::move(a);   // move assignment: b's old 512-byte block freed
                        // b now owns a's 1024-byte block
                        // a is left in valid empty state

    std::cout << "b.capacity() = " << b.capacity() << '\n'; // 1024
    std::cout << "a.capacity() = " << a.capacity() << '\n'; // 0
}
```

Expected output:
```
Construct(1024)
Construct(512)
Move-assign
b.capacity() = 1024
a.capacity() = 0
Destroy
Destroy
```

## Difference from Copy Assignment

| Aspect | Copy assignment | Move assignment |
|--------|----------------|-----------------|
| Source parameter | `const T&` | `T&&` |
| Allocates new memory? | Yes | No |
| Source state after | Unchanged | Valid but unspecified |
| Typical complexity | O(n) | O(1) |

## Copy-and-Swap vs Direct Move Assignment

The copy-and-swap idiom (using a local copy + `swap`) gives the strong exception guarantee but introduces an unnecessary copy when moving. For move assignment, prefer the direct approach:

```cpp
// Avoid for move assignment — copies just to swap
Buffer& operator=(Buffer o) noexcept { // 'o' is a copy or move
    std::swap(data_, o.data_);
    std::swap(capacity_, o.capacity_);
    return *this;  // o's destructor releases old data
}
```

This works but creates a temporary copy from an lvalue. Separate copy and move assignment operators are cleaner and more efficient.

## Common Pitfalls

- **Forgetting to release existing resources.** Without `delete[] data_` before the steal, the old allocation leaks.
- **Omitting self-assignment guard.** Without it you delete your own `data_` then try to read it from `other`.
- **Missing `noexcept`.** Standard containers fall back to copy during reallocation.

> **Interview answer:** The move assignment operator must first release the destination's existing resources, then steal the source's resource handles and nullify them, and finally return `*this`. Self-assignment guarding and `noexcept` are both essential for correctness and performance.
