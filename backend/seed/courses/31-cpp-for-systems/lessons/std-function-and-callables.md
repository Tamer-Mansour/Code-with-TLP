# std::function and Callable Objects

`std::function` is a type-erased wrapper that can hold any callable — function pointer, lambda, functor, or bound member function — with a matching signature. It is the standard way to store and pass callbacks.

## What Is a Callable?

A callable is anything that can be invoked with `()`:

- Free functions: `void f(int);`
- Function pointers: `void (*fp)(int);`
- Lambdas: `[](int x){ }`
- Functors (classes with `operator()`): `struct Add { int operator()(int a, int b); };`
- Bound member functions: `std::bind(&MyClass::method, obj, ...)`
- `std::function` itself

## `std::function` Syntax

```cpp
#include <functional>

std::function<ReturnType(Arg1, Arg2)> callback;
```

Example:

```cpp
std::function<int(int, int)> op;

op = [](int a, int b) { return a + b; };
op(3, 4);  // 7

op = std::plus<int>{};  // standard functor
op(3, 4);  // 7
```

## Storing Any Callable

```cpp
void free_fn(int x) { /* ... */ }

struct Multiplier {
    int factor;
    int operator()(int x) const { return x * factor; }
};

std::vector<std::function<int(int)>> transforms;
transforms.push_back(free_fn);                   // function pointer
transforms.push_back([](int x){ return x*2; });  // lambda
transforms.push_back(Multiplier{3});              // functor

for (auto& fn : transforms) {
    fn(10);
}
```

## Member Function Binding

```cpp
struct Device {
    void handle_irq(uint8_t irq);
};

Device dev;
std::function<void(uint8_t)> cb =
    std::bind(&Device::handle_irq, &dev, std::placeholders::_1);
cb(5);  // calls dev.handle_irq(5)
```

Or more idiomatically with a lambda:

```cpp
std::function<void(uint8_t)> cb = [&dev](uint8_t irq) {
    dev.handle_irq(irq);
};
```

Prefer the lambda form — it is clearer and avoids `std::bind` quirks.

## Performance Considerations

`std::function` uses **type erasure** via a virtual call or small-buffer-optimized heap allocation. This means:

| Property | `std::function` | Function pointer | Lambda (direct) |
|----------|----------------|-----------------|-----------------|
| Zero-overhead | No | Yes | Yes (inlined) |
| Stores state | Yes | No | Yes |
| Type-erased | Yes | No | No |
| Can be null | Yes | Yes | No |

In hot paths (interrupt handlers, DMA callbacks), avoid `std::function`. Use templates with concepts or direct function pointers.

## Checking for Empty

```cpp
std::function<void()> cb;  // default-constructed: empty

if (cb) {         // converts to bool
    cb();
}
// Calling an empty std::function throws std::bad_function_call
```

## `std::invoke` (C++17) — Uniform Call Syntax

`std::invoke(callable, args...)` calls any callable uniformly, including member function pointers:

```cpp
#include <functional>

struct Foo { int value() const { return 42; } };

Foo foo;
std::invoke(&Foo::value, foo);          // 42
std::invoke([](int x){ return x; }, 5); // 5
```

This is especially useful in generic code and higher-order functions.

## Systems Engineering Patterns

### IRQ dispatch table

```cpp
constexpr size_t NUM_IRQS = 256;
std::array<std::function<void()>, NUM_IRQS> irq_table;

void register_handler(uint8_t irq, std::function<void()> fn) {
    irq_table[irq] = std::move(fn);  // move to avoid copy
}

void dispatch_irq(uint8_t irq) {
    if (irq_table[irq]) irq_table[irq]();
}
```

### Policy-based design without virtual

```cpp
template<typename Policy>
void process_buffer(const uint8_t* data, size_t len, Policy&& policy) {
    policy(data, len);  // zero-overhead, inlined at compile time
}

// vs. runtime-flexible:
void process_buffer(const uint8_t* data, size_t len,
                    std::function<void(const uint8_t*, size_t)> policy);
```

Choose the template form for performance-critical code, `std::function` when the callable is determined at runtime.

## Worked Example: Event Dispatcher

```cpp
#include <functional>
#include <unordered_map>
#include <string>

class EventBus {
    std::unordered_map<std::string, std::function<void(int)>> handlers_;
public:
    void subscribe(std::string event, std::function<void(int)> fn) {
        handlers_[std::move(event)] = std::move(fn);
    }
    void emit(const std::string& event, int data) {
        auto it = handlers_.find(event);
        if (it != handlers_.end()) it->second(data);
    }
};
```

> **Interview answer:** "`std::function` is a type-erased wrapper for any callable with a matching signature. It enables runtime-polymorphic callbacks without inheritance, but has overhead from type erasure (potential heap allocation, virtual dispatch). In performance-critical paths, prefer template parameters or raw function pointers."
