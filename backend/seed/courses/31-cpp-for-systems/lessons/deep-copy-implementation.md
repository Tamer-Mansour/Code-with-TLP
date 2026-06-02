# Implementing a Deep-Copying Resource Class

Theory is only half the battle. This lesson walks through building a complete, correct, deep-copying class from scratch — a fixed-capacity integer array — applying every principle from this module.

## Requirements

- Owns a heap-allocated `int` array.
- Supports copy construction and copy assignment (deep copies).
- Destructor frees the allocation.
- `swap` is provided for the copy-and-swap idiom.
- Strong exception-safety guarantee on copy assignment.

## The Complete Implementation

```cpp
#include <algorithm>   // std::copy, std::swap
#include <stdexcept>   // std::out_of_range
#include <cstddef>     // std::size_t

class IntArray {
    int*        data_;
    std::size_t size_;

    // Private helper: allocate and copy from [src, src+n)
    static int* alloc_copy(const int* src, std::size_t n) {
        int* p = new int[n];               // throws std::bad_alloc on failure
        std::copy(src, src + n, p);
        return p;
    }

public:
    // ---- Construction ----

    explicit IntArray(std::size_t n, int fill = 0)
        : size_(n), data_(new int[n])
    {
        std::fill(data_, data_ + size_, fill);
    }

    // ---- Rule of Three ----

    // 1. Destructor
    ~IntArray() {
        delete[] data_;
    }

    // 2. Copy constructor
    IntArray(const IntArray& other)
        : size_(other.size_),
          data_(alloc_copy(other.data_, other.size_))
    {}

    // 3. Copy assignment (copy-and-swap)
    IntArray& operator=(IntArray rhs) {   // rhs constructed by copy ctor
        swap(*this, rhs);                 // cheap pointer exchange
        return *this;
        // rhs destructor frees old data_
    }

    // ---- Swap (must be no-throw) ----

    friend void swap(IntArray& a, IntArray& b) noexcept {
        using std::swap;
        swap(a.data_, b.data_);
        swap(a.size_, b.size_);
    }

    // ---- Element access ----

    int& operator[](std::size_t i) {
        if (i >= size_) throw std::out_of_range("IntArray index out of range");
        return data_[i];
    }

    const int& operator[](std::size_t i) const {
        if (i >= size_) throw std::out_of_range("IntArray index out of range");
        return data_[i];
    }

    std::size_t size() const noexcept { return size_; }
};
```

## Tracing Through a Copy Assignment

```cpp
IntArray a(3, 1);    // data_ -> [1,1,1]
IntArray b(2, 9);    // data_ -> [9,9]

b = a;
// Step 1: `a` is passed by value to operator=
//         copy constructor runs: rhs.data_ -> [1,1,1] (new allocation)
// Step 2: swap(b, rhs)
//         b.data_ now points to [1,1,1]
//         rhs.data_ now points to [9,9]
// Step 3: rhs goes out of scope → rhs destructor deletes [9,9]
// Result: b.data_ -> [1,1,1], independent of a
```

## Exception Safety Analysis

| Operation | Guarantee | Reason |
|---|---|---|
| Constructor | Strong | `new` throws before any state is set |
| Copy constructor | Strong | `alloc_copy` throws before `this` is modified |
| Copy assignment | Strong | Copy happens in `rhs` before any swap; old state released only in `rhs` destructor |
| Destructor | No-throw | `delete[]` never throws |
| `swap` | No-throw | Only pointer swaps, declared `noexcept` |

## Self-Assignment Trace

```cpp
b = b;
// Step 1: copy constructor makes a full copy of b → rhs
// Step 2: swap(b, rhs) — b holds the new copy, rhs holds old ptrs
// Step 3: rhs destructor deletes the "old" data (which is identical content)
// Result: b is functionally unchanged, no aliasing, no double-free
```

No explicit `if (this == &rhs)` check is needed.

## Testing the Class

```cpp
int main() {
    IntArray x(4, 7);
    IntArray y = x;            // copy constructor
    y[0] = 42;
    // x[0] is still 7 — independent deep copy

    IntArray z(1, 0);
    z = x;                     // copy assignment
    z[1] = 99;
    // x[1] is still 7 — independent deep copy

    // All destructors fire cleanly — no double free
}
```

## Key Takeaways

- Use a static helper (`alloc_copy`) to centralise allocation logic.
- Pass by value in `operator=` to invoke the copy constructor automatically — this is copy-and-swap.
- Mark `swap` as `noexcept` so it can be used in move operations and standard containers safely.
- The copy assignment strong guarantee falls out naturally from the idiom without extra `try`/`catch` blocks.

> **Interview answer:** A deep-copying resource class needs a destructor that frees the resource, a copy constructor that allocates fresh storage and copies the contents, and a copy assignment operator — ideally implemented via copy-and-swap — that is self-assignment-safe and provides the strong exception-safety guarantee.
