# Inheritance and Virtual Functions

SystemC is built on a deep inheritance hierarchy. `SC_MODULE` inherits from `sc_module`, which inherits from `sc_object`. Every port type you use (`sc_in<T>`, `sc_out<T>`) sits in its own hierarchy. Understanding inheritance and virtual functions is therefore not academic — it is the mechanism that makes the simulator work.

## Inheritance Basics

Inheritance lets one class (the **derived** class) reuse and extend another (the **base** class).

```cpp
class Animal {
public:
    std::string name;
    Animal(const std::string& n) : name(n) {}
    void breathe() { /* shared behaviour */ }
};

class Dog : public Animal {   // Dog IS-AN Animal
public:
    Dog(const std::string& n) : Animal(n) {}   // forward to base ctor
    void bark() { /* Dog-specific behaviour */ }
};

Dog d("Rex");
d.breathe();   // inherited
d.bark();      // own
```

The `public` inheritance keyword means every `public` member of `Animal` stays `public` in `Dog`. This is the standard form you'll see everywhere in SystemC code.

## Virtual Functions and Polymorphism

A **virtual function** allows a base-class pointer or reference to call the correct overridden version at runtime.

```cpp
class Shape {
public:
    virtual double area() const = 0;   // pure virtual — must be overridden
    virtual ~Shape() {}                // always virtual in a polymorphic base
};

class Circle : public Shape {
    double r;
public:
    Circle(double radius) : r(radius) {}
    double area() const override { return 3.14159 * r * r; }
};

class Square : public Shape {
    double s;
public:
    Square(double side) : s(side) {}
    double area() const override { return s * s; }
};

void printArea(const Shape& sh) {      // works for ANY Shape
    std::cout << sh.area() << "\n";
}
```

The keyword `override` (C++11) asks the compiler to verify that you are actually overriding a base-class virtual — it catches spelling mistakes that would otherwise silently create a new function.

## Abstract Classes

A class with at least one **pure virtual** function (`= 0`) is **abstract** — you cannot instantiate it directly. SystemC's `sc_interface` is a prime example: it declares pure virtual methods (`read`, `write`, etc.) that channel implementations must provide.

## How SystemC Uses Inheritance

| SystemC concept | Base class | Key virtual |
|-----------------|------------|-------------|
| Every module | `sc_module` | `before_end_of_elaboration`, `end_of_elaboration`, `start_of_simulation`, `end_of_simulation` |
| Every channel | `sc_prim_channel` or `sc_channel` | `update()` |
| Port binding check | `sc_interface` | `register_port()` |

The simulator calls these virtual hooks at the right phase; your derived class just overrides the ones it needs.

## Virtual Destructors

If you ever delete a derived object through a base-class pointer, the base destructor **must** be virtual — otherwise only the base destructor runs and the derived part leaks.

```cpp
Shape* s = new Circle(5.0);
delete s;   // calls Circle::~Circle() only if ~Shape() is virtual
```

Forgetting this is a classic C++ pitfall and a common interview question.

## Multiple Inheritance

SystemC modules sometimes use multiple inheritance — for example, a module that is also an interface:

```cpp
class MyFifo : public sc_module,
               public MyFifoIf   // implements the interface
{
    ...
};
```

When multiple bases each have their own vtable, C++ uses **virtual base classes** to avoid duplicated sub-objects. SystemC's `sc_interface` is declared as a virtual base in port templates for exactly this reason.

## Common Pitfalls

- **Non-virtual destructor in a polymorphic base** — always add `virtual ~Base() {}`.
- **Slicing** — assigning a derived object to a base *value* (not pointer/reference) silently strips the derived part.
- **Calling virtual functions in constructors** — at construction time the vtable points to the base version, not the derived one; the call does not dispatch correctly.

> **Interview answer:** Virtual functions enable runtime polymorphism: the compiler stores a pointer to each class's vtable in every object, and a call through a base pointer resolves to the correct derived override at runtime. In SystemC this lets the simulator call module lifecycle hooks (`end_of_elaboration`, etc.) without knowing the concrete module type.
