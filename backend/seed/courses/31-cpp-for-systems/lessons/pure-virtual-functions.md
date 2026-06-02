# Pure Virtual Functions and = 0

A **pure virtual function** is a virtual function that has no implementation in the base class and forces every concrete derived class to provide one. You declare it by appending `= 0` to the function signature.

```cpp
class Shape {
public:
    virtual double area() const = 0;   // pure virtual
    virtual void   draw()       = 0;   // pure virtual
    virtual ~Shape() = default;
};
```

## What `= 0` Actually Means

The `= 0` syntax is a declaration, not an assignment. It tells the compiler:

- This function **must** be overridden in any non-abstract derived class.
- The base class is now **abstract** — you cannot instantiate `Shape` directly.
- The vtable entry exists, but the default slot points to a linker symbol (`__cxa_pure_virtual` on GCC/Clang) that aborts the program if called at runtime.

## Overriding in a Derived Class

```cpp
class Circle : public Shape {
    double radius_;
public:
    explicit Circle(double r) : radius_(r) {}

    double area() const override { return 3.14159 * radius_ * radius_; }
    void   draw()       override { /* render circle */ }
};

// Shape s;      // ERROR: cannot instantiate abstract class
Circle c(5.0);   // OK
Shape* p = &c;   // OK: pointer/reference to abstract type is fine
```

The `override` keyword is not required but is strongly recommended — the compiler will catch typos in the function signature that would silently create a new virtual function instead of overriding the intended one.

## Partial Override — Still Abstract

If a derived class overrides only *some* pure virtual functions, it remains abstract:

```cpp
class ColoredShape : public Shape {
public:
    void draw() override { /* partial implementation */ }
    // area() still pure virtual — ColoredShape is still abstract
};
```

## Common Pitfalls

| Pitfall | Effect | Fix |
|---------|--------|-----|
| Forgetting `override` | Typo creates a new function, base stays pure | Always write `override` |
| Calling pure virtual in constructor | Undefined behaviour (UB) | Never call virtuals in ctor/dtor |
| Missing `virtual ~Base()` | Derived destructor not called via base pointer | Always declare virtual dtor |
| Assuming no body is allowed | Pure virtual CAN have a body (see later lesson) | Understand the distinction |

## Why Use Pure Virtual Functions?

- **Enforces a contract.** Every driver, plugin, or strategy must implement the required interface.
- **Documents intent.** Readers immediately see which functions define the abstraction boundary.
- **Enables polymorphism.** Base-class pointers/references work without knowing the concrete type.

In systems and OS code, pure virtual functions appear in HAL (Hardware Abstraction Layer) designs where `Device`, `FileSystem`, or `Scheduler` base classes define the mandatory operations that every concrete implementation must provide.

> **Interview answer:** A pure virtual function is declared with `= 0`, makes the class abstract so it cannot be instantiated directly, and forces every concrete derived class to provide an implementation — giving you a compile-time-enforced interface contract.
