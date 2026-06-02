# Construction and Destruction Order in Hierarchies

When objects are created and destroyed in an inheritance hierarchy, the C++ standard defines a strict order. Violations — or misunderstandings — of this order are a frequent source of subtle bugs.

## Construction Order (Top-Down)

Construction always flows from the most-base class to the most-derived class:

1. **Virtual base classes** (if any) — in the order they appear in depth-first, left-to-right traversal of the hierarchy, each constructed only once.
2. **Direct base classes** — in left-to-right declaration order.
3. **Member variables** — in declaration order within the class.
4. **Constructor body** — runs last.

```cpp
#include <iostream>

struct A {
    A() { std::cout << "A()\n"; }
    ~A() { std::cout << "~A()\n"; }
};

struct B : A {
    B() { std::cout << "B()\n"; }
    ~B() { std::cout << "~B()\n"; }
};

struct C : B {
    C() { std::cout << "C()\n"; }
    ~C() { std::cout << "~C()\n"; }
};

// Construction: A() → B() → C()
// Destruction:  ~C() → ~B() → ~A()
```

## Destruction Order (Bottom-Up)

Destruction is the exact reverse of construction:

1. **Destructor body** runs first.
2. **Members** destroyed in **reverse** declaration order.
3. **Direct base classes** destroyed in **reverse** declaration order.
4. **Virtual base classes** destroyed last.

This mirror symmetry guarantees that no object ever depends on a sub-object that has already been destroyed.

## Multiple Inheritance

```cpp
struct Left {
    Left() { std::cout << "Left()\n"; }
    ~Left() { std::cout << "~Left()\n"; }
};

struct Right {
    Right() { std::cout << "Right()\n"; }
    ~Right() { std::cout << "~Right()\n"; }
};

struct Both : Left, Right {   // Left before Right in declaration
    Both() { std::cout << "Both()\n"; }
    ~Both() { std::cout << "~Both()\n"; }
};

// Construction: Left() → Right() → Both()
// Destruction:  ~Both() → ~Right() → ~Left()
```

## Members vs. Base Classes

Members of a class are constructed after the base classes and in declaration order:

```cpp
struct Logger {
    Logger(const char* tag) { std::cout << tag << " Logger()\n"; }
    ~Logger() { std::cout << "~Logger()\n"; }
};

struct Widget : A {       // A is a base class
    Logger l1{"l1"};      // member 1
    Logger l2{"l2"};      // member 2
    Widget() { std::cout << "Widget()\n"; }
    ~Widget() { std::cout << "~Widget()\n"; }
};

// Construction: A() → l1 Logger() → l2 Logger() → Widget()
// Destruction:  ~Widget() → ~l2 Logger() → ~l1 Logger() → ~A()
```

## Virtual Base Classes and Diamond Inheritance

Virtual base classes are constructed before any non-virtual bases, and only once even if they appear multiple times in the hierarchy. The **most-derived** class is responsible for constructing them.

```cpp
struct Base {
    int x;
    Base(int x) : x(x) { std::cout << "Base(" << x << ")\n"; }
    virtual ~Base() = default;
};

struct Left  : virtual Base { Left()  : Base(1) { std::cout << "Left()\n"; } };
struct Right : virtual Base { Right() : Base(2) { std::cout << "Right()\n"; } };

struct Diamond : Left, Right {
    Diamond() : Base(99), Left(), Right() {    // must init Base here
        std::cout << "Diamond()\n";
    }
};
// Output:
// Base(99)   ← virtual base, constructed by Diamond with x=99
// Left()
// Right()
// Diamond()
```

The `Base(1)` and `Base(2)` in `Left` and `Right`'s initializer lists are **ignored** when constructing a `Diamond`. Only the most-derived class's initializer for the virtual base is used.

## Calling Virtual Functions During Construction

As established in the previous lesson, calling a virtual function during construction dispatches to the currently-constructing class's version — never a more-derived override. The same applies during destruction.

```cpp
struct Safe {
    virtual void setup() { std::cout << "Safe::setup()\n"; }
    Safe() { setup(); }         // calls Safe::setup(), not an override
};

struct Risky : Safe {
    int* data;
    void setup() override {
        data = new int[10];    // DANGEROUS: called during Safe's ctor,
                               // but data member of Risky not yet initialized
    }
    Risky() : Safe(), data(nullptr) {}
};
```

**Rule:** avoid calling virtual functions in constructors or destructors. If shared initialization is needed, use a two-phase initialization pattern or a factory.

## Quick Reference

| Phase | Order |
|---|---|
| Virtual bases | Declaration order, depth-first, left-to-right |
| Direct bases | Left-to-right declaration order |
| Members | Declaration order in the class |
| Constructor body | Last |
| Destruction | Exact reverse of construction |

> **Interview answer:** Construction flows top-down: virtual bases first (once), then direct bases left-to-right, then members in declaration order, then the constructor body. Destruction is the exact reverse. Virtual function calls inside constructors dispatch to the currently-constructing class, not derived overrides, because the vptr is not yet fully updated.
