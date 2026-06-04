# Virtual Dispatch Table Lookup

This exercise models the exact mechanism the C++ compiler uses to implement `virtual` function calls. Every class with at least one virtual function has a **vtable** — a static array of function pointers. Every object of that class carries a hidden **vptr** pointing to its vtable. When you call `obj->speak()`, the compiler emits code equivalent to `obj->vptr[speak_slot]()` — one pointer dereference and one indirect call.

## What You Are Building

Given a class hierarchy and method definitions, resolve CALL operations by walking up the MRO (Method Resolution Order) from the most-derived class to its base classes, returning the first matching override.

See the prompt for full input/output specification.

## Simulating the Vtable Walk

```python
def resolve(cls, method, parent, methods):
    cur = cls
    while cur is not None:
        if (cur, method) in methods:
            return methods[(cur, method)]
        cur = parent.get(cur)
    return 'ERROR'
```

This is exactly how C++ constructs the vtable at compile time: it scans the class hierarchy from most-derived upward and fills each vtable slot with the most-derived override it finds.

## Key Insight: Override vs Overload

- **Override** (what this exercise models): a derived class replaces a virtual function from a base class. The vtable slot for that method points to the derived version.
- **Overload**: a function with the same name but different parameters. Overloads are resolved at compile time by the type system; they do not involve the vtable.

In C++, always mark overrides with the `override` keyword:

```cpp
class Dog : public Animal {
public:
    std::string speak() override { return "Woof"; }
};
```

The compiler will error if `speak` is not actually virtual in `Animal`, preventing the silent bug of accidentally hiding rather than overriding.

## Runtime Cost

A single virtual call costs:
1. Load vptr from object (pointer-chasing the object's first hidden field).
2. Index into the vtable array (compile-time-known slot index).
3. Indirect function call through the loaded pointer.

This is typically 1–3 ns on a modern CPU — negligible unless the call is inside a tight loop with many different concrete types, preventing branch prediction. Blanket avoidance of virtual calls is premature optimization; profile first.

## Further Reading

- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines), rule **C.120**: Use class hierarchies to represent concepts with inherent hierarchical structure (only).
- *A Tour of C++* by Bjarne Stroustrup — [https://isocpp.org/files/papers/5-Tour-Util.pdf](https://isocpp.org/files/papers/5-Tour-Util.pdf) — covers virtual dispatch and abstract classes concisely.
