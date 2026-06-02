# Name Hiding and the using Declaration

One of C++'s most surprising inheritance behaviors is **name hiding**: a member in a derived class with the same name as a base-class member hides *all* overloads of that name in the base, even if the signatures are completely different. Understanding this rule prevents subtle bugs and is a common interview topic.

## What Is Name Hiding?

When the compiler looks up a name in a derived class, it searches scopes outward. As soon as it finds the name in one scope it stops — it does not keep looking into base-class scopes. This means a single derived-class declaration can shadow an entire family of base-class overloads.

```cpp
#include <iostream>

struct Base {
    void print(int x)    { std::cout << "Base::print(int) " << x << "\n"; }
    void print(double x) { std::cout << "Base::print(double) " << x << "\n"; }
};

struct Derived : Base {
    void print(const char* s) { std::cout << "Derived::print(str) " << s << "\n"; }
    // hides BOTH Base::print(int) and Base::print(double)
};

int main() {
    Derived d;
    d.print("hello");   // OK
    d.print(42);        // ERROR: no matching function — int version is hidden
    d.print(3.14);      // ERROR: double version is hidden
}
```

This behavior surprises developers who expect overload resolution to consider the entire inheritance chain.

## Why Does C++ Do This?

The rule prevents **accidental overloading across class boundaries**. If a library author adds a new overload to a base class, your derived class should not silently start matching calls that previously had no candidate. Name hiding makes the dependency explicit — you must opt in.

## Restoring Hidden Names with using

The `using` declaration brings a base-class name into the derived-class scope, making all overloads visible again:

```cpp
struct Derived : Base {
    using Base::print;           // restore all Base::print overloads

    void print(const char* s) { std::cout << "Derived::print(str) " << s << "\n"; }
};

int main() {
    Derived d;
    d.print("hello");   // Derived::print(const char*)
    d.print(42);        // Base::print(int)   -- now visible
    d.print(3.14);      // Base::print(double) -- now visible
}
```

The `using Base::print;` line imports the name, not a specific overload. All overloads of `Base::print` participate in overload resolution together with the derived-class overloads.

## Name Hiding vs Overriding

These are different concepts:

| Concept | Requires virtual? | Resolved at? |
|---|---|---|
| Overriding | Yes | Runtime (vtable) |
| Hiding | No | Compile time |

A non-virtual function in a derived class with the same signature as a base function **hides** it — it does not override it:

```cpp
struct Base {
    void show() { std::cout << "Base\n"; }
};

struct Derived : Base {
    void show() { std::cout << "Derived\n"; }   // hides, does not override
};

Derived d;
d.show();            // Derived::show()
Base& b = d;
b.show();            // Base::show()  -- NOT Derived::show() (no virtual dispatch)
```

If `show()` were `virtual` in `Base`, `b.show()` would call `Derived::show()`.

## Accessing a Hidden Name Explicitly

Even without `using`, you can always call a hidden base function using scope resolution:

```cpp
struct Derived : Base {
    void show() {
        Base::show();            // explicitly call the hidden version
        std::cout << "Derived extra\n";
    }
};
```

This is the standard pattern for **extending** (not replacing) base behavior.

## Practical Example: Policy Classes

Name hiding combined with `using` is used in policy-based design to selectively expose base capabilities:

```cpp
template <typename Policy>
class Container : private Policy {
public:
    using Policy::allocate;     // expose only what clients need
    using Policy::deallocate;
};
```

## Common Pitfalls

- Adding an overload to a base class silently hides it in all derived classes unless they use `using`.
- Using `using` with a private-inherited base to selectively make members public:

```cpp
class MyStack : private std::vector<int> {
public:
    using std::vector<int>::size;    // expose size but not everything else
    using std::vector<int>::empty;
};
```

- Confusing hiding with overriding when debugging unexpected function calls — check whether the base function is `virtual`.

> **Interview answer:** Name hiding occurs when a derived-class member declaration shadows all base-class overloads of the same name, even those with different signatures. The `using Base::name;` declaration restores all those overloads to participate in overload resolution inside the derived class.
