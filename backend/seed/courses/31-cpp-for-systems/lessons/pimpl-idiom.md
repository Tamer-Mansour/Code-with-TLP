# The Pimpl Idiom and Compilation Firewalls

**Pimpl** (Pointer to IMPLementation, also called "compilation firewall" or "Cheshire Cat") is a technique that moves all private members — data and helper functions — into a forward-declared nested struct defined only in the `.cpp`. Callers include the header without pulling in any of the implementation's dependencies.

## The Problem It Solves

Suppose your class uses a platform SDK:

```cpp
// bad_widget.h
#include <windows.h>   // drags in 10 MB of Win32 headers into EVERY caller
#include <d3d12.h>

class Widget {
    HWND   hwnd_;      // private, but its type forces callers to know Windows
    ID3D12Device* device_;
public:
    void render();
};
```

Any change to the private section requires recompiling every `.cpp` that includes this header. On a large codebase that is minutes of build time for a one-line private change.

## The Pimpl Pattern

`widget.h` — the public surface:

```cpp
#pragma once
#include <memory>

class Widget {
public:
    Widget();
    ~Widget();               // must be defined in .cpp where Impl is complete

    Widget(Widget&&) noexcept;
    Widget& operator=(Widget&&) noexcept;

    // No copy: Impl is non-copyable by design
    Widget(const Widget&)            = delete;
    Widget& operator=(const Widget&) = delete;

    void render();
    void resize(int w, int h);

private:
    struct Impl;                    // forward declaration — size unknown to callers
    std::unique_ptr<Impl> impl_;    // pointer = fixed size, no platform header needed
};
```

`widget.cpp` — everything heavy lives here:

```cpp
#include "widget.h"
#include <windows.h>    // ONLY compiled in this one TU
#include <d3d12.h>

struct Widget::Impl {
    HWND          hwnd   = nullptr;
    ID3D12Device* device = nullptr;
    int width = 800, height = 600;

    Impl() { /* create window, init D3D12 */ }
    ~Impl() { /* release D3D12 resources, destroy window */ }
};

// All special members must be defined here (Impl is complete)
Widget::Widget()  : impl_(std::make_unique<Impl>()) {}
Widget::~Widget() = default;   // unique_ptr destructor runs ~Impl here
Widget::Widget(Widget&&) noexcept            = default;
Widget& Widget::operator=(Widget&&) noexcept = default;

void Widget::render()        { /* impl_->device->DrawInstanced(...) */ }
void Widget::resize(int w, int h) { impl_->width = w; impl_->height = h; }
```

## What Pimpl Provides

| Benefit | Explanation |
|---|---|
| Compilation firewall | Private changes never trigger header-consumer recompilation |
| ABI stability | Adding private members does not change `sizeof(Widget)` |
| Platform isolation | Heavy platform headers stay in one `.cpp` |
| Testability | `Impl` can be swapped or mocked per test binary |

## The Cost

- **Heap allocation** — each `Widget` does a `new Impl`. For small, frequently created objects this can be significant.
- **Indirection** — every method call dereferences `impl_`. Usually negligible; can matter in tight loops.
- **More boilerplate** — move operations and destructor must be explicitly defined in the `.cpp`.

## Avoiding the Heap: Stack-Allocated Pimpl

For performance-critical code, an aligned storage buffer can host `Impl` without heap:

```cpp
// header
class FastWidget {
    alignas(8) unsigned char storage_[64]; // size must be known — fragile
public:
    FastWidget();
    ~FastWidget();
};
```

This trades heap for a fixed-size constraint: `sizeof(Impl)` must not exceed `storage_`. It is brittle and rarely worth the complexity outside embedded / real-time contexts.

## When to Use Pimpl

- Libraries with **stable ABIs** (a private member change would break binary compatibility without Pimpl).
- Headers that otherwise pull in **large platform SDKs**.
- Classes where **build time** is a measurable team pain point.
- **Not** for every class — simple internal utilities do not need it.

## Interview Answer

> "Pimpl moves all private members into a forward-declared struct defined only in the `.cpp`. The header holds only a `unique_ptr<Impl>`. This creates a compilation firewall (private changes don't recompile callers) and stabilizes the ABI, at the cost of one heap allocation and one pointer indirection per object."
