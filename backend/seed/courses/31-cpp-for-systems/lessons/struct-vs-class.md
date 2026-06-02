# struct vs class: What Is the Difference?

In C++, `struct` and `class` are almost identical. The single technical difference is the **default access specifier** and the **default inheritance mode**. Everything else — methods, constructors, destructors, templates, inheritance — works the same way.

## The One Rule That Differs

| Feature                  | `struct`    | `class`     |
|--------------------------|-------------|-------------|
| Default member access    | `public`    | `private`   |
| Default base-class access| `public`    | `private`   |

That is the complete formal difference. Both keywords create a fully capable C++ type.

```cpp
struct Point {
    int x;    // public by default
    int y;    // public by default
};

class Point2 {
    int x;    // private by default — callers cannot read this
    int y;
};
```

## When to Use Which (Convention)

Because the language gives you a free choice, the community has settled on a **style convention** that conveys intent:

- Use **`struct`** for plain data aggregates — types whose only job is to group related fields with no invariants to protect. Common in C-interop, protocol headers, and POD types.
- Use **`class`** for types with behaviour, invariants, or private state.

```cpp
// struct: plain aggregate, all fields public, no invariant
struct IpHeader {
    uint8_t  version_ihl;
    uint8_t  dscp_ecn;
    uint16_t total_length;
    uint16_t identification;
    uint16_t flags_fragment_offset;
    uint8_t  ttl;
    uint8_t  protocol;
    uint16_t checksum;
    uint32_t src_ip;
    uint32_t dst_ip;
};

// class: behaviour + invariant — length must not exceed capacity
class PacketBuffer {
private:
    uint8_t data_[65535] {};
    size_t  len_ = 0;
public:
    bool append(const uint8_t* src, size_t n);
    size_t length() const { return len_; }
};
```

## C Compatibility

C does not have `class`. When writing headers shared with C code (e.g., kernel modules, embedded firmware), use `struct`:

```c
// kernel_types.h — included by both C and C++ translation units
struct DeviceStatus {
    uint32_t error_code;
    uint32_t flags;
    char     name[32];
};
```

In a C++ translation unit this is a full C++ type (you can add methods, constructors, etc.). In a C translation unit it is a plain struct.

## Common Pitfall: Forgetting the Default Access in `class`

```cpp
class Vector3 {
    float x, y, z;       // private! caller can't touch these
};

Vector3 v;
v.x = 1.0f;             // ERROR: 'x' is private
```

New C++ programmers coming from C often assume `class` members are public by default. They are not. Either switch to `struct`, or add `public:` before the fields.

## POD and Trivial Types

A **Plain Old Data (POD)** type is compatible with `memcpy` and C memory layout. Both `struct` and `class` can be POD — the keyword doesn't matter; what matters is whether you add non-trivial constructors, virtual functions, or other features that disrupt the layout.

```cpp
static_assert(std::is_trivially_copyable<IpHeader>::value,
              "IpHeader must be memcpy-safe for DMA");
```

## Worked Example: Choosing the Right Keyword

```cpp
// struct — just data, used like a C struct
struct Registers {
    uint64_t rax, rbx, rcx, rdx;
    uint64_t rsp, rbp, rsi, rdi;
};

// class — encapsulates a thread context with an invariant
class Thread {
private:
    Registers saved_regs_ {};
    uint64_t  stack_top_   = 0;
    bool      running_     = false;
public:
    void save(const Registers& r)  { saved_regs_ = r; }
    const Registers& regs() const  { return saved_regs_; }
    void start();
    void stop();
};
```

`Registers` is a dumb aggregate — `struct` is perfect. `Thread` manages a lifecycle invariant — `class` signals that intent.

---

> **Interview answer:** "The only technical difference between `struct` and `class` in C++ is the default access level: `struct` defaults to `public`, `class` defaults to `private`. By convention, `struct` is used for plain data aggregates and `class` for types with behaviour and invariants."
