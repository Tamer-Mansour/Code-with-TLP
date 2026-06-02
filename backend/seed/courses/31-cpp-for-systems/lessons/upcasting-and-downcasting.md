# Upcasting, Downcasting, and dynamic_cast

Casting between base and derived types is central to polymorphic C++ code. There are two directions — **upcasting** (derived to base) and **downcasting** (base to derived) — and they carry very different safety implications.

## Upcasting — Always Safe

Converting a derived pointer/reference to a base pointer/reference is called an **upcast**. It is always safe and happens implicitly:

```cpp
class Animal { public: virtual void speak() {} virtual ~Animal() = default; };
class Dog : public Animal { public: void speak() override { std::cout << "Woof\n"; } };

Dog d;
Animal* a = &d;    // implicit upcast — no cast needed
a->speak();        // virtual dispatch: calls Dog::speak()
```

An upcast is safe because every `Dog` **is** an `Animal`. The compiler performs pointer adjustment automatically when multiple inheritance is involved.

## Downcasting — Potentially Unsafe

Going from `Base*` to `Derived*` is a **downcast**. The compiler cannot verify at compile time that the object actually is the target type, so you have to choose a cast carefully.

### static_cast (compile-time, no check)

```cpp
Animal* a = new Dog();
Dog* d = static_cast<Dog*>(a);   // OK if you are certain the object is a Dog
d->speak();                      // fine

// Danger:
Animal* a2 = new Animal();
Dog* d2 = static_cast<Dog*>(a2);   // compiles, but undefined behavior
d2->speak();                       // UB: no Dog vtable
```

`static_cast` is fast (zero-overhead) but trusts you completely. Use it only when you have guaranteed knowledge of the actual type, for example after checking a discriminator or inside a sealed factory.

### dynamic_cast (runtime type check)

`dynamic_cast` verifies the actual type at runtime using RTTI (run-time type information). It requires at least one `virtual` function in the base class (so the compiler generates a vtable).

```cpp
Animal* a = new Dog();

Dog*  d = dynamic_cast<Dog*>(a);   // returns valid Dog* if a is-a Dog
Cat*  c = dynamic_cast<Cat*>(a);   // returns nullptr — a is not a Cat

if (d) {
    d->speak();    // safe
}
```

For **references**, a failed `dynamic_cast` throws `std::bad_cast` instead of returning `nullptr`:

```cpp
try {
    Animal& a_ref = *new Animal();
    Dog& d_ref = dynamic_cast<Dog&>(a_ref);   // throws std::bad_cast
} catch (const std::bad_cast& e) {
    std::cout << e.what() << "\n";
}
```

## Cost of dynamic_cast

`dynamic_cast` is not free. It must:

1. Read the vptr of the object.
2. Walk the type hierarchy stored in RTTI structures.
3. Compare type descriptors.

On most implementations this is O(depth of hierarchy), roughly a handful of comparisons. In tight loops or real-time code this can matter. Profile before optimizing, but be aware of the cost.

## Avoiding dynamic_cast with Visitor or Tag

Needing `dynamic_cast` frequently is often a design smell — the base class should provide the right virtual interface. Common alternatives:

**Visitor pattern** — double dispatch through virtual functions:

```cpp
struct Visitor;
struct Shape { virtual void accept(Visitor&) = 0; };
struct Circle : Shape { void accept(Visitor& v) override; };
struct Rect   : Shape { void accept(Visitor& v) override; };

struct Visitor {
    virtual void visit(Circle&) = 0;
    virtual void visit(Rect&)   = 0;
};
```

**Type tag / enum** — store the concrete type explicitly (common in OS kernels):

```cpp
enum class NodeKind { Int, Float, String };
struct Node { NodeKind kind; };
struct IntNode : Node { int value; };
// cast to IntNode* only after checking node->kind == NodeKind::Int
```

## Cross-Casting

`dynamic_cast` can also cast between sibling branches in a multiple-inheritance tree — something `static_cast` cannot do:

```cpp
struct A { virtual ~A() = default; };
struct B { virtual ~B() = default; };
struct C : A, B {};

C obj;
A* a = &obj;
B* b = dynamic_cast<B*>(a);   // cross-cast: A* -> B* through the actual C object
```

This is one of the few cases where `dynamic_cast` is the only correct tool.

## Summary Table

| Cast | Checked? | Cost | Use when |
|---|---|---|---|
| Implicit upcast | N/A | Zero | Always (no cast needed) |
| `static_cast` downcast | No | Zero | Guaranteed type, performance-critical |
| `dynamic_cast` downcast | Yes (RTTI) | Small | Type uncertain, safety needed |
| `reinterpret_cast` | Never | Zero | Unrelated types, very low-level |

> **Interview answer:** Upcasting (derived to base) is implicit and always safe. Downcasting (base to derived) requires `dynamic_cast` for safety — it performs a runtime check and returns `nullptr` (or throws `std::bad_cast` for references) if the object is not of the target type. Use `static_cast` for downcasting only when the type is guaranteed by design.
