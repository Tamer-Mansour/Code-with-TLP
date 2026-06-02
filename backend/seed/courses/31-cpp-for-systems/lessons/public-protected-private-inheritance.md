# public, protected, and private Inheritance

C++ gives you three access specifiers for inheritance. Most developers know only `public` inheritance — but `protected` and `private` inheritance serve real purposes and appear frequently in systems and library code.

## The Three Modes

```cpp
class Base {
public:    int pub;
protected: int prot;
private:   int priv;   // never accessible in derived, regardless of mode
};

class D_pub   : public    Base {};   // standard is-a
class D_prot  : protected Base {};   // internal hierarchy
class D_priv  : private   Base {};   // implementation detail
```

The access specifier **lowers** (never raises) the visibility of inherited members from the perspective of code outside the derived class:

| Base member | public inh. | protected inh. | private inh. |
|---|---|---|---|
| `public` | `public` | `protected` | `private` |
| `protected` | `protected` | `protected` | `private` |
| `private` | inaccessible | inaccessible | inaccessible |

The **base's own private members** always remain inaccessible in the derived class, regardless of inheritance mode. They exist in the object's memory layout but cannot be named by derived-class code.

## Public Inheritance — is-a

The most common form. A `Derived*` can be implicitly converted to a `Base*`. This is what makes virtual dispatch work.

```cpp
class Animal {
public:
    virtual void speak() { std::cout << "...\n"; }
    virtual ~Animal() = default;
};

class Dog : public Animal {
public:
    void speak() override { std::cout << "Woof\n"; }
};

void makeSpeak(Animal& a) { a.speak(); }   // works because Dog is-a Animal
```

## Protected Inheritance — hierarchy-internal is-a

With `protected` inheritance, the derived class **is-a** base class from within the class family, but that relationship is hidden from the outside world.

```cpp
class Engine {
public:
    void start() { running_ = true; }
protected:
    bool running_ = false;
};

class Car : protected Engine {
public:
    void drive() {
        start();          // OK: Car can call Engine::start()
        if (running_) std::cout << "Driving\n";
    }
};

int main() {
    Car c;
    c.drive();    // OK
    // c.start(); // ERROR: start() is now protected in Car
}
```

`Car` can use `Engine`'s interface internally, but callers cannot call `Engine` methods directly through a `Car` object. A subclass of `Car` **can** still access them.

## Private Inheritance — implemented-in-terms-of

Private inheritance is the strongest form of hiding. It is semantically similar to composition: the derived class uses the base class's implementation but does not expose the is-a relationship to anyone, including further derived classes.

```cpp
class Timer {
public:
    void reset() { ticks_ = 0; }
    int  elapsed() const { return ticks_; }
private:
    int ticks_ = 0;
};

class RateLimiter : private Timer {   // implemented-in-terms-of Timer
public:
    bool allow() {
        if (elapsed() > 1000) { reset(); return true; }
        return false;
    }
};
```

`RateLimiter` users cannot call `reset()` or `elapsed()`. No implicit conversion from `RateLimiter*` to `Timer*` is allowed outside the class. This prevents misuse of the base-class interface.

**Private inheritance vs composition:**

- Private inheritance gives access to `protected` members and allows overriding virtual functions of the base — composition does not.
- Private inheritance enables the **empty base optimization (EBO)**: if the base is empty (no data members), the compiler is allowed to give it zero size in the derived class. This matters for policy classes and allocators.

```cpp
struct Empty {};           // sizeof(Empty) == 1 (padding)

struct WithMember {
    Empty e;               // sizeof == 1 + padding for next member
    int   x;               // total: 8 bytes (with alignment)
};

struct WithInheritance : Empty {
    int x;                 // total: 4 bytes — EBO kicks in
};
```

## The using Declaration to Restore Visibility

Even with protected or private inheritance you can selectively restore a member's original visibility:

```cpp
class MyQueue : private std::deque<int> {
public:
    using std::deque<int>::push_back;   // restore just this one
    using std::deque<int>::pop_front;
    using std::deque<int>::empty;
    using std::deque<int>::size;
    // everything else remains private
};
```

## Pitfall: Forgetting the Default

If no access specifier is given, the default depends on the keyword used to define the derived type:

- `class Derived : Base` — **private** inheritance
- `struct Derived : Base` — **public** inheritance

This is a common source of confusion, especially when porting code between `class` and `struct`.

> **Interview answer:** Public inheritance models is-a and allows implicit base conversions. Protected inheritance restricts the is-a relationship to the class family. Private inheritance is implemented-in-terms-of and is an alternative to composition that also allows overriding virtual functions and leverages the empty base optimization.
