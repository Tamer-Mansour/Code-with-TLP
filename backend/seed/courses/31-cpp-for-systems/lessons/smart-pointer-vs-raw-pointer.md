# When to Use Smart vs Raw (Non-Owning) Pointers

The headline rule in the C++ Core Guidelines is clear: **if a pointer owns a resource, express that ownership with a smart pointer. If it merely observes, a raw pointer or reference is fine.** Knowing where the line falls is essential for writing idiomatic modern C++.

## Ownership vs Observation

Ownership means: "I am responsible for this object's lifetime."
Observation means: "I need access to this object, but I am not responsible for it."

```cpp
// Owner — heap-allocated, needs cleanup
auto owner = std::make_unique<Widget>();

// Observer — borrows from the owner, no cleanup responsibility
Widget* viewer = owner.get();
viewer->read();
// If owner is destroyed, viewer becomes a dangling pointer — caller's responsibility
```

Ownership should always be expressed in the type. Raw observing pointers are fine as long as their use is bounded within the lifetime of the owner.

## Decision Table

| Scenario | Recommended type |
|---|---|
| Single owner, heap-allocated object | `unique_ptr<T>` |
| Multiple owners, shared lifetime | `shared_ptr<T>` |
| Non-owning observer, no lifetime concern | `T*` or `T&` |
| Non-owning observer that may outlive the source | `weak_ptr<T>` |
| Optional non-owning reference | `T*` (null = absent) |
| Guaranteed non-null, non-owning | `T&` |

## Function Parameters: The Most Common Decision Point

Parameters communicate intent at the call site:

```cpp
// Takes ownership — caller transfers; callee is responsible for deletion
void sink(std::unique_ptr<Widget> w);

// Borrows for the duration of the call — no ownership transfer
void use(Widget& w);          // preferred when non-null is guaranteed
void use(Widget* w);          // when null is a valid input

// Borrows a shared owner — increments ref count, callee may store it
void cache(std::shared_ptr<Widget> w);

// Reads a shared owner without incrementing ref count
void inspect(const std::shared_ptr<Widget>& w);
```

Passing `shared_ptr` by value when you only need to read the object is unnecessarily expensive — it pays for an atomic increment and decrement. Prefer `const T&` or `T*` in those cases.

## The "Observing Pointer" Pattern in Practice

Consider a scene graph renderer:

```cpp
class Scene {
    std::vector<std::unique_ptr<Node>> nodes_;
public:
    Node* findByName(std::string_view name);  // returns raw ptr, non-owning
};
```

`findByName` returns a raw pointer. This is correct: the `Scene` owns the nodes; callers that use the pointer for a quick read do not need ownership. If the `Scene` is destroyed before the caller uses the pointer, that is a programming error — not a case where `shared_ptr` would help.

## Stack Objects Need No Smart Pointers

Smart pointers are only needed for **heap-allocated** objects. Stack objects are destroyed automatically:

```cpp
Widget w;            // stack — no smart pointer needed
Widget* p = &w;      // raw observing pointer — fine
```

## Common Mistakes to Avoid

- **Using `shared_ptr` everywhere out of habit** — it adds atomic operations and a control block with no benefit when a single owner could be identified.
- **Storing `.get()` result in a long-lived structure** — the raw pointer becomes dangling when the smart pointer is destroyed.
- **Passing `unique_ptr` by `const&` to inspect** — this leaks implementation detail; pass `const Widget&` instead.
- **Returning raw `new` from a factory** — callers cannot tell whether they own the result. Always return `unique_ptr` from factories.

## The Core Guideline Summary

- `unique_ptr` — default choice for heap allocation.
- `shared_ptr` — only when shared lifetime is genuinely required.
- `weak_ptr` — observers that must handle the object disappearing.
- Raw pointer / reference — non-owning access within a known lifetime bound.
- Never `new` or `delete` in application code directly — let smart pointers handle it.

## Interview Answer

**"When would you use a raw pointer instead of a smart pointer?"**

> Raw pointers are appropriate for non-owning access — borrowing an object for the duration of a function call, iterating a container, or returning a pointer to an element the caller does not own. Smart pointers encode ownership; raw pointers encode access without ownership. If the lifetime is controlled elsewhere and the pointer can't outlive its source, a raw pointer is simpler and equally correct.
