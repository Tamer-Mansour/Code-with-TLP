# Can a Virtual Function Be inline?

Yes — declaring a virtual function `inline` is legal and sometimes useful, but the `inline` hint applies only to **direct calls**, not to virtual dispatch. Understanding the distinction prevents a common misconception.

## What `inline` Does and Does Not Do

`inline` has two effects in C++:

1. **Linkage hint** — tells the linker to allow multiple identical definitions (one per translation unit) without an error. This is its only guaranteed effect.
2. **Optimization suggestion** — hints that the compiler may substitute the function body at the call site. The compiler is free to ignore this.

Virtual functions called through a base pointer or reference are dispatched through the vtable at runtime. The compiler cannot substitute an unknown body at the call site, so the `inline` hint has **no effect** on virtual dispatch.

## When `inline virtual` Does Help

When the compiler can see the **concrete type** (static dispatch / devirtualization), it may inline an `inline virtual` function:

```cpp
struct Shape {
    virtual double area() const = 0;
    virtual ~Shape() = default;
};

struct Circle : Shape {
    double r;
    Circle(double r) : r(r) {}

    // inline virtual — body in header, linkage-safe, inlinable on devirtualized calls
    inline double area() const override {
        return 3.14159265358979 * r * r;
    }
};

void foo() {
    Circle c(5.0);
    double a = c.area();          // direct call → compiler may inline
    Shape* s = &c;
    double b = s->area();         // virtual dispatch → NOT inlined (vtable used)
}
```

Compiling with `-O2` on GCC/Clang: `c.area()` is typically inlined; `s->area()` is not.

## Defining Virtual Functions in the Class Body (Implicit inline)

Any function defined inside a class body is implicitly `inline` regardless of whether it is virtual:

```cpp
struct Widget {
    virtual void draw() {          // implicitly inline
        std::cout << "Widget\n";
    }
};
```

This is common and perfectly valid. It affects linkage (allowing the definition in multiple translation units via a shared header) but does not guarantee inlining through a vtable call.

## Pure Virtual Functions Can Have Bodies

A pure virtual function (`= 0`) can optionally have a body. It must be defined **outside** the class body:

```cpp
struct Base {
    virtual void init() = 0;
};

// Valid definition of a pure virtual function
void Base::init() {
    std::cout << "Base::init default\n";
}

struct Derived : Base {
    void init() override {
        Base::init();              // explicit static call to base body
        std::cout << "Derived::init\n";
    }
};
```

This pattern lets you provide a default implementation that derived classes can opt into with `Base::init()`.

## Summary Table

| Call site | `inline virtual` inlined? |
|-----------|--------------------------|
| Direct call (`obj.f()`, known concrete type) | Possibly yes (compiler decides) |
| Virtual dispatch (`ptr->f()`, unknown type) | No |
| Devirtualized by compiler (`-O2` + final / local type) | Possibly yes |

## Key Takeaway

`inline virtual` is not contradictory or harmful. The `inline` keyword governs **linkage and direct-call inlining**; `virtual` governs **dispatch**. They operate on different dimensions. Putting a virtual function's body in the class definition is the standard idiom — just do not expect the `inline` hint to remove vtable overhead on polymorphic calls.

**Interview answer:** A virtual function can be `inline`, and the compiler may inline it when the concrete type is statically known (direct or devirtualized call); when dispatched through the vtable at runtime the inline hint is ignored because the callee is not known at compile time.
