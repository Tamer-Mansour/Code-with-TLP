# Structured Bindings

Structured bindings (C++17) let you decompose a tuple, pair, struct, or array into individually named variables in a single declaration. They eliminate the clutter of `.first`/`.second` and manual `get<N>()` calls.

## Basic Syntax

```cpp
auto [a, b] = std::make_pair(1, 3.14);
// a is int, b is double
```

The compiler creates a hidden binding object and then binds each name to a member.

## Works With Pairs and Tuples

```cpp
#include <tuple>

std::tuple<int, double, std::string> get_record() {
    return {42, 1.5, "hello"};
}

auto [id, score, name] = get_record();
// id:int, score:double, name:std::string
```

Before C++17 you would write:

```cpp
int id; double score; std::string name;
std::tie(id, score, name) = get_record();
```

Structured bindings are cleaner and work with `const`, references, and `auto&&`.

## Works With Structs (Aggregates)

Any aggregate (no user-declared constructors, no private/protected non-static data members) can be decomposed:

```cpp
struct Packet {
    uint32_t seq;
    uint16_t length;
    uint8_t  flags;
};

Packet pkt{100, 64, 0x03};
auto [seq, len, flags] = pkt;  // copies
auto& [rseq, rlen, rflags] = pkt;  // references — mutation affects pkt
```

## Works With Arrays

```cpp
int arr[3] = {1, 2, 3};
auto [x, y, z] = arr;
```

## Qualifiers: `const`, `&`, `&&`

The qualifier applies to the hidden binding object, which then affects all bound names:

```cpp
const auto& [a, b] = some_pair;  // a and b are const references
auto& [x, y] = my_struct;        // mutable references
auto&& [p, q] = get_pair();      // forwarding reference
```

## Most Common Pattern: Map Iteration

```cpp
#include <map>
#include <string>

std::map<std::string, int> scores;

for (const auto& [name, score] : scores) {
    // Much cleaner than: it->first, it->second
}
```

This is the idiomatic way to iterate associative containers in C++17.

## Systems Engineering Use Cases

### Decomposing `ioctl` result structs

```cpp
struct DmaResult { int fd; size_t bytes_transferred; int error_code; };

DmaResult perform_dma();

auto [fd, bytes, err] = perform_dma();
if (err != 0) { handle_error(err); }
```

### Returning multiple values from low-level functions

```cpp
std::pair<bool, uint32_t> read_register(uint32_t addr);

auto [ok, value] = read_register(0x4000'0000);
if (ok) { process(value); }
```

### Custom Types via `get<>` Specialization

You can enable structured bindings for your own non-aggregate types by specializing `std::tuple_size`, `std::tuple_element`, and providing a `get<N>` function:

```cpp
struct Vec2 { float x, y; };

template<> struct std::tuple_size<Vec2> { static constexpr size_t value = 2; };
template<> struct std::tuple_element<0, Vec2> { using type = float; };
template<> struct std::tuple_element<1, Vec2> { using type = float; };

template<size_t I> float& get(Vec2& v) {
    if constexpr (I == 0) return v.x; else return v.y;
}

Vec2 v{1.0f, 2.0f};
auto [vx, vy] = v;
```

## Common Pitfalls

- **Copying by accident**: `auto [a, b] = map_iter;` copies the entire element — prefer `const auto&`.
- **Aggregate requirement**: non-aggregates (classes with private members or constructors) require the `get<>` customization point.
- **Count mismatch**: the number of bindings must exactly match the number of members/elements — compiler error otherwise.

> **Interview answer:** "Structured bindings (C++17) decompose pairs, tuples, arrays, and aggregates into named variables with `auto [a, b, c] = ...`. They eliminate `.first`/`.second` noise and are especially valuable in map iteration and multi-return functions. Qualifiers like `const auto&` apply to the underlying binding object."
