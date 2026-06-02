# Delegating and Inheriting Constructors

## The Problem: Constructor Code Duplication

Before C++11, classes with multiple constructors often repeated the same initialization logic:

```cpp
class Server {
    std::string host;
    int port;
    bool ssl;
    void init() { /* shared setup */ }
public:
    Server()                         { host = "localhost"; port = 8080; ssl = false; init(); }
    Server(int p)                    { host = "localhost"; port = p;    ssl = false; init(); }
    Server(std::string h, int p)     { host = h;           port = p;    ssl = false; init(); }
};
```

This is fragile: change the shared logic in one place and forget another.

## Delegating Constructors (C++11)

A **delegating constructor** calls another constructor of the same class in its member initializer list. The called constructor runs completely first; then control returns to the delegating constructor's body.

```cpp
class Server {
    std::string host;
    int port;
    bool ssl;
    void init() { /* shared setup */ }
public:
    // Primary ("target") constructor — does all the real work
    Server(std::string h, int p, bool s)
        : host(h), port(p), ssl(s) { init(); }

    // Delegating constructors
    Server()          : Server("localhost", 8080, false) {}
    Server(int p)     : Server("localhost", p,    false) {}
};
```

**Rules:**
- The target constructor name in the MIL must be `ClassName(...)` (not a base class).
- A delegating constructor's MIL can contain **only** the delegation — no other member initializers are allowed in that same list.
- Delegation can chain: A → B → C, but forming a cycle (A → B → A) is undefined behavior.

## Execution Order with Delegation

```
Server("localhost", 8080, false)  ← target constructor runs first
    : host(h), port(p), ssl(s)    ← members initialized here
    { init(); }                   ← target body
Server()                          ← delegating constructor
    : Server(...)                 ← delegation done; members already set
    {}                            ← delegating body runs after
```

The object is considered fully constructed after the target constructor's body finishes. If an exception escapes the target constructor, the delegating constructor's body does **not** run, but the destructor **is** called (because the object was partially constructed).

## Inheriting Constructors (C++11)

Derived classes do not automatically inherit base class constructors. Before C++11 you had to write thin forwarding wrappers. C++11 adds the `using` directive to pull base constructors into scope:

```cpp
class Base {
public:
    int x, y;
    Base(int x, int y) : x(x), y(y) {}
    Base(int x)        : x(x), y(0) {}
};

class Derived : public Base {
    // Extra member with a default value
    std::string label;
public:
    using Base::Base;   // inherit all Base constructors

    // Derived-specific constructor still works
    Derived(int x, int y, std::string lbl)
        : Base(x, y), label(lbl) {}
};

Derived d1(3, 4);       // uses inherited Base(int, int)
Derived d2(7);          // uses inherited Base(int)
Derived d3(1, 2, "hi"); // uses Derived's own constructor
```

**What the `using` declaration does:** for each constructor in `Base` that is not shadowed by a `Derived` constructor with the same signature, it synthesizes a forwarding constructor in `Derived` that passes all arguments to the corresponding `Base` constructor and default-initializes any extra `Derived` members.

## Pitfalls

- **New members are default-initialized.** When an inherited constructor runs, any `Derived`-only members are default-initialized (not zero-initialized for POD types unless you provide a default member initializer).

```cpp
class Derived : public Base {
    int extra = 0;   // default member initializer — safe with inherited ctors
    using Base::Base;
};
```

- **Shadowing:** if `Derived` declares a constructor with the same signature as one of `Base`'s, the `using` declaration does not generate a forwarder for that signature; `Derived`'s version wins.

- **Access:** an inherited constructor has the same access level as the original base constructor.

## Worked Example

```cpp
#include <iostream>
#include <string>

class Widget {
protected:
    int id;
    std::string name;
public:
    Widget(int id, std::string name) : id(id), name(name) {
        std::cout << "Widget(" << id << ", " << name << ")\n";
    }
};

class Button : public Widget {
    bool pressed = false;   // safe default member initializer
public:
    using Widget::Widget;   // inherit Widget(int, std::string)

    void click() { pressed = true; }
};

int main() {
    Button b(42, "submit");   // Widget(42, submit) printed
    b.click();
}
```

> **Interview answer:** Delegating constructors allow one constructor to call another of the same class, eliminating duplicated initialization logic. The target runs entirely before the delegating body. Inheriting constructors (`using Base::Base`) let a derived class expose all base constructors without writing forwarding wrappers, though derived-only members are default-initialized when those constructors fire.
