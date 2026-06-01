# Types, References, auto

## Basic types

```cpp
int       i = 42;
long long big = 1'000'000'000'000LL;  // ' is digit separator
double    d = 3.14;
bool      b = true;
char      c = 'A';
auto      n = 5;                       // type inferred as int
auto      pi = 3.14;                   // double
std::size_t size = 100;                // unsigned, for indices/sizes
```

For exact-width integers, include `<cstdint>` and use `int32_t`, `uint64_t`, etc.

## References

A reference is an alias for another value. You can't reseat it.

```cpp
int x = 10;
int& ref = x;        // ref is an alias for x
ref = 20;            // x is now 20

int* ptr = &x;       // pointer can be reseated, can be null
*ptr = 30;
```

Use references when:
- A function shouldn't take ownership but does need to mutate.
- You want to avoid an expensive copy (pass `const std::string&`).
- You're inside operator overloads.

## const

```cpp
const int MAX = 100;             // can't reassign
void print(const std::string& s); // function won't modify s
int* const ptr = &x;             // pointer can't be reseated
const int* ptr = &x;             // can't modify through pointer
```

`const` is part of the type. Use it aggressively — it's documentation the compiler enforces.

## auto and decltype

```cpp
auto x = 5;                            // int
auto v = std::vector<int>{1, 2, 3};    // std::vector<int>
auto& ref = some_long_type_name;       // reference to it
const auto& ref2 = some_long_thing;

auto add(int a, int b) -> int { return a + b; }   // trailing return type
```

`auto` is type *inference*, not dynamic typing — the type is fixed at compile time.

## std::string

```cpp
std::string s = "hello";
s += " world";
s.length();
s.substr(0, 5);
s.find("world");
s.starts_with("hello");      // C++20
s.contains("ll");             // C++23
```

For string formatting:

```cpp
#include <format>             // C++20
auto out = std::format("Hello, {}. Age {}.", name, age);
```

## std::optional

```cpp
#include <optional>

std::optional<User> find_user(int id) {
    if (id == 0) return std::nullopt;
    return User{...};
}

if (auto u = find_user(42)) {
    std::cout << u->name;
}
```

Replaces "return null pointer or sentinel value" with a typed Maybe.

## std::variant — type-safe union

```cpp
std::variant<int, std::string> v = 42;
v = "hello";

std::visit([](auto&& x) { std::cout << x; }, v);
```

## std::span — view into contiguous data

```cpp
void process(std::span<const int> data) {
    for (int x : data) ...
}

std::vector<int> v = {1, 2, 3};
process(v);                  // works
int arr[] = {1, 2, 3};
process(arr);                // also works
```

`std::span<T>` (C++20) is the modern way to accept "any contiguous range of T" — replaces `T* + size`.

## References vs pointers — when to use which

- **Reference (`T&`)** — when null is not a valid state.
- **Pointer (`T*`)** — when null is meaningful, or when you need re-pointing.
- **`std::unique_ptr` / `std::shared_ptr`** — when ownership is involved.

Raw `new`/`delete` are rare in modern code. We cover smart pointers in the RAII lesson.
