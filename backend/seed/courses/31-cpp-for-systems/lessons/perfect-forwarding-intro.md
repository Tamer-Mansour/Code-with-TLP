# Forwarding References and std::forward (Intro)

**Perfect forwarding** is the ability to pass arguments through a function template to another function while preserving the exact value category of each argument — lvalue stays lvalue, rvalue stays rvalue. Without it, every intermediary layer forces an unnecessary copy or loses move semantics.

## The Problem: Value Category Is Lost in Transit

```cpp
void sink(std::string&& s) {
    // s is an rvalue reference but a named lvalue here
}

template<typename T>
void relay(T arg) {
    sink(arg); // ALWAYS passes as lvalue — move is lost
}

relay(std::string{"hello"}); // we passed an rvalue, but sink sees lvalue
```

Even if we change `relay` to accept `T&&`, we still need to forward correctly:

```cpp
template<typename T>
void relay(T&& arg) {
    sink(arg);            // still lvalue — 'arg' has a name
    sink(std::move(arg)); // always rvalue — wrong for lvalue args!
}
```

## Forwarding References (Universal References)

When `T&&` appears in a template where `T` is a **deduced** type parameter, it is a **forwarding reference** (also called a universal reference), not a plain rvalue reference. It can bind to both lvalues and rvalues through **reference collapsing**:

| Caller passes | `T` deduced as | `T&&` becomes |
|---------------|---------------|--------------|
| `std::string` lvalue | `std::string&` | `std::string& &&` → `std::string&` |
| `std::string` rvalue | `std::string` | `std::string&&` |

Reference collapsing rules: any combination involving `&` collapses to `&`; `&&` only survives when both sides are `&&`.

```cpp
template<typename T>
void relay(T&& arg);  // forwarding reference — binds to anything

std::string s = "hello";
relay(s);                    // T = std::string&,  arg: std::string&
relay(std::string{"world"}); // T = std::string,   arg: std::string&&
```

## std::forward: The Perfect Cast

`std::forward<T>(arg)` conditionally casts `arg` to `T&&`:
- If `T` is `std::string&`, it casts to `std::string&` (lvalue preserved).
- If `T` is `std::string`, it casts to `std::string&&` (rvalue preserved).

```cpp
#include <utility>

template<typename T>
void relay(T&& arg) {
    sink(std::forward<T>(arg)); // preserves value category
}

std::string s = "hello";
relay(s);                    // sink gets lvalue reference
relay(std::string{"world"}); // sink gets rvalue reference — moved
```

Conceptually, `std::forward<T>` is:

```cpp
template<typename T>
T&& forward(std::remove_reference_t<T>& t) noexcept {
    return static_cast<T&&>(t);
}
```

## std::move vs std::forward

| | `std::move(x)` | `std::forward<T>(x)` |
|--|---|---|
| Always produces | rvalue | Depends on `T` |
| Use in | Sink functions, move constructors | Forwarding function templates |
| Requires type param | No | Yes — `T` must be the deduced type |

```cpp
// WRONG: std::move in a relay — always moves even for lvalue callers
template<typename T>
void relay_bad(T&& arg) { sink(std::move(arg)); }

// CORRECT: std::forward preserves what the caller passed
template<typename T>
void relay_good(T&& arg) { sink(std::forward<T>(arg)); }
```

## Real-World Usage: Factory Functions (make_*)

Perfect forwarding powers `std::make_unique`, `std::make_shared`, and `std::vector::emplace_back`:

```cpp
template<typename T, typename... Args>
std::unique_ptr<T> make_unique(Args&&... args) {
    return std::unique_ptr<T>(new T(std::forward<Args>(args)...));
}
```

Arguments passed to `make_unique<Widget>(x, std::move(y))` arrive at `Widget`'s constructor with their original value categories intact — no extra copies.

## Common Pitfall: Forwarding Twice

Once you `std::forward` (move from) an argument, do not use it again:

```cpp
template<typename T>
void bad_relay(T&& arg) {
    use(std::forward<T>(arg));  // arg may be moved from here
    log(arg);                   // UNDEFINED if arg was rvalue
}
```

> **Interview answer:** A forwarding reference is a `T&&` parameter in a deduced template context that binds to both lvalues and rvalues via reference collapsing. `std::forward<T>` conditionally casts the argument back to its original value category — lvalue or rvalue — enabling a relay function to pass arguments to downstream functions without adding extra copies or losing move semantics.
