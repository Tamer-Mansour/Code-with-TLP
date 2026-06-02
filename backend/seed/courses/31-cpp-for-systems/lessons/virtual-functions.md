# Virtual Functions and the override Keyword

A **virtual function** is a member function declared with the `virtual` keyword in a base class. When you call it through a base-class pointer or reference, C++ dispatches to the most-derived override — not the base-class version. Without `virtual`, the call is bound at compile time based on the static type of the pointer.

## Declaring and Overriding

```cpp
struct Animal {
    virtual void speak() const {          // virtual in base
        std::cout << "...\n";
    }
    virtual ~Animal() = default;          // always virtual if polymorphic
};

struct Dog : Animal {
    void speak() const override {         // override in derived
        std::cout << "Woof\n";
    }
};

struct Cat : Animal {
    void speak() const override {
        std::cout << "Meow\n";
    }
};

Animal* a = new Dog();
a->speak();   // prints "Woof" — runtime dispatch
delete a;
```

Without `virtual`, `a->speak()` would always print `"..."` because the compiler sees the static type `Animal*`.

## The `override` Keyword

`override` (added in C++11) asks the compiler to verify that the function actually overrides a virtual function in a base class. Without it, a typo silently creates a new function instead of overriding.

```cpp
struct Base {
    virtual void process(int x) const;
};

struct Derived : Base {
    // BAD: "prosses" is not an override — it is a new function,
    // no compiler error without 'override'
    virtual void prosses(int x) const;

    // GOOD: compiler error if signature does not match Base::process
    void process(int x) const override;
};
```

Always use `override`. It costs nothing at runtime and catches an entire class of bugs.

## Pure Virtual Functions and Abstract Classes

A **pure virtual function** is declared with `= 0`. A class with at least one pure virtual function is **abstract** — you cannot instantiate it directly. Derived classes must provide an implementation (or remain abstract themselves).

```cpp
struct Drawable {
    virtual void draw() const = 0;        // pure virtual
    virtual ~Drawable() = default;
};

struct Circle : Drawable {
    void draw() const override {
        std::cout << "Drawing circle\n";
    }
};

// Drawable d;      // ERROR: cannot instantiate abstract class
Drawable* d = new Circle();
d->draw();           // OK
delete d;
```

Pure virtuals are the idiomatic way to define C++ interfaces.

## Virtual Destructors

If a class is meant to be used polymorphically (stored behind a base pointer), its destructor **must** be virtual. Otherwise, deleting a derived object through a base pointer is undefined behavior.

```cpp
struct Base {
    ~Base() { }           // NOT virtual — dangerous!
};

struct Derived : Base {
    int* data;
    Derived() : data(new int[100]) {}
    ~Derived() { delete[] data; }  // never called if Base::~Base is not virtual
};

Base* b = new Derived();
delete b;   // UB: Derived::~Derived not called, data leaked
```

**Rule of thumb:** if a class has at least one virtual function, make the destructor virtual too.

## Common Pitfalls

- Forgetting `virtual` on the destructor in a polymorphic base class.
- Overloading instead of overriding (different signature silently creates a new function).
- Calling a virtual function inside a constructor or destructor — the vtable is not yet fully constructed, so only the current class's version runs.

```cpp
struct Base {
    Base() { init(); }          // calls Base::init, NOT Derived::init
    virtual void init() { std::cout << "Base::init\n"; }
};

struct Derived : Base {
    void init() override { std::cout << "Derived::init\n"; }
};

Derived d;   // prints "Base::init" — surprising!
```

**Interview answer:** A virtual function enables runtime dispatch through a base pointer or reference; the `override` keyword asks the compiler to confirm the signature matches a base-class virtual, preventing silent new-function bugs.
