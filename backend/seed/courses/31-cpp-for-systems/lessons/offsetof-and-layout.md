# offsetof and Standard-Layout Types

`offsetof` is a C macro (inherited by C++) that tells you the byte offset of a member within a struct. It is the authoritative, portable way to inspect struct layout at compile time — and it is only defined for a specific class of types called **standard-layout types**.

## `offsetof` — Syntax and Use

```cpp
#include <cstddef>   // or <stddef.h>

struct Point {
    float x;    // offset 0
    float y;    // offset 4
    float z;    // offset 8
};

static_assert(offsetof(Point, x) == 0);
static_assert(offsetof(Point, y) == 4);
static_assert(offsetof(Point, z) == 8);
static_assert(sizeof(Point)      == 12);
```

`offsetof(T, member)` expands to a `std::size_t` constant expression giving the number of bytes from the start of an object of type `T` to its member `member`.

### Practical Uses

- **Serialization**: know exactly where each field sits in a buffer.
- **Generic field access via pointer arithmetic**: used extensively in the Linux kernel (`container_of` macro).
- **Compile-time layout assertions**: catch ABI regressions in CI.

```c
// Linux kernel's container_of — recover outer struct from member pointer
#define container_of(ptr, type, member) \
    ((type *)((char *)(ptr) - offsetof(type, member)))

// Example: given a pointer to the 'list' field, get the enclosing Node*
struct Node {
    int   value;
    struct list_head list;   // embedded list link
};

struct list_head* lh = get_next();
struct Node* node = container_of(lh, struct Node, list);
```

## Standard-Layout Types

The C++ standard only guarantees `offsetof` yields correct results for **standard-layout** types. A type is standard-layout if it has no:

- Virtual functions or virtual base classes
- Non-static data members of non-standard-layout type
- Multiple base classes with non-static data members
- Base class of the same type as the first member (no hidden padding conflict)

And additionally:

- All non-static data members have the same access control (all `public`, or all `private`, etc.)
- No non-standard-layout base classes

```cpp
struct StandardLayout {
    int   a;
    float b;
    char  c;
};
// offsetof is well-defined here

struct NotStandardLayout {
    virtual void foo();   // virtual function → not standard-layout
    int a;
};
// offsetof(NotStandardLayout, a) is undefined behavior
```

You can check at compile time:

```cpp
#include <type_traits>
static_assert(std::is_standard_layout_v<StandardLayout>);
static_assert(!std::is_standard_layout_v<NotStandardLayout>);
```

## Related Type Traits

| Trait | Meaning |
|---|---|
| `std::is_standard_layout_v<T>` | Guarantees `offsetof` is valid |
| `std::is_trivially_copyable_v<T>` | Safe to copy with `memcpy` |
| `std::is_pod_v<T>` (deprecated C++20) | Both trivial and standard-layout |
| `std::is_trivial_v<T>` | Trivial default constructor + trivially copyable |

**Standard-layout** is the key property for `offsetof`. **Trivially copyable** is the key property for `memcpy`. In systems code you often want both — sometimes called "trivial standard-layout" or informally "POD-like".

## Layout Assertions as ABI Guards

Use `offsetof` assertions in headers that cross ABI boundaries:

```cpp
struct DeviceRegisters {
    uint32_t control;    // must be at byte 0
    uint32_t status;     // must be at byte 4
    uint64_t address;    // must be at byte 8
};

static_assert(offsetof(DeviceRegisters, control) == 0);
static_assert(offsetof(DeviceRegisters, status)  == 4);
static_assert(offsetof(DeviceRegisters, address) == 8);
static_assert(sizeof(DeviceRegisters)            == 16);
```

If a developer adds a new member in the wrong position, the build breaks immediately rather than corrupting hardware registers silently.

## Common Mistakes

```cpp
struct WithBitField {
    unsigned int flag : 1;
    unsigned int val  : 7;
};
// offsetof(WithBitField, flag) is ill-formed — bit-fields have no address
```

Bit-field members cannot be operands of `offsetof` because they have no distinct byte address.

> **Interview answer:** `offsetof(T, member)` returns the byte offset of a member within a standard-layout struct as a compile-time constant. It is used for serialization, the `container_of` pattern, and ABI regression checks. It is only well-defined for standard-layout types — those without virtual functions, mixed access control, or non-standard-layout members.
