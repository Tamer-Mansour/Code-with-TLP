# Classes, Objects, and Constructors

SystemC modules are C++ classes. Before you can read a line of SystemC source, you need a firm grip on how C++ classes, objects, and constructors work — because every `SC_MODULE` you write is just a class that inherits from `sc_module`.

## What Is a Class?

A class is a blueprint that groups **data** (member variables) and **behaviour** (member functions) into one named type. When the program instantiates that blueprint it creates an **object**. The object owns its own copy of every non-static member variable.

```cpp
class Counter {
public:
    int value;          // member variable

    void increment() {  // member function
        value++;
    }
};

int main() {
    Counter c;          // object 'c' is created on the stack
    c.value = 0;
    c.increment();      // c.value is now 1
}
```

## Access Control

| Specifier | Who can access |
|-----------|----------------|
| `public`  | Anyone |
| `protected` | The class itself and derived classes |
| `private` | The class itself only |

SystemC ports (`sc_in`, `sc_out`) are almost always declared `public` so the testbench can bind them. Internal signals are usually `private`.

## Constructors

A constructor is a special member function that **runs automatically when an object is created**. It has the same name as the class and no return type.

```cpp
class Counter {
public:
    int value;

    // Default constructor
    Counter() : value(0) {}           // member-initializer list

    // Parameterised constructor
    Counter(int start) : value(start) {}
};

Counter a;       // value == 0
Counter b(10);   // value == 10
```

The **member-initializer list** (after the `:`) is the preferred way to set member variables. It runs before the constructor body and is the *only* way to initialise `const` members and base-class sub-objects.

## SystemC Module Constructors

Every SystemC module must pass its string name to `sc_module`:

```cpp
#include <systemc.h>

SC_MODULE(Adder) {
    sc_in<int>  a, b;
    sc_out<int> result;

    SC_CTOR(Adder) {          // expands to: Adder(sc_module_name nm) : sc_module(nm)
        SC_METHOD(compute);
        sensitive << a << b;
    }

    void compute() {
        result.write(a.read() + b.read());
    }
};
```

`SC_CTOR` is a macro that hides the boilerplate of forwarding the name string. If you need extra constructor parameters you must write the constructor by hand and call `sc_module(nm)` explicitly in the initialiser list.

## Destructors

A destructor (`~ClassName()`) runs when an object's lifetime ends. It is the right place to free any resources the constructor acquired. In SystemC you rarely write destructors manually because the simulator owns module lifetime, but understanding them is critical for avoiding memory leaks in larger models.

## Common Pitfalls

- **Forgetting the initialiser list** — writing `value = 0` inside the constructor body is an *assignment* that runs after default-initialisation; for complex types this wastes a default-construction step.
- **Shadowing member variables** — using the same name for a parameter and a member without `this->` causes silent bugs.
- **Missing `SC_CTOR` name propagation** — every SystemC module must receive and forward `sc_module_name`; failing to do so causes crashes at elaboration time.

## Worked Example: Parameterised Module

```cpp
SC_MODULE(Multiplier) {
    sc_in<int>  a, b;
    sc_out<int> product;
    int         scale;   // private parameter

    // Custom constructor — SC_CTOR cannot carry extra args
    Multiplier(sc_module_name nm, int scale_factor)
        : sc_module(nm), scale(scale_factor)
    {
        SC_METHOD(compute);
        sensitive << a << b;
    }

    void compute() {
        product.write(a.read() * b.read() * scale);
    }
};
```

> **Interview answer:** A C++ constructor runs when an object is created, initialises member variables via the initialiser list, and in SystemC is the place where processes are registered with `SC_METHOD`/`SC_THREAD` and port sensitivities are declared.
