# Overloading vs Overriding: What Is the Difference?

These two terms sound alike but describe fundamentally different mechanisms. Mixing them up is one of the most common mistakes in C++ interviews.

## Function Overloading

Overloading means defining **multiple functions with the same name but different parameter lists** in the same scope. The compiler selects the best match at compile time based solely on argument types and count — no runtime cost.

```cpp
int    add(int a, int b)       { return a + b; }
double add(double a, double b) { return a + b; }
int    add(int a, int b, int c){ return a + b + c; }

add(1, 2);        // resolves to add(int, int)
add(1.0, 2.0);    // resolves to add(double, double)
add(1, 2, 3);     // resolves to add(int, int, int)
```

Key rules:
- The return type alone **cannot** distinguish overloads.
- `const` on member functions counts as a different signature.
- Works across any functions — free functions, member functions, constructors.

## Function Overriding

Overriding means providing a **new implementation for a virtual function** from a base class in a derived class. The signature (name + parameters + `const`) must match exactly. Resolution happens at **runtime** through the vtable.

```cpp
struct Logger {
    virtual void log(const std::string& msg) const {
        std::cout << "[LOG] " << msg << '\n';
    }
    virtual ~Logger() = default;
};

struct FileLogger : Logger {
    void log(const std::string& msg) const override {   // overrides Logger::log
        std::cout << "[FILE] " << msg << '\n';
    }
};

Logger* l = new FileLogger();
l->log("hello");  // prints "[FILE] hello" — runtime dispatch
delete l;
```

## Side-by-Side Comparison

| Aspect | Overloading | Overriding |
|--------|-------------|------------|
| Location | Same scope / same class | Derived class |
| Signature | Different parameters | Must match base exactly |
| Resolution | Compile time | Runtime (virtual dispatch) |
| `virtual` required | No | Yes (in base) |
| `override` keyword | N/A | Recommended (C++11+) |
| Return type | Can differ (not a differentiator) | Must match (or be covariant) |

## Hiding: The Silent Third Option

A derived class function with the same name but a **different** parameter list does not override — it **hides** all base-class overloads with that name. This is a common source of bugs.

```cpp
struct Base {
    virtual void process(int x)    { std::cout << "Base(int)\n"; }
    virtual void process(double x) { std::cout << "Base(double)\n"; }
};

struct Derived : Base {
    // Hides BOTH base overloads, only overrides the int version
    void process(int x) override { std::cout << "Derived(int)\n"; }
};

Derived d;
d.process(3);      // "Derived(int)"
d.process(3.14);   // "Derived(int)" — double converted to int, base hidden!

Base& b = d;
b.process(3.14);   // "Base(double)" — base is still reachable via base ref
```

To bring hidden base overloads back into scope, use a `using` declaration:

```cpp
struct Derived : Base {
    using Base::process;          // re-expose both base overloads
    void process(int x) override { std::cout << "Derived(int)\n"; }
};
```

## Quick Diagnostic Checklist

1. Same class, different parameters? → **Overloading**
2. Derived class, same signature, base has `virtual`? → **Overriding**
3. Derived class, same name but different parameters? → **Hiding** (usually a bug)

**Interview answer:** Overloading is compile-time selection among same-named functions with different signatures in the same scope; overriding is runtime dispatch where a derived class replaces a base-class virtual function with an identical signature.
