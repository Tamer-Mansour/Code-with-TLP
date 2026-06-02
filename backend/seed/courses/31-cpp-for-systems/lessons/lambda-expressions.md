# Lambda Expressions and Captures

Lambdas (C++11) are anonymous function objects defined inline. They are not syntactic sugar — each lambda creates a unique, unnamed class with an `operator()`. Understanding captures is critical to avoiding dangling references and data races.

## Basic Syntax

```cpp
[capture-list](parameters) -> return-type { body }
```

All parts except the body and capture list are optional:

```cpp
auto greet = []{ return 42; };          // no params, no capture
auto add   = [](int a, int b){ return a+b; };
auto mul   = [](int a, int b) -> int { return a * b; };
```

## Capture Modes

The capture list controls what the lambda can see from its enclosing scope:

| Capture | Meaning |
|---------|---------|
| `[]` | Capture nothing |
| `[=]` | Copy everything used |
| `[&]` | Reference everything used |
| `[x]` | Copy `x` only |
| `[&x]` | Reference `x` only |
| `[=, &x]` | Copy all, except `x` by ref |
| `[this]` | Capture `this` pointer |
| `[*this]` | Copy the object (C++17) |

```cpp
int base = 100;

auto by_copy = [base](int x) { return base + x; };  // base copied
auto by_ref  = [&base](int x) { return base + x; };  // base referenced

base = 200;
by_copy(5);  // 105 — saw original 100
by_ref(5);   // 205 — sees updated 200
```

## Mutable Lambdas

Captured copies are `const` by default. Add `mutable` to modify them:

```cpp
int counter = 0;
auto inc = [counter]() mutable { return ++counter; };
inc();  // returns 1 — but outer counter is unchanged
inc();  // returns 2
```

## Immediately Invoked Lambda Expressions (IILE)

Useful for complex `const` initialization:

```cpp
const std::string mode = [&]() -> std::string {
    if (debug) return "debug";
    if (verbose) return "verbose";
    return "release";
}();
```

## Generic Lambdas (C++14)

`auto` parameters make the lambda a template:

```cpp
auto max_val = [](auto a, auto b) { return a > b ? a : b; };
max_val(3, 4);        // int
max_val(1.5, 2.5);    // double
```

## Capture with Initializer (C++14)

Capture computed or moved-only values:

```cpp
auto ptr = std::make_unique<int>(42);

// Move unique_ptr into the lambda
auto fn = [p = std::move(ptr)]() { return *p; };
```

This is the only way to capture move-only types.

## Lambdas in Systems Code

### Sorting with custom comparators

```cpp
std::vector<Process> procs;
std::sort(procs.begin(), procs.end(),
    [](const Process& a, const Process& b) {
        return a.priority > b.priority;  // highest priority first
    });
```

### Deferred callbacks

```cpp
void register_irq_handler(uint8_t irq, std::function<void()> handler);

uint32_t base_addr = 0x4000'0000;
register_irq_handler(5, [base_addr]() {
    volatile uint32_t* reg = reinterpret_cast<volatile uint32_t*>(base_addr);
    *reg |= 0x1;  // ACK interrupt
});
```

### `std::for_each` with side effects

```cpp
size_t total = 0;
std::for_each(packets.begin(), packets.end(),
    [&total](const Packet& p) { total += p.length; });
```

## Common Pitfalls

- **Dangling reference capture**: a lambda that captures by reference and outlives the captured variable is UB.

```cpp
auto make_adder(int x) {
    return [&x](int y) { return x + y; };  // DANGER: x is gone after return
}
```

Fix: capture by value `[x]`.

- **`[=]` capturing `this`**: `[=]` in a member function implicitly captures `this` — you can still access members through the pointer even though it looks like a value capture.

- **Thread safety**: captured references are not protected — use `[=]` or explicit synchronization when passing lambdas to other threads.

## Worked Example: Interrupt-Driven Buffer Flush

```cpp
#include <vector>
#include <algorithm>

struct Packet { uint32_t id; size_t size; bool ready; };

size_t flush_ready(std::vector<Packet>& buf) {
    size_t flushed = 0;
    std::for_each(buf.begin(), buf.end(), [&flushed](Packet& p) {
        if (p.ready) {
            // send_to_dma(p);
            flushed += p.size;
            p.ready = false;
        }
    });
    return flushed;
}
```

> **Interview answer:** "Each lambda generates a unique class with `operator()`. The capture list decides what the lambda borrows — `[=]` copies, `[&]` references. Reference captures create dangling pointers if the lambda outlives the scope, so callbacks and thread lambdas should prefer value captures or captured initializers (`[p = std::move(ptr)]`)."
