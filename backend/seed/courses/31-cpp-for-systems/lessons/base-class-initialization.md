# Calling Base Constructors and Member Access

When a derived class object is created, the base class sub-object must be initialized first. C++ enforces a strict construction and destruction order, and understanding it prevents some of the most confusing bugs in class hierarchies.

## Construction Order

1. Base class constructor (depth-first, left-to-right for multiple bases)
2. Derived class member variables (in declaration order)
3. Derived class constructor body

Destruction is the **exact reverse**: derived body, derived members, base destructor.

```cpp
#include <iostream>

struct Base {
    Base()  { std::cout << "Base()\n"; }
    ~Base() { std::cout << "~Base()\n"; }
};

struct Derived : Base {
    int x;
    Derived(int v) : Base(), x(v) {   // Base() called in initializer list
        std::cout << "Derived(" << v << ")\n";
    }
    ~Derived() { std::cout << "~Derived()\n"; }
};

int main() {
    Derived d(42);
}
// Output:
// Base()
// Derived(42)
// ~Derived()
// ~Base()
```

## Calling a Specific Base Constructor

Use the **member initializer list** to pass arguments to the base constructor:

```cpp
class Socket {
    int fd_;
public:
    explicit Socket(int fd) : fd_(fd) {}
    int fd() const { return fd_; }
};

class TCPSocket : public Socket {
    uint16_t port_;
public:
    TCPSocket(int fd, uint16_t port)
        : Socket(fd),      // must be first in the list
          port_(port)
    {}
};
```

If you omit the base in the initializer list, the **default constructor** of the base is called. If the base has no default constructor, the code will not compile — a common compile error when adding a constructor with parameters to a base class.

## Inherited Constructors (C++11)

You can pull all base constructors into the derived class with a single `using` declaration:

```cpp
class Base {
public:
    Base(int x) {}
    Base(int x, double y) {}
};

class Derived : public Base {
public:
    using Base::Base;   // inherits Base(int) and Base(int, double)
    // derived-specific data members get default-initialized
};

Derived d1(5);        // calls Base(int)
Derived d2(5, 3.14);  // calls Base(int, double)
```

Inherited constructors do **not** initialize derived-class members unless those members have in-class initializers.

## Accessing Base Members

Inside derived class methods, access base members directly by name (if visible) or qualify with `Base::`:

```cpp
class Animal {
public:
    std::string name;
    void breathe() const { std::cout << name << " breathes\n"; }
};

class Dog : public Animal {
public:
    void greet() const {
        Animal::breathe();          // explicit base qualification
        std::cout << name << " wags tail\n";   // direct access
    }
};
```

Explicit `Base::` qualification is required when:

- You want to call the **base version** of an overridden (non-virtual or virtual) function.
- A derived member **hides** a base member with the same name.

## The protected Access Specifier

`protected` members are accessible in the derived class but not from outside the class hierarchy. This is the intended way to expose internals to subclasses:

```cpp
class Buffer {
protected:
    char*  data_;
    size_t size_;
public:
    Buffer(size_t n) : data_(new char[n]), size_(n) {}
    virtual ~Buffer() { delete[] data_; }
};

class RingBuffer : public Buffer {
    size_t head_ = 0, tail_ = 0;
public:
    RingBuffer(size_t n) : Buffer(n) {}
    void write(char c) { data_[tail_++ % size_] = c; }   // uses protected data_
};
```

## Common Pitfall: Calling Virtual Functions from Constructors

During base-class construction, the derived class does not yet exist. If you call a `virtual` function from a base constructor, **it resolves to the base version**, not the derived override — a frequent source of bugs.

```cpp
struct Base {
    Base() { init(); }                    // BAD: virtual dispatch not active yet
    virtual void init() { std::cout << "Base::init\n"; }
};

struct Derived : Base {
    void init() override { std::cout << "Derived::init\n"; }
};

Derived d;   // prints "Base::init", not "Derived::init"
```

The fix is to call `init()` explicitly after construction, or use a factory function.

## Destruction and Virtual Destructors

If you ever delete a derived object through a base pointer, the base destructor **must** be `virtual`. Otherwise only the base destructor is called, causing a resource leak.

```cpp
struct Base {
    virtual ~Base() = default;   // mandatory for polymorphic base classes
};

struct Derived : Base {
    std::vector<int> data;       // destructor cleans this up correctly
};

Base* p = new Derived();
delete p;   // calls ~Derived() then ~Base() — correct
```

> **Interview answer:** Base constructors are called before derived constructors and must be invoked through the member initializer list. Virtual destructors are required in any class intended to be used polymorphically to ensure proper cleanup through base pointers.
