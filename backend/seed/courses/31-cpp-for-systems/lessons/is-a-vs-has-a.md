# is-a vs has-a: Inheritance vs Composition

The single most important design decision in OOP is choosing between **inheritance** (is-a) and **composition** (has-a). Getting this wrong creates brittle code that is painful to refactor. This lesson gives you the vocabulary and heuristics to decide quickly.

## Definitions

| Relationship | Meaning | C++ mechanism |
|---|---|---|
| is-a | Derived type is a specialization of the base type | Inheritance |
| has-a | One type owns or uses another type as a component | Composition (member variable) |
| uses-a | One type calls another's interface but does not own it | Dependency / reference member |

## The is-a Test

Ask: "Can I truthfully say *a Derived is always an Base*?"

- A `Dog` is always an `Animal` — inheritance is correct.
- A `Car` is always a `Vehicle` — inheritance is correct.
- A `Stack` is-a `vector`? **No.** A stack hides most of vector's interface. Using public inheritance exposes `push_back`, `operator[]`, and `insert`, which violate the stack contract. Use composition instead.

The classic blunder is the `Square : public Rectangle` hierarchy. Mathematically a square is a rectangle, but if `Rectangle::setWidth` and `Rectangle::setHeight` are independent, they break the invariant of `Square`. The Liskov Substitution Principle (LSP) says: every derived object must be usable wherever a base is expected **without surprising callers**. When that breaks, inheritance is wrong.

## The has-a Test

Ask: "Does this type *contain* or *control* another object as a part?"

```cpp
// BAD: Stack should not inherit from vector
class Stack : public std::vector<int> {
    // push_back, erase, insert all leak through the interface
};

// GOOD: Stack has-a vector
class Stack {
    std::vector<int> data_;   // hidden implementation detail
public:
    void push(int v) { data_.push_back(v); }
    int  pop()       { int v = data_.back(); data_.pop_back(); return v; }
    bool empty()     { return data_.empty(); }
};
```

The composition version:

- Hides the implementation — you can swap `vector` for `deque` without touching callers.
- Enforces the stack contract (no random access).
- Is easier to unit-test in isolation.

## When Inheritance Is Genuinely Needed

1. **Runtime polymorphism** — you need to call a method on an object whose concrete type is only known at runtime.

```cpp
void render(const Shape& s) { s.draw(); }   // works for Circle, Rect, ...
```

2. **Framework extension points** — a library provides a base class that the user subclasses to plug in behavior (e.g., `std::exception`, OS device driver base classes).

3. **Covariant return types** — derived class returns a more specific pointer.

## Composition for Code Reuse

Prefer composition when you want to reuse *implementation* without committing to a public interface contract.

```cpp
class Logger {
public:
    void log(const std::string& msg);
};

class NetworkManager {
    Logger logger_;           // has-a Logger
public:
    void connect(const std::string& host) {
        logger_.log("Connecting to " + host);
        // ...
    }
};
```

`NetworkManager` is not a `Logger`. It just uses one. Inheriting from `Logger` would expose `log()` as part of `NetworkManager`'s public API — which is wrong.

## Common Pitfalls

- **Fragile base class problem**: changing a base class breaks all derived classes, even those that did not use the changed member.
- **Deep hierarchies**: more than 2-3 levels of inheritance almost always indicate a design flaw.
- **God base class**: a base class that accumulates every shared utility, forcing unrelated derived classes to carry dead weight.

## Quick Decision Guide

```
Need runtime polymorphism (virtual dispatch)?  → Inheritance (is-a only)
Need to reuse code without changing interface?  → Composition (has-a)
Unsure?                                         → Start with composition; refactor to inheritance only if you need substitutability
```

> **Interview answer:** Inheritance (is-a) is appropriate only when a derived type can fully substitute for the base without surprising callers. Composition (has-a) should be the default for code reuse because it avoids the fragile base-class problem and keeps interfaces minimal.
