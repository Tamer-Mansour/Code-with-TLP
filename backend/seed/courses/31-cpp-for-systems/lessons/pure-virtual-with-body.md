# Pure Virtual Functions That Still Have a Body

A common misconception is that `= 0` means "no body allowed." In fact, a pure virtual function *can* have a definition — it just cannot have that definition inline in the class declaration. The class remains abstract: you still cannot instantiate it.

## Syntax

```cpp
class Protocol {
public:
    virtual void send(const char* data, std::size_t len) = 0;  // pure virtual
    virtual ~Protocol() = default;
};

// Out-of-class definition — perfectly legal
void Protocol::send(const char* data, std::size_t len) {
    // Default implementation — validate args, log, etc.
    if (!data || len == 0) throw std::invalid_argument("bad args");
    // Derived classes may call this via Protocol::send(...)
}
```

The class `Protocol` is still abstract. You cannot write `Protocol p;`. But any derived class can explicitly call the base version.

## Calling the Pure Virtual Body from a Derived Class

```cpp
class TcpProtocol : public Protocol {
public:
    void send(const char* data, std::size_t len) override {
        Protocol::send(data, len);          // call base for validation
        // ... actual TCP send logic ...
    }
};
```

This is the primary use case: **provide shared pre/post logic in the base while still forcing every derived class to supply its own override.**

## Why Would You Want This?

1. **Shared validation or logging** — the base body handles invariants that every implementation must respect. Derived classes call `Base::method()` as a preamble.
2. **Default fallback behaviour** — a derived class that intentionally skips adding its own logic can call the base explicitly. The `= 0` still forces the derived class to *write* an override (even if that override just calls `Base::f()`), making the decision explicit.
3. **Destructors** — pure virtual destructors *must* have a body (see below).

## Pure Virtual Destructor — the Special Case

A pure virtual destructor is the one situation where a body is not just allowed but **required**:

```cpp
class AbstractBase {
public:
    virtual ~AbstractBase() = 0;   // makes class abstract
};

// Body is mandatory — the derived destructor chain calls it
AbstractBase::~AbstractBase() {}
```

Without the out-of-class definition, the linker will fail with an "undefined reference to `AbstractBase::~AbstractBase()`" error because the derived destructor implicitly calls it.

A pure virtual destructor is useful when you want a class to be abstract but have no other pure virtual functions to declare.

```cpp
class AbstractSensor {
protected:
    int id_;
public:
    explicit AbstractSensor(int id) : id_(id) {}
    virtual int read() { return 0; }      // has a default implementation
    virtual ~AbstractSensor() = 0;        // forces class to be abstract
};
AbstractSensor::~AbstractSensor() {}

class TempSensor : public AbstractSensor {
public:
    explicit TempSensor(int id) : AbstractSensor(id) {}
    int read() override { /* read hardware register */ return 25; }
};
```

## Quick Comparison

| Feature | Regular virtual | Pure virtual (no body) | Pure virtual with body |
|---------|----------------|----------------------|----------------------|
| Class abstract? | No | Yes | Yes |
| Derived must override? | No | Yes | Yes |
| Callable as `Base::f()`? | Yes | No (body is missing) | Yes |
| Common use case | Default impl | Enforce contract | Shared logic + contract |

## Common Pitfall: Inline Definition

You cannot place the body inline inside the class with `= 0`:

```cpp
// ILLEGAL
virtual void send() = 0 { /* ... */ }   // syntax error
```

The definition must appear outside the class, after the closing `}`.

> **Interview answer:** A pure virtual function can have an out-of-class body that derived classes call explicitly via `Base::f()`; the class is still abstract, but the body provides shared validation or default logic — and for pure virtual destructors a body is mandatory because the destructor chain always calls it.
