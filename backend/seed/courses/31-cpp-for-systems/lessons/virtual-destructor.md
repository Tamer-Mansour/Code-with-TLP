# Why You Need a Virtual Destructor

When you delete a derived object through a base-class pointer, the language must know which destructor to call. Without a `virtual` destructor on the base, the compiler calls only the base destructor — the derived class's destructor is silently skipped. The result is **undefined behaviour** and, in practice, resource leaks.

## The Classic Bug

```cpp
class Base {
public:
    ~Base() { std::puts("Base dtor"); }   // NOT virtual — bug!
};

class Derived : public Base {
    int* data_;
public:
    Derived() : data_(new int[1024]) {}
    ~Derived() {                           // never called via Base*
        delete[] data_;                    // memory leak!
        std::puts("Derived dtor");
    }
};

Base* p = new Derived();
delete p;   // only ~Base() runs — Derived::data_ is leaked
```

The output is just `Base dtor`. The 4 KB allocation in `Derived` is gone forever.

## The Fix: `virtual ~Base()`

```cpp
class Base {
public:
    virtual ~Base() { std::puts("Base dtor"); }   // virtual!
};
```

Now `delete p` dispatches through the vtable, calls `~Derived()` first (which frees `data_`), then `~Base()`.

```
Derived dtor
Base dtor
```

## Rules for When You Need a Virtual Destructor

| Situation | Need virtual dtor? |
|-----------|--------------------|
| Class is used as a polymorphic base | **Yes, always** |
| Class is a pure interface (all pure virtual) | **Yes** |
| Class is a `final` concrete class, never used as a base | No |
| Class has no virtual functions at all | Usually no |

The guideline: **if a class has any virtual function, give it a virtual destructor.**

## Defaulted Virtual Destructor

For abstract classes and interfaces that need no custom cleanup, use:

```cpp
class IDevice {
public:
    virtual void init() = 0;
    virtual void shutdown() = 0;
    virtual ~IDevice() = default;   // virtual, compiler-generated body
};
```

`= default` generates the correct destructor body while keeping it `virtual`.

## The `override` Specifier on Destructors

Derived classes can (and arguably should) mark their destructors with `override` when the base dtor is virtual:

```cpp
class GpioDevice : public IDevice {
public:
    ~GpioDevice() override { /* cleanup GPIO pins */ }
};
```

This confirms at compile time that you are genuinely overriding a virtual destructor and not accidentally creating a new one.

## What Happens Without a Virtual Destructor — Compiler Warning

Modern compilers (GCC, Clang) will warn when a class with virtual functions lacks a virtual destructor:

```
warning: 'class Base' has virtual functions but non-virtual destructor
```

Enable `-Wall -Wextra` (or `/W4` on MSVC) and treat this as an error in production code.

## Pitfall: `std::unique_ptr` and Custom Deleters

When a `unique_ptr<Base>` owns a `Derived` object, the same rule applies. The destructor called by `unique_ptr`'s default deleter is `~Base()`. Without a virtual destructor, the derived part is not cleaned up:

```cpp
std::unique_ptr<Base> ptr = std::make_unique<Derived>();
// ~ptr goes out of scope: only ~Base() runs if not virtual
```

Always pair polymorphic ownership with a virtual destructor.

## Summary

- `delete base_ptr` calls only the static type's destructor unless it is `virtual`.
- Any polymorphic base class must have `virtual ~Base()`.
- Use `= default` for no-op virtual destructors.
- Missing virtual destructors cause silent resource leaks and undefined behaviour.

> **Interview answer:** Without a virtual destructor, deleting a derived object through a base pointer invokes only the base destructor, leaving the derived object's resources un-freed — which is undefined behaviour. Marking the base destructor `virtual` ensures the correct derived destructor runs first.
