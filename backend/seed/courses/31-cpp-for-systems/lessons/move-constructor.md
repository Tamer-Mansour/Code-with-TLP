# The Move Constructor: Stealing Resources

A **move constructor** transfers ownership of resources from one object to another without allocating or copying memory. For heap-heavy objects like strings, vectors, and file handles, this can reduce an O(n) copy to an O(1) pointer swap.

## Why Move Constructors Exist

Consider a class that owns a heap allocation:

```cpp
class DynamicArray {
    int*   data_;
    size_t size_;
public:
    DynamicArray(size_t n) : data_(new int[n]), size_(n) {}
    ~DynamicArray() { delete[] data_; }

    // Copy constructor — O(n)
    DynamicArray(const DynamicArray& other)
        : data_(new int[other.size_]), size_(other.size_)
    {
        std::copy(other.data_, other.data_ + size_, data_);
    }
};
```

When you return a `DynamicArray` from a function or push it into a container, the copy constructor allocates fresh memory and copies every element. If the source is a temporary, that copy is immediately thrown away — pure waste.

## Writing the Move Constructor

```cpp
// Move constructor — O(1)
DynamicArray(DynamicArray&& other) noexcept
    : data_(other.data_),   // steal the pointer
      size_(other.size_)
{
    other.data_ = nullptr;  // leave source in valid state
    other.size_ = 0;        //   so its destructor is safe
}
```

The three steps are always the same:
1. **Pilfer** the source's resources into `this`.
2. **Nullify** the source's resource handles.
3. Ensure the source's **destructor is safe** to run (it will run eventually).

## The noexcept Guarantee

Mark move constructors `noexcept` whenever possible. The standard library (e.g., `std::vector`) checks `std::is_nothrow_move_constructible` before deciding whether to move or copy elements during a reallocation. Without `noexcept`, `std::vector::push_back` will copy instead of move to maintain the strong exception guarantee.

```cpp
DynamicArray(DynamicArray&& other) noexcept { /* ... */ }
//                                 ^^^^^^^^ critical
```

## Worked Example: Full Class

```cpp
#include <algorithm>
#include <utility>

class DynamicArray {
    int*   data_;
    size_t size_;

public:
    explicit DynamicArray(size_t n)
        : data_(new int[n]()), size_(n) {}

    ~DynamicArray() { delete[] data_; }

    // Copy constructor
    DynamicArray(const DynamicArray& o)
        : data_(new int[o.size_]), size_(o.size_) {
        std::copy(o.data_, o.data_ + size_, data_);
    }

    // Move constructor — steals resources
    DynamicArray(DynamicArray&& o) noexcept
        : data_(o.data_), size_(o.size_) {
        o.data_ = nullptr;
        o.size_ = 0;
    }

    size_t size() const { return size_; }
    int& operator[](size_t i) { return data_[i]; }
};

DynamicArray make_array(size_t n) {
    DynamicArray a(n);
    for (size_t i = 0; i < n; ++i) a[i] = static_cast<int>(i);
    return a; // NRVO or move — no copy
}

int main() {
    DynamicArray arr = make_array(1'000'000); // O(1), no heap copy
    DynamicArray arr2 = std::move(arr);       // explicit move
    // arr.size() == 0 now
}
```

## When Is the Move Constructor Called?

- Initializing from a **prvalue**: `DynamicArray b = make_array(10);`
- Initializing from an **xvalue**: `DynamicArray c = std::move(arr);`
- Return value optimization falls back to move when NRVO cannot apply.
- `std::vector` reallocations (only if `noexcept`).

## Common Pitfalls

- **Forgetting to null the source pointer.** The source's destructor will run and call `delete[]` on a pointer now owned by `this` — double free.
- **Omitting `noexcept`.** The standard library silently falls back to copies.
- **Leaving the source in an invalid state.** The moved-from object must be destructible and assignable; other operations on it have unspecified (but valid) behavior.

```cpp
// BAD — double free
DynamicArray(DynamicArray&& o) noexcept
    : data_(o.data_), size_(o.size_) {
    // forgot: o.data_ = nullptr;
}
```

> **Interview answer:** A move constructor takes an rvalue reference, pilfers the source's resource handles (pointers, file descriptors) into `this`, and nullifies them in the source so the source's destructor is a no-op. It should be marked `noexcept` so standard containers can prefer it over copies during reallocation.
