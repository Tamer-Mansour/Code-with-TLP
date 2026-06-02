# Why Constructors Cannot Be Virtual

Attempting to declare a virtual constructor in C++ is a compile error:

```cpp
class Base {
public:
    virtual Base() {}   // ERROR: constructors cannot be virtual
};
```

This is not an arbitrary restriction — it follows directly from how virtual dispatch and object construction work at the machine level.

## How Virtual Dispatch Works

Virtual dispatch relies on the **vtable pointer** (vptr): a hidden pointer stored inside every polymorphic object that points to the class's virtual function table. When you call a virtual function through a pointer or reference, the runtime dereferences the vptr to find the correct function.

```
+-------------------+
| vptr ------------> [ Base vtable ]
| member data       |   &Base::foo
+-------------------+   &Base::bar
```

The vptr is set by the constructor. That means the vptr does not exist until the constructor runs.

## The Chicken-and-Egg Problem

Virtual dispatch requires a vptr. The vptr is installed by the constructor. Therefore, to dispatch to the right constructor virtually, you would need the vptr to already be set — but the vptr is only set *by* the constructor. This is a fundamental circular dependency.

Put differently:

1. To call a virtual function, the runtime must know the object's dynamic type.
2. The dynamic type of an object is not established until its constructor has run.
3. Therefore, calling the constructor virtually — before the object exists — is impossible.

## What Happens During Construction

The language resolves this by making the vptr installation a multi-step process across the constructor chain:

```cpp
class Base {
public:
    Base() { /* vptr set to Base vtable here */ }
    virtual void identify() { std::cout << "Base\n"; }
};

class Derived : public Base {
public:
    Derived() { /* vptr updated to Derived vtable here */ }
    void identify() override { std::cout << "Derived\n"; }
};
```

When `Derived d;` is constructed:

1. `Base::Base()` runs — vptr points to `Base`'s vtable.
2. `Derived::Derived()` runs — vptr is updated to `Derived`'s vtable.

If you call a virtual function *inside* `Base::Base()`, it dispatches to `Base::identify()`, not `Derived::identify()`, because at that moment the object is still behaving as a `Base`. This is not a bug; it is the defined behavior.

```cpp
class Base {
public:
    Base() { identify(); }            // calls Base::identify — always
    virtual void identify() { std::cout << "Base\n"; }
};

class Derived : public Base {
public:
    Derived() {}
    void identify() override { std::cout << "Derived\n"; }
};

Derived d;   // prints "Base", not "Derived"
```

## The Virtual Constructor Idiom

Although constructors themselves cannot be virtual, you can simulate virtual construction with a **factory method** or the **clone pattern**:

### Factory Method

```cpp
class Shape {
public:
    static Shape* create(const std::string& type);
    virtual ~Shape() = default;
    virtual void draw() = 0;
};

class Circle : public Shape { /* ... */ };
class Rect   : public Shape { /* ... */ };

Shape* Shape::create(const std::string& type) {
    if (type == "circle") return new Circle();
    if (type == "rect")   return new Rect();
    return nullptr;
}
```

### Clone Pattern (Virtual Copy Constructor)

```cpp
class Document {
public:
    virtual ~Document() = default;
    virtual Document* clone() const = 0;  // "virtual constructor"
};

class Report : public Document {
public:
    Report* clone() const override { return new Report(*this); }
};
```

Calling `doc->clone()` produces a new object of the same dynamic type as `doc` — effectively a virtual constructor.

## Summary

| Question | Answer |
|---|---|
| Can a constructor be virtual? | No — compile error |
| Why not? | vptr doesn't exist yet when constructor runs |
| Do virtual calls work inside a constructor? | Yes, but they dispatch to the currently-constructing class's vtable, not a derived class |
| How to achieve virtual construction? | Factory method or clone() virtual method |

> **Interview answer:** Constructors cannot be virtual because virtual dispatch relies on the vptr, which is installed *by* the constructor. Before the constructor runs, there is no object and no vptr to dispatch through. The workaround is a factory method or a virtual `clone()` method that dispatches to a copy constructor of the correct dynamic type.
