# Const Reference Lifetime Extension of Temporaries

C++ has a special rule: binding a **const reference** to a temporary extends the temporary's lifetime to match the lifetime of the reference. This is not a trick — it is a deliberate language feature documented in the C++ standard (§ 6.7.7 / [class.temporary]).

## The Problem It Solves

Normally, a temporary (rvalue) object is destroyed at the end of the full expression that created it:

```cpp
std::string greet() { return "Hello, World!"; }

// Without lifetime extension:
const char* p = greet().c_str();  // temporary destroyed here!
std::cout << p;                    // undefined behavior — dangling pointer
```

## Lifetime Extension in Action

When you bind a `const` reference directly to a temporary, the temporary's destructor is delayed until the reference goes out of scope:

```cpp
const std::string& ref = greet();  // lifetime extended!
std::cout << ref;                  // safe — temporary still alive
// ref goes out of scope here → temporary destroyed here
```

This is guaranteed by the standard. The temporary is "attached" to the reference and destroyed when the reference's scope ends.

## Rules and Restrictions

Lifetime extension has precise limits. It only works when the `const` reference is **bound directly** to the temporary:

```cpp
// Works: direct binding
const std::string& r1 = std::string("hello");

// Does NOT work: binding through a function return
const std::string& r2 = someFunction();  // if someFunction returns by value,
                                          // the temporary IS extended — OK
                                          // but only at this point of binding

// Does NOT work: binding through a data member
struct Wrap { const std::string& ref; };
Wrap w{std::string("hi")};  // temporary NOT extended — dangling!
```

Also, lifetime extension does **not** propagate through:
- Function parameters (const ref parameter does not extend past the call)
- Return statements
- Struct/class members

```cpp
const std::string& dangerous(const std::string& s) {
    return s;   // if caller passed a temporary, it died at the call site
}
```

## Practical Use Cases

### Avoiding a Copy in Range-Based For

```cpp
std::vector<int> makeData() { return {1, 2, 3, 4, 5}; }

// Temporary vector lifetime is extended for the duration of the loop
for (const int& v : makeData()) {
    std::cout << v << " ";
}
```

This is idiomatic and safe.

### Accepting Both Lvalues and Rvalues

A single `const T&` overload accepts both:

```cpp
void process(const std::string& s) { /* ... */ }

std::string name = "Alice";
process(name);              // lvalue — OK
process("Bob");             // temporary — OK, lifetime extended for the call
process(std::string("Charlie")); // temporary — OK
```

### Capturing a Computed Temporary

```cpp
const auto& config = parseConfig(readFile("app.cfg"));
// Temporary config object is kept alive as long as `config` reference lives
```

## What Lifetime Extension Is Not

- It is **not** a way to store a temporary in a struct member safely.
- It is **not** available for non-const references (a non-const reference cannot bind to a temporary at all).
- It is **not** a substitute for `std::move` semantics when you need ownership transfer.

## Common Pitfall: Member References

```cpp
struct Bad {
    const std::string& s;
    Bad(const std::string& str) : s(str) {}
};

Bad b{"temporary"};
// "temporary" was a temporary at the constructor call site.
// Lifetime extension does NOT apply to member references.
// b.s is already dangling!
```

Use `std::string s;` (value member) instead.

## Worked Example: Conditional Initialization

```cpp
#include <string>
#include <iostream>

const std::string& pickGreeting(bool formal) {
    static const std::string hi  = "Hi!";
    static const std::string hey = "Good day, sir.";
    return formal ? hey : hi;
}

int main() {
    // Lifetime extension applies to a locally-bound temporary
    const std::string& msg = std::string("Bound: ") + pickGreeting(false);
    std::cout << msg << "\n";  // safe
}
```

> **Interview answer:** Binding a const reference to a temporary extends the temporary's lifetime to match that of the reference. This is a standard-guaranteed rule but only applies to direct bindings — it does not propagate through function returns, struct members, or intermediate references.
