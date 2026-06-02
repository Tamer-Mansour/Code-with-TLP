# Self-Assignment and the Copy-and-Swap Idiom

Self-assignment occurs when you write `x = x` or, more subtly, `a[i] = a[j]` when `i == j`. It looks harmless, but a naive copy assignment operator will destroy the object's data before reading it — producing a use-after-free bug.

## Why Self-Assignment Breaks Naive Assignment

```cpp
Buffer& Buffer::operator=(const Buffer& rhs) {
    delete[] data_;                          // (1) free old storage
    size_ = rhs.size_;                       // (2) if this == &rhs, rhs.size_ is now garbage
    data_ = new int[rhs.size_];             // (3) allocate
    std::copy(rhs.data_, ...);              // (4) copy from freed memory — UB!
    return *this;
}
```

When `this == &rhs`, step (1) frees the very memory that steps (2)–(4) then read. The result is undefined behaviour, typically a crash or silent data corruption.

## Fix 1: Identity Check

The simplest fix adds an early-exit guard:

```cpp
Buffer& Buffer::operator=(const Buffer& rhs) {
    if (this == &rhs) return *this;   // nothing to do
    delete[] data_;
    size_ = rhs.size_;
    data_ = new int[rhs.size_];
    std::copy(rhs.data_, rhs.data_ + rhs.size_, data_);
    return *this;
}
```

This works but still provides only the **basic exception-safety guarantee**: if `new` throws after `delete[]`, the object is left in a valid-but-unspecified state (data_ is dangling).

## Fix 2: Allocate-First Pattern

Allocate new memory before releasing the old:

```cpp
Buffer& Buffer::operator=(const Buffer& rhs) {
    if (this == &rhs) return *this;

    int* tmp = new int[rhs.size_];              // may throw — old state intact
    std::copy(rhs.data_, rhs.data_ + rhs.size_, tmp);
    delete[] data_;                             // safe to free now
    data_ = tmp;
    size_ = rhs.size_;
    return *this;
}
```

This gives the **strong exception-safety guarantee**: on failure, the object is unchanged.

## Fix 3: Copy-and-Swap Idiom (Preferred)

The copy-and-swap idiom elegantly handles both self-assignment and exception safety by leveraging the copy constructor and `swap`:

```cpp
class Buffer {
    int* data_;
    int  size_;
public:
    // Swap two Buffer objects (no allocation, no-throw)
    friend void swap(Buffer& a, Buffer& b) noexcept {
        using std::swap;
        swap(a.data_, b.data_);
        swap(a.size_, b.size_);
    }

    // Copy constructor (deep copy)
    Buffer(const Buffer& other)
        : size_(other.size_), data_(new int[other.size_])
    {
        std::copy(other.data_, other.data_ + other.size_, data_);
    }

    // Copy assignment via copy-and-swap
    Buffer& operator=(Buffer rhs) {   // rhs is a copy (by value)
        swap(*this, rhs);             // swap internals
        return *this;                 // old data_ deleted in rhs's destructor
    }

    ~Buffer() { delete[] data_; }
};
```

### How It Works

1. The parameter `rhs` is passed **by value** — invoking the copy constructor.
2. `swap` exchanges `this`'s internals with `rhs`'s internals (cheap pointer swap, no allocation).
3. When `rhs` goes out of scope at the closing `}`, its destructor frees what used to be `this`'s old data.

### Self-Assignment With Copy-and-Swap

```cpp
buf = buf;
// Step 1: copy constructor makes a full copy → tmp holds same data
// Step 2: swap exchanges this's data with tmp's copy
// Step 3: tmp's destructor frees the copy — object is unmodified
```

Self-assignment is handled automatically with no special check needed.

## Comparison of Approaches

| Approach | Self-assign safe | Exception safety | Extra allocation on self-assign |
|---|---|---|---|
| Identity check only | Yes | Basic | No |
| Allocate-first + guard | Yes | Strong | No |
| Copy-and-swap | Yes | Strong | Yes (one copy) |

The extra copy on self-assign is rarely a concern in practice; correctness and simplicity usually outweigh it.

## When to Use Each

- **Identity check**: acceptable for trivially cheap copies where you want to avoid the overhead.
- **Copy-and-swap**: preferred for any class that manages resources; it is impossible to get wrong and reuses the copy constructor you already tested.

> **Interview answer:** Self-assignment (`x = x`) is dangerous in a naive copy assignment operator because deleting the object's resource first destroys the very data you then try to copy. The copy-and-swap idiom avoids this by making a full copy first (via the copy constructor), then swapping, then letting the destructor clean up the old data — giving strong exception safety with no explicit self-assignment check.
