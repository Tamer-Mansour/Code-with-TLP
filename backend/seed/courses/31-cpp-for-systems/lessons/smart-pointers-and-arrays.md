# Smart Pointers with Arrays and Incomplete Types

Smart pointers are not limited to single objects. They handle dynamic arrays, and they work with types that are only forward-declared at the point of the smart pointer's definition — a technique critical for the Pimpl idiom and other compile-time optimization patterns.

## unique_ptr with Arrays

`unique_ptr<T[]>` manages a heap-allocated array and calls `delete[]` (not `delete`) in its destructor:

```cpp
auto buf = std::make_unique<int[]>(1024);
buf[0] = 42;
buf[1] = 7;
// delete[] called automatically
```

Key differences from `unique_ptr<T>`:

- Uses `operator[]` for element access; `operator*` and `operator->` are deleted.
- Calls `delete[]` on destruction.
- Does not support `unique_ptr<T[]>` of a derived type — no polymorphism.

```cpp
auto arr = std::make_unique<Widget[]>(10);
// arr[3].method();   // OK
// *arr              // ERROR: operator* not defined for array form
```

## shared_ptr with Arrays (C++17)

`shared_ptr<T[]>` was added in C++17:

```cpp
auto arr = std::make_shared<int[]>(64);
arr[0] = 1;
```

Before C++17, `shared_ptr<T>` could hold an array pointer with a custom deleter, but `operator[]` was unavailable. C++17 adds the specialization properly.

## Prefer std::vector and std::array

For most use cases, prefer standard containers over smart-pointer arrays:

```cpp
// Prefer this:
std::vector<int> v(1024);

// Over this:
auto v = std::make_unique<int[]>(1024);
```

`vector` provides size tracking, bounds-checked `.at()`, range-based for, and growth. Smart pointer arrays are raw memory — use them when you need to own a buffer returned from a C API or when the allocation must be contiguous with no overhead from a vector's size/capacity tracking.

## Incomplete Types and unique_ptr

`unique_ptr` works with incomplete types (forward declarations) **as long as the destructor is defined where the complete type is visible**. This is the foundation of the Pimpl idiom:

```cpp
// widget.h
class Widget {
public:
    Widget();
    ~Widget();            // declared but NOT defined in the header
    void doWork();
private:
    struct Impl;
    std::unique_ptr<Impl> pImpl_;   // Impl is incomplete here — OK
};
```

```cpp
// widget.cpp
#include "widget.h"

struct Widget::Impl {
    int value = 0;
    std::string name;
};

Widget::Widget() : pImpl_(std::make_unique<Impl>()) {}
Widget::~Widget() = default;   // Impl is complete here — unique_ptr destructor OK
void Widget::doWork() { pImpl_->value++; }
```

If you declare `~Widget()` as `= default` in the header, the compiler generates the destructor there, where `Impl` is incomplete, and the compiler cannot call `delete` on an incomplete type. Moving the definition to the `.cpp` file fixes this.

## shared_ptr with Incomplete Types

`shared_ptr` is more permissive with incomplete types than `unique_ptr` because it stores the deleter in the control block at the point of construction (where the type is complete), not in the `shared_ptr` type itself:

```cpp
// header — Impl is incomplete
class Widget {
    std::shared_ptr<Impl> pImpl_;  // OK — deleter stored at construction site
};
```

This means `shared_ptr<Impl>` can be used without defining the destructor in the header. This is convenient but slightly obscures the ownership model, which is why `unique_ptr` remains preferred for Pimpl.

## Summary Table

| Feature | `unique_ptr<T>` | `unique_ptr<T[]>` | `shared_ptr<T>` |
|---|---|---|---|
| Single object | Yes | No | Yes |
| Array with `[]` | No | Yes | Yes (C++17) |
| Custom deleter | Yes | Yes | Yes |
| Incomplete type | Yes (destructor in .cpp) | Yes | Yes (more permissive) |
| Polymorphism | Yes | No | Yes |

## Interview Answer

**"How does unique_ptr handle arrays differently from single objects?"**

> `unique_ptr<T[]>` calls `delete[]` instead of `delete` and exposes `operator[]` instead of `operator*`/`operator->`. It is the safe RAII wrapper for a heap-allocated buffer, though for most code `std::vector` is preferable because it also tracks size and supports growth.
