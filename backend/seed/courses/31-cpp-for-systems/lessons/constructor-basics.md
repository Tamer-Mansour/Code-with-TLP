# Constructors: Default, Parameterized, and Implicit

A constructor is a special member function that runs automatically whenever an object is created. It shares the class name, has no return type, and its job is to put the object into a valid initial state. Understanding how and when each constructor variant fires is one of the most tested C++ interview topics.

## The Default Constructor

A default constructor takes no arguments (or has all arguments defaulted). If you declare no constructors at all, the compiler synthesizes one for you — but only if you do not declare *any* other constructor.

```cpp
class Counter {
public:
    int value;
    Counter() : value(0) {}   // user-defined default constructor
};

Counter c;          // calls Counter()
Counter arr[10];    // calls Counter() ten times
```

**Pitfall:** If you declare a parameterized constructor and forget to write a default one, `Counter c;` becomes a compile error.

## Parameterized Constructors

Any constructor with parameters is a parameterized constructor. Overloads are resolved the same way as regular functions.

```cpp
class Point {
public:
    double x, y;

    Point(double x, double y) : x(x), y(y) {}
};

Point p1(1.0, 2.5);        // direct initialization
Point p2 = Point(3.0, 4.0); // also fine
```

You can provide default argument values to merge the default and parameterized forms:

```cpp
Point(double x = 0.0, double y = 0.0) : x(x), y(y) {}
```

## Implicit (Compiler-Generated) Constructors

The compiler can silently generate up to three constructors when you don't declare them yourself:

| Generated constructor | When generated |
|-----------------------|----------------|
| Default `T()` | No user-declared constructors |
| Copy `T(const T&)` | No user-declared copy/move constructor or destructor |
| Move `T(T&&)` | No user-declared copy/move ops or destructor |

These implicit constructors perform **memberwise** initialization: each member is copy- or move-constructed from the source.

```cpp
class Box {
public:
    int width, height;
    // No constructors declared — compiler generates all three
};

Box a;          // default: width and height are indeterminate (POD)
Box b = a;      // copy constructor
Box c = Box{};  // value-initialization: zeros width and height
```

**Pitfall:** `Box a;` leaves `a.width` and `a.height` with indeterminate values (they are not zero). Use `Box a{};` or `Box a = {};` for zero-initialization.

## Initialization Syntax

C++11 introduced uniform (brace) initialization, which works everywhere:

```cpp
Point p1(1.0, 2.0);   // direct initialization (old style)
Point p2{1.0, 2.0};   // list initialization (C++11)
Point p3 = {1.0, 2.0}; // copy-list initialization
```

Brace initialization prevents narrowing conversions (e.g., double → int silently) and should be preferred in modern code.

## A Worked Example

```cpp
#include <iostream>
#include <string>

class Server {
    std::string host;
    int port;
public:
    Server()                        : host("localhost"), port(8080) {}
    Server(std::string h, int p)    : host(h), port(p) {}
    Server(int p)                   : host("localhost"), port(p) {}

    void info() const {
        std::cout << host << ":" << port << "\n";
    }
};

int main() {
    Server s1;            // localhost:8080
    Server s2("prod", 443);
    Server s3(9090);      // localhost:9090

    s1.info();
    s2.info();
    s3.info();
}
```

## Common Pitfalls

- **Most Vexing Parse:** `Server s();` declares a *function*, not an object. Use `Server s;` or `Server s{}`.
- **Shadowing parameter names:** Using the same name for a member and a parameter (`int port; Server(int port) { port = port; }`) leaves the member unchanged. Fix with `this->port = port` or use a member-initializer list.
- **Forgetting the default constructor** after adding a parameterized one breaks all call sites that relied on the implicit default.

> **Interview answer:** A default constructor takes no arguments and is synthesized by the compiler only when you declare no constructors yourself. A parameterized constructor accepts arguments to set the object's initial state. Both fire at object creation, before the object is used.
