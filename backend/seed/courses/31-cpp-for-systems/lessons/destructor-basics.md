# Destructors and When They Run

A **destructor** is the mirror image of a constructor. It runs automatically just before an object's lifetime ends and is responsible for releasing any resources the object holds — file handles, heap memory, network sockets, locks.

## Syntax

```cpp
class FileHandle {
    FILE* fp;
public:
    FileHandle(const char* name) : fp(fopen(name, "r")) {}

    ~FileHandle() {         // destructor: tilde + class name, no params, no return
        if (fp) fclose(fp);
    }
};
```

Key facts:
- Name is `~ClassName`.
- No parameters, no return type.
- Cannot be overloaded (only one destructor per class).
- Can be declared `virtual` (and often must be, in base classes).

## When Destructors Run

| Situation | When |
|-----------|------|
| Local (stack) variable | Goes out of scope |
| `new`-allocated object | `delete` is called |
| Static variable | Program exits (in reverse construction order) |
| Array element | When the array is destroyed (last to first) |
| Member object | When the containing object is destroyed |
| Temporary | End of the full expression |

```cpp
void demo() {
    FileHandle f("log.txt");   // constructor
    // ... use f ...
}   // <-- destructor runs here automatically
```

This automatic, scope-driven cleanup is the foundation of **RAII** (Resource Acquisition Is Initialization) — the dominant resource-management idiom in modern C++.

## Compiler-Generated Destructor

If you declare no destructor, the compiler generates one that calls the destructor of each member and base class in reverse declaration order. For classes that hold only value-type members (no raw pointers, no handles), this is all you need.

```cpp
class Point {
    double x, y;
    // Compiler-generated ~Point() is perfectly fine
};
```

**The Rule of Three / Five:** if your class needs a custom destructor (because it owns a resource), it almost certainly also needs a custom copy constructor and copy-assignment operator (Rule of Three) and, in C++11+, move operations (Rule of Five).

## Destruction Order in Objects

When an object is destroyed:
1. The destructor body runs first.
2. Members are destroyed in **reverse declaration order**.
3. Base class destructors run last, from most-derived to least-derived.

```cpp
struct A { ~A() { std::cout << "~A\n"; } };
struct B { ~B() { std::cout << "~B\n"; } };

struct Composite {
    A a;   // declared first, destroyed second
    B b;   // declared second, destroyed first
    ~Composite() { std::cout << "~Composite body\n"; }
};

// Output when Composite is destroyed:
// ~Composite body
// ~B
// ~A
```

## Virtual Destructors

If a class is intended to be a base class and objects may be deleted through a pointer to the base, the destructor **must** be `virtual`. Without it, deleting through a base pointer is undefined behavior.

```cpp
class Base {
public:
    virtual ~Base() {}   // MUST be virtual
};

class Derived : public Base {
    int* data;
public:
    Derived() : data(new int[100]) {}
    ~Derived() { delete[] data; }   // called correctly because ~Base is virtual
};

Base* b = new Derived();
delete b;   // calls ~Derived() then ~Base() — correct
```

## A Common Pitfall: Double Delete

```cpp
FileHandle* h = new FileHandle("log.txt");
FileHandle* alias = h;
delete h;
delete alias;   // UNDEFINED BEHAVIOR — already deleted
```

Smart pointers (`std::unique_ptr`, `std::shared_ptr`) eliminate this class of bug entirely.

## Worked Example: RAII Lock Guard

```cpp
#include <mutex>
#include <iostream>

class LockGuard {
    std::mutex& mtx;
public:
    explicit LockGuard(std::mutex& m) : mtx(m) { mtx.lock(); }
    ~LockGuard() { mtx.unlock(); }   // always unlocks, even if exception thrown
};

std::mutex g_mtx;

void critical_section() {
    LockGuard guard(g_mtx);
    std::cout << "Inside critical section\n";
}   // guard destroyed here → mutex unlocked automatically
```

This pattern — acquire in constructor, release in destructor — guarantees release even when exceptions or early returns occur.

> **Interview answer:** A destructor runs when an object's lifetime ends — scope exit for locals, `delete` for heap objects. If a class owns a resource, the destructor should release it. Base classes intended for polymorphic deletion must declare their destructor `virtual` to ensure the correct derived destructor is called.
