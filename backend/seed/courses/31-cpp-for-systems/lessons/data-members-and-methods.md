# Data Members and Member Functions

A class bundles two kinds of content: the **data** each object carries and the **functions** that operate on that data. Together they form a self-contained unit — a fundamental idea in systems design.

## Data Members

Data members declare the state an object holds. They are declared inside the class body exactly like ordinary variables, but they belong to every instance.

```cpp
class NetworkBuffer {
public:
    uint8_t  data[1500];   // payload bytes
    size_t   length;       // current number of valid bytes
    uint32_t checksum;     // CRC computed over data
};
```

Every `NetworkBuffer` object gets its own 1500-byte array, its own `length`, and its own `checksum`. Changing one object's `length` never touches another object's `length`.

### Initialising Data Members

Prefer **in-class initialisers** (C++11 and later) to guarantee a known state:

```cpp
class NetworkBuffer {
public:
    uint8_t  data[1500] {};   // zero-initialised
    size_t   length   = 0;
    uint32_t checksum = 0;
};
```

Without initialisation, members of non-trivial objects are indeterminate — a frequent source of undefined behaviour in systems code.

## Member Functions (Methods)

Member functions operate on the object they are called on. They have implicit access to all data members via the hidden `this` pointer (covered in a later lesson).

```cpp
class NetworkBuffer {
public:
    uint8_t  data[1500] {};
    size_t   length = 0;

    // Write bytes into the buffer
    bool write(const uint8_t* src, size_t n) {
        if (n > sizeof(data)) return false;
        std::memcpy(data, src, n);
        length = n;
        return true;
    }

    // Read how full the buffer is
    size_t used() const { return length; }

    // Clear the buffer
    void clear() { length = 0; }
};
```

### Inline vs Out-of-Line Definitions

For readability and separate compilation, define methods **outside** the class using the scope-resolution operator `::`:

```cpp
// Header: NetworkBuffer.hpp
class NetworkBuffer {
public:
    bool write(const uint8_t* src, size_t n);
    size_t used() const;
};

// Source: NetworkBuffer.cpp
bool NetworkBuffer::write(const uint8_t* src, size_t n) {
    if (n > sizeof(data)) return false;
    std::memcpy(data, src, n);
    length = n;
    return true;
}
```

Methods defined *inside* the class body are implicitly `inline` — the compiler may expand them at the call site, which is desirable for tiny accessors.

## Accessor and Mutator Pattern

In real codebases, data members are often `private`, and access is channelled through get/set methods (accessors and mutators). This lets you:

- Validate inputs before storing them.
- Change internal representation without breaking callers.
- Enforce invariants (e.g., `length` never exceeds `sizeof(data)`).

```cpp
class NetworkBuffer {
private:
    size_t length_ = 0;

public:
    size_t length() const { return length_; }       // accessor
    void   setLength(size_t n) {                    // mutator with guard
        if (n <= 1500) length_ = n;
    }
};
```

## Common Pitfalls

| Pitfall | Consequence | Fix |
|---------|-------------|-----|
| Uninitialised data members | Undefined behaviour on read | Use in-class initialisers |
| Non-`const` accessor | Prevents use with `const` objects | Mark read-only methods `const` |
| Fat method bodies in headers | Long recompilation chains | Move large bodies to `.cpp` |
| Public data + no invariant | State can become inconsistent | Prefer private data + mutators |

## Worked Example: Ring Buffer

```cpp
class RingBuffer {
private:
    static constexpr size_t CAP = 256;
    uint8_t buf_[CAP] {};
    size_t  head_ = 0, tail_ = 0, count_ = 0;

public:
    bool push(uint8_t byte) {
        if (count_ == CAP) return false;   // full
        buf_[tail_] = byte;
        tail_ = (tail_ + 1) % CAP;
        ++count_;
        return true;
    }

    bool pop(uint8_t& out) {
        if (count_ == 0) return false;     // empty
        out  = buf_[head_];
        head_ = (head_ + 1) % CAP;
        --count_;
        return true;
    }

    size_t size() const { return count_; }
};
```

The data (`buf_`, `head_`, `tail_`, `count_`) is private and can only be accessed through the three public methods — a textbook encapsulation that prevents callers from corrupting the ring invariant.

---

> **Interview answer:** "Data members store per-object state; member functions operate on that state through the implicit `this` pointer. Hiding data as `private` and exposing it through methods lets you maintain class invariants and change internal representation without breaking callers."
