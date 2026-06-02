# The Rule of Zero and Why It Is Preferred

The **Rule of Zero** says: if your class does not directly manage a resource, do not define any of the five special member functions. Let the compiler generate them — they will be correct, efficient, and automatically updated when you add members.

## The Principle

```cpp
// Rule of Zero in practice — no special members defined
class Server {
    std::string              host_;
    std::vector<Connection>  connections_;
    std::unique_ptr<Logger>  logger_;
};
```

Every member is a well-behaved RAII wrapper. The compiler-generated destructor destroys members in reverse order. The compiler-generated move constructor moves each member. The compiler-generated copy constructor copies each member (or is deleted if any member is non-copyable, like `unique_ptr`).

No boilerplate. No bugs. No maintenance burden.

## Rule of Zero vs Rule of Five

| Rule | When | Code written |
|------|------|-------------|
| Rule of Five | Class directly owns a raw resource | All 5 special members |
| Rule of Zero | Class composes RAII members | 0 special members |

The design philosophy: **push resource ownership into a dedicated type** (your own RAII wrapper or a standard type like `unique_ptr`, `shared_ptr`, `vector`, `string`) and then compose those types. The composer needs zero special members.

## Worked Example: Before and After

### Before — Rule of Five on every class (wrong approach)

```cpp
class NetworkBuffer {
    char*  data_;
    size_t size_;
public:
    NetworkBuffer(size_t n) : data_(new char[n]), size_(n) {}
    ~NetworkBuffer()                              { delete[] data_; }
    NetworkBuffer(const NetworkBuffer& o)         : data_(new char[o.size_]), size_(o.size_) {
        std::copy(o.data_, o.data_ + size_, data_);
    }
    NetworkBuffer& operator=(const NetworkBuffer&); // ...
    NetworkBuffer(NetworkBuffer&&) noexcept;         // ...
    NetworkBuffer& operator=(NetworkBuffer&&) noexcept; // ...
};

class Packet {
    NetworkBuffer buffer_;  // still must duplicate all five for Packet!
    uint32_t      seq_;
};
```

### After — Rule of Zero via composition

```cpp
// The one class that owns the raw resource
class RawBuffer {
    char*  data_;
    size_t size_;
public:
    explicit RawBuffer(size_t n) : data_(new char[n]()), size_(n) {}
    ~RawBuffer()                            { delete[] data_; }
    RawBuffer(const RawBuffer&)             = delete;   // non-copyable
    RawBuffer& operator=(const RawBuffer&) = delete;
    RawBuffer(RawBuffer&& o) noexcept      : data_(o.data_), size_(o.size_) {
        o.data_ = nullptr; o.size_ = 0;
    }
    RawBuffer& operator=(RawBuffer&&) noexcept; // ...
};

// Every other class composes — zero special members needed
class Packet {
    RawBuffer buffer_;   // compiler-generated move delegates to RawBuffer::move
    uint32_t  seq_;
    // No destructor, no copy/move defined
};

class Connection {
    Packet    outbox_;
    Packet    inbox_;
    // Still zero special members
};
```

## Relying on Standard RAII Types

In practice, you rarely need to write `RawBuffer` from scratch:

```cpp
class Packet {
    std::vector<char> buffer_;  // std::vector handles all five
    uint32_t          seq_ = 0;
    // Rule of Zero — done
};
```

`std::vector`, `std::string`, `std::unique_ptr`, and `std::shared_ptr` are already correct RAII types. Compose them freely.

## When Rule of Zero Does Not Apply

The Rule of Zero fails when:
- You must interface with C APIs that use raw pointers and handle types.
- You need custom copy/move semantics (e.g., a copy of a socket should duplicate the file descriptor via `dup(2)`, not copy the integer).
- Performance requires a specific memory layout not achievable with standard containers.

In those cases, write **one** focused RAII class that applies the Rule of Five, then compose it everywhere else with the Rule of Zero.

## Common Pitfall: User-Declared Destructor Breaks the Rule

```cpp
class Component {
    std::vector<int> data_;
public:
    ~Component() {
        std::cout << "Component destroyed\n"; // logging
    }
    // Move operations are now DELETED by the compiler!
};

std::vector<Component> components;
components.push_back(Component{}); // ERROR or unexpected copy
```

Adding a destructor (even a trivial one) suppresses the implicit move operations. Fix: either remove the destructor or explicitly `= default` all five.

> **Interview answer:** The Rule of Zero says a class should define none of the five special members when it only composes RAII members, letting the compiler generate correct, maintenance-free implementations. The pattern is to isolate raw-resource ownership in a single dedicated RAII type (Rule of Five), then compose those types everywhere else (Rule of Zero).
