# What std::move Actually Does

`std::move` is one of the most misunderstood utilities in modern C++. Its name is misleading — it does **not move anything**. It is a cast.

## The One-Line Truth

```cpp
// Conceptual implementation (simplified from <utility>)
template<typename T>
constexpr std::remove_reference_t<T>&& move(T&& t) noexcept {
    return static_cast<std::remove_reference_t<T>&&>(t);
}
```

`std::move(x)` performs a static cast that strips any reference qualifier from `T` and casts the result to an rvalue reference (`T&&`). It converts an lvalue into an **xvalue** — an expiring value that the compiler is allowed to move from.

No bytes are touched. No memory is allocated or freed. It is a compile-time operation that changes value category.

## The Actual Move Happens in the Constructor or Assignment

```cpp
std::string a = "hello";
std::string b = std::move(a);  // <-- move happens HERE in move constructor
//              ^^^^^^^^^^^
//              just a cast; move constructor does the real work
```

The sequence:
1. `std::move(a)` returns `std::string&&` referencing `a`.
2. `std::string`'s move constructor is selected because the argument is an rvalue.
3. The move constructor steals `a`'s internal buffer and nullifies `a`.

## After std::move — The Source Is in a "Valid but Unspecified" State

The C++ standard guarantees the moved-from object is **destructible** and **assignable**, but makes no promise about its value. For `std::string`, it is typically empty after a move. For user-defined types, it depends on your move constructor's implementation.

```cpp
std::string s = "world";
std::string t = std::move(s);

// s is valid — you can do this:
s = "reassigned";   // OK
s.clear();          // OK
std::cout << s;     // OK (may print "" or something else)

// But do NOT rely on a specific value:
// if (s == "world") { ... }  // WRONG assumption
```

## Common Pitfall: Moving a const Object Does Nothing

```cpp
const std::string cs = "hello";
std::string t = std::move(cs); // Calls COPY constructor, not move!
```

`std::move(cs)` produces `const std::string&&`. No move constructor accepts `const T&&` (it would not be able to modify the source), so overload resolution falls back to the `const T&` copy constructor. The move silently becomes a copy — no warning from the compiler.

## Common Pitfall: Moving in Return Statements Suppresses NRVO

```cpp
std::string make_string() {
    std::string result = "hello";
    return std::move(result);  // BAD — prevents NRVO
    return result;             // GOOD — NRVO or implicit move
}
```

Compilers apply Named Return Value Optimization (NRVO) to eliminate the move entirely when you return a local variable by name. Adding `std::move` interferes with NRVO because it changes the expression from an lvalue to an xvalue, which NRVO cannot optimize. Always return local variables directly; the compiler will move them automatically when NRVO fails.

## When You Should Use std::move

| Situation | Use std::move? |
|-----------|---------------|
| Passing a local variable to a sink function | Yes |
| Storing a parameter into a member | Yes (if parameter is by-value) |
| Return statement for a local variable | No — let compiler decide |
| Moving from a const object | Never — it silently copies |
| Moving from a function argument you still need | No — undefined behavior territory |

## Practical Pattern: Sink Parameter

```cpp
class Logger {
    std::string tag_;
public:
    // By-value parameter — caller chooses copy or move
    explicit Logger(std::string tag)
        : tag_(std::move(tag)) {} // move from local copy into member
};

Logger log1("fixed");              // one copy into tag
Logger log2(std::string("temp"));  // one move into tag (no copy)
```

> **Interview answer:** `std::move` is a compile-time cast from lvalue to xvalue — it does not move any data. It enables the compiler to select move-constructor and move-assignment overloads. The actual resource transfer happens in those special member functions. Moving a `const` object silently falls back to copying.
