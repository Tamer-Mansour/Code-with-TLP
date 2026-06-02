# Member Initializer Lists and Initialization Order

A **member initializer list** (MIL) is the colon-separated clause between a constructor's parameter list and its body. It is the correct and often the only way to initialize class members in C++.

## Syntax

```cpp
class Connection {
    std::string host;
    int port;
    bool secure;
public:
    Connection(std::string h, int p, bool s)
        : host(h), port(p), secure(s)   // <-- member initializer list
    {
        // constructor body (runs after members are initialized)
    }
};
```

Every name before the `(` must be a data member or a base class. The values inside `()` (or `{}`) are used to construct the member directly.

## Why MIL Beats Assignment in the Body

When you write assignment in the constructor body, the member is first **default-constructed**, then **assigned**. That is two operations instead of one.

```cpp
// Bad: double initialization for std::string
Connection::Connection(std::string h) {
    host = h;   // host is default-constructed first, then assigned
}

// Good: single construction
Connection::Connection(std::string h) : host(h) {}
```

For `std::string` the difference is just overhead; for types with no default constructor the body-assignment approach is a **compile error**.

## Members That Require a MIL

Three categories of members cannot be assigned after construction:

| Member type | Why |
|---|---|
| `const` members | Must be set at construction; immutable after |
| Reference members (`T&`) | References cannot be reseated |
| Members with no default constructor | Cannot be default-constructed |

```cpp
class Fixed {
    const int id;
    int& ref;
    std::mutex mtx;   // no default constructor in some implementations

    Fixed(int id, int& r) : id(id), ref(r) {} // mandatory MIL
};
```

## Initialization Order: It Follows Declaration, Not MIL Order

**The single most common MIL pitfall:** members are initialized in the order they are *declared in the class*, regardless of the order they appear in the initializer list.

```cpp
class Range {
    int low;
    int high;
    int span;   // declared after high
public:
    Range(int lo, int hi)
        : span(hi - lo),   // listed first but initialized THIRD
          low(lo),         // initialized FIRST (declaration order)
          high(hi)         // initialized SECOND
    {}
};
```

Here `span` is computed from `hi - lo`, which is fine because `hi` and `lo` are constructor *parameters*, not members. But consider this broken variant:

```cpp
class Bad {
    int size;
    int* data;
public:
    Bad(int n)
        : data(new int[size]),  // BUG: size not yet initialized
          size(n)
    {}
};
```

`size` is declared first so it is initialized first, but in the MIL `data` is listed first. The compiler initializes `size` (to `n`) then `data` (with `new int[size]`). Wait — `size` *is* declared first, so it *is* initialized first. This particular example is actually fine. The bug appears when you reverse the declarations:

```cpp
class Bad2 {
    int* data;  // declared first
    int size;
public:
    Bad2(int n) : size(n), data(new int[size]) {} // BUG: data uses uninitialized size
};
```

**Rule:** always list MIL entries in the same order as the class declarations, and enable `-Wreorder` (GCC/Clang warns about mismatches).

## Base Class Initialization

Base classes must be initialized in the MIL too, before any member:

```cpp
class Animal {
    std::string name;
public:
    Animal(std::string n) : name(n) {}
};

class Dog : public Animal {
    std::string breed;
public:
    Dog(std::string n, std::string b)
        : Animal(n),     // base first
          breed(b)       // then own members
    {}
};
```

## Worked Example: Immutable Config Record

```cpp
#include <string>
#include <iostream>

class Config {
    const std::string env;
    const int maxConn;
    const bool debug;
public:
    Config(std::string e, int m, bool d)
        : env(e), maxConn(m), debug(d) {}

    void print() const {
        std::cout << env << " max=" << maxConn
                  << " debug=" << debug << "\n";
    }
};

int main() {
    Config prod("production", 100, false);
    Config dev("development",  10,  true);
    prod.print();
    dev.print();
}
```

Because `env`, `maxConn`, and `debug` are `const`, the MIL is the **only** place they can receive a value.

## Key Takeaways

- Always prefer the member initializer list over body assignment.
- Initialization order follows **declaration order** in the class, not MIL order.
- `const`, reference, and no-default-constructor members *require* the MIL.
- Initialize base classes in the MIL before member initializers.

> **Interview answer:** The member initializer list constructs members directly in-place, avoiding a redundant default-construction step. Members are always initialized in declaration order regardless of MIL order — a common source of bugs when members depend on each other.
