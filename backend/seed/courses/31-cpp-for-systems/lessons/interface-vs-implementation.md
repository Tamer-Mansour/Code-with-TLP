# Separating Interface from Implementation

In C++ the most tangible form of the interface/implementation split is the **header file (.h) / translation unit (.cpp) pair**. The header declares *what* the class provides; the `.cpp` defines *how* it does it. This physical separation is a cornerstone of scalable C++ system design.

## Why It Matters

- **Compile-time isolation** — callers recompile only when the header changes, not when the implementation changes.
- **Binary compatibility** — ship a prebuilt `.so`/`.dll` and a header; clients do not need your source.
- **Parallel builds** — each `.cpp` is an independent translation unit; ten engineers can work on ten `.cpp` files simultaneously without stepping on each other.
- **Information hiding** — implementation details (helper methods, internal types) stay out of the header.

## The Basic Pattern

`timer.h` — the public contract:

```cpp
#pragma once
#include <cstdint>

class Timer {
public:
    Timer();
    ~Timer();

    void     start();
    void     stop();
    uint64_t elapsed_us() const;
    bool     is_running() const;

private:
    struct Impl;          // forward declaration only — clients see nothing
    Impl* impl_;          // opaque pointer (Pimpl variant)
};
```

`timer.cpp` — the private machinery:

```cpp
#include "timer.h"
#include <chrono>

struct Timer::Impl {
    std::chrono::steady_clock::time_point start_point;
    uint64_t accumulated_us = 0;
    bool running = false;
};

Timer::Timer()  : impl_(new Impl{}) {}
Timer::~Timer() { delete impl_; }

void Timer::start() {
    if (impl_->running) return;
    impl_->start_point = std::chrono::steady_clock::now();
    impl_->running = true;
}

void Timer::stop() {
    if (!impl_->running) return;
    auto now = std::chrono::steady_clock::now();
    impl_->accumulated_us +=
        std::chrono::duration_cast<std::chrono::microseconds>(
            now - impl_->start_point).count();
    impl_->running = false;
}

uint64_t Timer::elapsed_us() const { return impl_->accumulated_us; }
bool     Timer::is_running() const { return impl_->running; }
```

Callers include only `timer.h`. Nothing about `std::chrono` leaks into their compilation.

## What Belongs in the Header

| Goes in `.h` | Goes in `.cpp` |
|---|---|
| Class declaration | Method bodies |
| Public method signatures | Private helper functions |
| Public type aliases | `#include` of heavy headers |
| Inline / template definitions | Static local data |
| Forward declarations | Platform-specific code |

## Inline Functions: When to Break the Rule

Small, hot functions (trivial getters, one-liners) are legitimate candidates for definition in the header so the compiler can inline them:

```cpp
// header — acceptable inline
class Packet {
public:
    uint16_t length() const { return len_; }
private:
    uint16_t len_;
    uint8_t  data_[1500];
};
```

Reserve inline definitions for functions where the inlining benefit clearly outweighs the recompilation cost.

## Abstract Interfaces (Pure-Virtual)

For polymorphic designs, the interface is an abstract base class with no data members:

```cpp
// ilogger.h
class ILogger {
public:
    virtual ~ILogger() = default;
    virtual void log(int level, const char* msg) = 0;
};
```

Implementations live in separate `.cpp` files and are selected at runtime (or via a factory). Callers depend only on `ILogger*` — they never `#include` the concrete class header.

## Pitfalls

- **Defining non-trivial methods in headers** — causes the One Definition Rule (ODR) violations or code bloat when included in many translation units.
- **Including unnecessary heavy headers** — prefer forward declarations (`class Foo;`) in headers; include the full header only in the `.cpp`.
- **Exposing private helper types in the header** — they become part of the public ABI and constrain future changes.

## Interview Answer

> "Separate interface from implementation by declaring the class contract in a header and placing method bodies in a `.cpp`. This minimizes recompilation (callers recompile only on header changes), keeps implementation details private, and enables binary-compatible library distribution."
