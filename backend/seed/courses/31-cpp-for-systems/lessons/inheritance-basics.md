# What Is Inheritance and When to Use It

Inheritance is one of the core mechanisms of object-oriented programming. It lets one class (the **derived class**) acquire the data members and member functions of another class (the **base class**), then extend or override them. In C++ the syntax is simple, but the semantics run deep — and misusing inheritance is one of the most common design errors in systems code.

## The Basic Syntax

```cpp
class Animal {
public:
    std::string name;
    void breathe() { std::cout << name << " breathes\n"; }
};

class Dog : public Animal {   // Dog IS-A Animal
public:
    void bark() { std::cout << name << " barks\n"; }
};

int main() {
    Dog d;
    d.name = "Rex";
    d.breathe();   // inherited from Animal
    d.bark();      // defined in Dog
}
```

`Dog` automatically gains `name` and `breathe()` without redeclaring them. The `public` keyword before `Animal` is the **access specifier** — it controls how inherited members are visible to the outside world (covered in detail in the next lesson).

## What Gets Inherited

| Member kind | Inherited? |
|---|---|
| Public and protected data members | Yes |
| Public and protected member functions | Yes |
| Private members | No (exist in object, but inaccessible) |
| Constructors and destructor | No (but they are called) |
| Assignment operator | Not automatically |
| `friend` declarations | No |

Constructors are not inherited by default in C++03. C++11 introduced `using Base::Base;` to pull them in explicitly.

## When Inheritance Is Appropriate

Use inheritance when the relationship is truly **is-a**:

- `Dog` is-a `Animal`
- `TCPSocket` is-a `Socket`
- `LinuxProcess` is-a `Process`

A concrete checklist:

- The derived class can be substituted everywhere the base class is expected (Liskov Substitution Principle).
- The derived class needs to override behavior, not just reuse code.
- You need runtime polymorphism through virtual functions.

## When Inheritance Is the Wrong Tool

Do not inherit just to reuse code. If you only need the functionality of another class without the conceptual hierarchy, use **composition** (has-a). For example, a `Car` has-a `Engine` — inheriting from `Engine` would be bizarre and would expose all of `Engine`'s interface to `Car`'s users.

Common red flags:

- You inherit from a class but override nearly every method.
- The derived class cannot fulfill the base class contract.
- You are inheriting only for one or two utility functions.
- The base class is not designed for inheritance (no virtual destructor).

## The Cost of Inheritance in Systems Code

Inheritance is not free:

- **Virtual dispatch** (when virtual functions are involved) adds an indirection through the vtable — typically one pointer dereference, ~1-4 ns.
- Each object with virtual functions carries a hidden `vptr` (usually 8 bytes on 64-bit).
- Deep inheritance hierarchies make code harder to reason about and can reduce cache efficiency.

In latency-critical paths (kernel drivers, real-time systems, HPC) you may prefer templates (static polymorphism) over virtual inheritance to eliminate runtime overhead.

## A Minimal Working Example

```cpp
#include <iostream>
#include <string>

class Shape {
public:
    std::string color;
    void describe() const {
        std::cout << "I am a " << color << " shape\n";
    }
    virtual double area() const { return 0.0; }
    virtual ~Shape() = default;   // always virtual if used polymorphically
};

class Circle : public Shape {
public:
    double radius;
    double area() const override { return 3.14159 * radius * radius; }
};

int main() {
    Circle c;
    c.color  = "red";
    c.radius = 5.0;
    c.describe();                           // inherited
    std::cout << "Area: " << c.area() << "\n"; // overridden
}
```

> **Interview answer:** Inheritance models an is-a relationship and lets a derived class reuse and override base-class behavior. Use it when you need substitutability and polymorphism; prefer composition when you only need code reuse.
