# Class vs Object: What Is the Difference?

A **class** is a blueprint; an **object** is a concrete instance built from that blueprint. This distinction sits at the heart of object-oriented programming and comes up in nearly every C++ interview.

## The Blueprint Analogy

Think of a class the way an architect thinks of a floor plan. The floor plan describes rooms, doors, and wiring — but it is not a house you can live in. You must *build* a house from the plan. Every house built from the same plan is its own object, occupying its own memory, with its own state (furniture arrangement, paint colour, temperature).

```cpp
// Blueprint — no memory allocated yet
class Thermostat {
public:
    int temperature;
    void setTemp(int t) { temperature = t; }
};

// Objects — each occupies memory, each has independent state
Thermostat kitchen;          // object 1
Thermostat bedroom;          // object 2

kitchen.setTemp(22);
bedroom.setTemp(18);
// kitchen.temperature == 22, bedroom.temperature == 18
```

## What a Class Defines

A class groups together:

- **Data members** — the state each object carries (e.g., `temperature`).
- **Member functions (methods)** — the behaviour objects expose (e.g., `setTemp`).
- **Access rules** — `public`, `private`, `protected` labels that control visibility.
- **Special functions** — constructors, destructors, copy/move operations.

The class itself is merely a *type definition*. The compiler uses it as a template when generating code; no storage is allocated until you instantiate an object.

## Instantiation: Bringing Objects to Life

```cpp
Thermostat t1;           // automatic (stack) object — destroyed at end of scope
Thermostat* t2 = new Thermostat();  // dynamic (heap) object — destroyed with delete
delete t2;
```

Each object gets its own copy of every **non-static** data member. Member *functions* are shared in the compiled code; only the data differs per instance.

## Class vs Type vs Object — Quick Comparison

| Term    | What it is                          | Example                  |
|---------|-------------------------------------|--------------------------|
| Class   | User-defined type / blueprint       | `class Thermostat { … }` |
| Type    | Broader concept (includes built-ins)| `int`, `Thermostat`      |
| Object  | Named instance with its own storage | `Thermostat kitchen;`    |
| Value   | The data an object holds at runtime | `kitchen.temperature`    |

## Common Pitfall: Confusing the Type with an Instance

Beginners often write code like:

```cpp
Thermostat.setTemp(22);  // ERROR — calling on the type, not an object
```

You must always call methods on an *instance* (or a pointer to one). The class name alone is not callable.

## Why It Matters for Systems Programming

In OS kernels and embedded code, every byte of memory is precious. Understanding that a class definition costs **zero** runtime memory, while each object costs `sizeof(ClassName)` bytes, lets you reason about memory layout, cache behaviour, and structure packing.

```cpp
#include <iostream>
int main() {
    std::cout << sizeof(Thermostat) << '\n'; // prints size of one object
}
```

## Worked Example: Packet Header

```cpp
class PacketHeader {
public:
    uint16_t src_port;
    uint16_t dst_port;
    uint32_t seq_num;

    void print() const {
        // prints header fields
    }
};

PacketHeader p1, p2;  // two independent headers in stack memory
p1.src_port = 8080;
p2.src_port = 443;
```

`PacketHeader` is 8 bytes. Two objects mean 16 bytes total — predictable, zero overhead.

---

> **Interview answer:** "A class is a compile-time blueprint that defines a type's data and behaviour. An object is a runtime instance of that class, occupying its own memory with its own state. Many objects can be created from one class, each independent."
