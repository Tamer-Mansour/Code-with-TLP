# Range-Based for Loops

Range-based `for` (introduced in C++11) iterates over any sequence that exposes `begin()` and `end()`. It eliminates manual index management, reducing off-by-one errors that are especially costly in systems code.

## Syntax

```cpp
for (declaration : range-expression) {
    // body
}
```

The compiler expands this roughly to:

```cpp
{
    auto&& __range = range-expression;
    auto __it  = begin(__range);
    auto __end = end(__range);
    for (; __it != __end; ++__it) {
        declaration = *__it;
        // body
    }
}
```

Understanding this expansion explains every pitfall.

## Common Forms

```cpp
std::vector<int> v = {1, 2, 3, 4};

// Copy each element (expensive for large types)
for (int x : v) { /* x is a copy */ }

// Const reference — cheapest for read-only access
for (const int& x : v) { /* no copy, no mutation */ }

// Mutable reference — modify elements in place
for (int& x : v) { x *= 2; }

// auto& — adapts to element type automatically
for (auto& x : v) { x += 1; }
```

Rule of thumb: use `const auto&` for reading, `auto&` for mutation, plain `auto` only for cheap/trivial types.

## Works with Any Range

Any type that provides `begin()` / `end()` (as member functions or ADL-found free functions) works:

```cpp
int arr[] = {10, 20, 30};
for (auto x : arr) { /* works for raw arrays too */ }

std::string s = "hello";
for (char c : s) { /* iterates characters */ }
```

Custom types just need:

```cpp
struct Buffer {
    uint8_t* begin() { return data; }
    uint8_t* end()   { return data + size; }
    uint8_t* data;
    size_t   size;
};
```

## C++17: Range-Based `for` with Initializer

```cpp
for (auto v = get_devices(); const auto& dev : v) {
    process(dev);
}
// v is not visible here
```

The initializer clause limits the scope of temporary objects, avoiding dangling references.

## Pitfall: Range Expression Evaluated Once

The range expression is evaluated exactly once and bound to `__range`. This means:

```cpp
// Safe: end() is recalculated only once
for (auto& x : expensive_container()) { }

// Dangerous: if the container reallocates during iteration, iterators dangle
for (auto& x : v) {
    v.push_back(99);  // UB: invalidates iterators
}
```

## Pitfall: Temporary Lifetime

```cpp
std::vector<int> get_vec();

for (auto x : get_vec()) { }   // OK: temporary lives for the loop
for (auto& x : get_vec()) { }  // OK in C++11/14/17 (lifetime extended)

// But with a reference member — can dangle:
struct View { const std::vector<int>& ref; };
// Don't bind __range to a View pointing at a temporary
```

## Systems Engineering Perspective

Iterating over a device list, DMA scatter-gather array, or interrupt table with range-based `for` is cleaner and safer than index-based loops. It also works with custom allocators and MMIO-mapped memory arrays as long as you provide `begin`/`end`.

## Worked Example: Iterating a Fixed-Size Register Bank

```cpp
#include <array>
#include <cstdint>

struct Reg { uint32_t addr; uint32_t mask; };

constexpr std::array<Reg, 4> GPIO_REGS = {{
    {0x4000'0000, 0xFF},
    {0x4000'0004, 0xFF},
    {0x4000'0008, 0x0F},
    {0x4000'000C, 0x0F},
}};

void reset_gpio() {
    for (const auto& reg : GPIO_REGS) {
        *reinterpret_cast<volatile uint32_t*>(reg.addr) &= ~reg.mask;
    }
}
```

`std::array` is a zero-overhead wrapper — the range-based loop here compiles to the same code as a hand-written index loop.

> **Interview answer:** "Range-based `for` desugars to `begin`/`end` iterator pairs. Use `const auto&` for read-only access to avoid copies, `auto&` to mutate elements. Never modify the container size during iteration — it invalidates iterators and causes undefined behavior."
