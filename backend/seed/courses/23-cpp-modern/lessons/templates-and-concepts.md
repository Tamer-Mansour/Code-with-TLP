# Templates and Concepts

Templates are C++'s generic programming mechanism — write code once, the compiler instantiates a copy per concrete type. Concepts (C++20) let you constrain what types are allowed.

## Function templates

```cpp
template <typename T>
T max_of(T a, T b) {
    return a > b ? a : b;
}

max_of(3, 5);              // T = int
max_of(3.5, 2.0);          // T = double
max_of(std::string{"x"}, std::string{"y"});
```

The compiler generates one function per (T) you actually call.

## Class templates

```cpp
template <typename T>
class Stack {
    std::vector<T> data_;
public:
    void push(T value) { data_.push_back(std::move(value)); }
    T pop() {
        T v = std::move(data_.back());
        data_.pop_back();
        return v;
    }
    bool empty() const { return data_.empty(); }
};

Stack<int> s;
s.push(1); s.push(2);
```

## Variadic templates

```cpp
template <typename... Args>
void print(Args... args) {
    (std::cout << ... << args) << '\n';     // fold expression (C++17)
}

print(1, " ", "hello", " ", 3.14);
```

`...` packs and unpacks parameter packs. Fold expressions (`(... op pack)`) combine them.

## SFINAE — old way to constrain

```cpp
template <typename T,
          typename = std::enable_if_t<std::is_integral_v<T>>>
T add(T a, T b) { return a + b; }
```

Verbose, error messages are terrible. Concepts replace this.

## Concepts (C++20)

```cpp
#include <concepts>

template <typename T>
concept Number = std::integral<T> || std::floating_point<T>;

template <Number T>
T square(T x) { return x * x; }

square(5);             // OK
square(2.5);           // OK
square("hello");       // ❌ clear error: "constraint not satisfied: not a Number"
```

Concepts:
- Self-documenting — the constraint is right there.
- Better error messages.
- Allow function overloading by constraint.

```cpp
template <std::integral T> void print(T x) { /* ints */ }
template <std::floating_point T> void print(T x) { /* doubles */ }
```

The compiler picks the right one without enable_if gymnastics.

## Built-in concepts

```
std::integral         std::floating_point     std::arithmetic
std::same_as<T>       std::convertible_to<T>  std::derived_from<T>
std::default_initializable  std::copyable    std::movable
std::regular          std::semiregular
std::equality_comparable    std::totally_ordered
std::invocable<R, Args...>  std::predicate
std::input_iterator   std::random_access_iterator
std::ranges::range    std::ranges::view
```

Compose with `&&`, `||`, `requires`.

## requires clauses

For ad-hoc constraints without a named concept:

```cpp
template <typename T>
requires requires(T a, T b) { a + b; }
T sum(T a, T b) { return a + b; }
```

Read as: "requires that for two T's, `a + b` is valid."

## Template specialization

You can provide a different implementation for a specific type:

```cpp
template <typename T>
struct Serializer {
    std::string to_string(T v) { return std::to_string(v); }
};

template <>
struct Serializer<std::string> {
    std::string to_string(const std::string& s) { return "\"" + s + "\""; }
};
```

Use sparingly — concepts usually express constraint better than specialization.

## When NOT to template

Templates have costs:
- Slow compile times.
- Code bloat (each instantiation is its own copy).
- Errors deep inside instantiations are notoriously hard to read (better with concepts).

If your "generic" thing only operates on `int` and `double`, just write two overloads. Templates are for *true* polymorphism over types.
