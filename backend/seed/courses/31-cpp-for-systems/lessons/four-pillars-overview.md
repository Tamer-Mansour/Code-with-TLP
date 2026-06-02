# The Four Pillars of OOP: How They Fit Together

Object-oriented programming rests on four principles: **Encapsulation, Abstraction, Inheritance, and Polymorphism**. Each pillar solves a different design problem, and they work together — misunderstanding one leads to misapplying the others.

## Quick Reference

| Pillar | One-line definition | Primary C++ mechanism |
|---|---|---|
| Encapsulation | Bundle data with its operations; control access | `private` / `public`, access specifiers |
| Abstraction | Expose only what the caller needs; hide the rest | Classes, pure-virtual interfaces, templates |
| Inheritance | Reuse and extend behaviour from a base class | `class Derived : public Base` |
| Polymorphism | One interface, many implementations | `virtual` functions, function overloading, templates |

## Encapsulation

Encapsulation says: **own your data**. Private fields with controlled mutators mean the class can enforce invariants. Without it there is no guarantee an object is ever in a valid state.

```cpp
class Voltage {
public:
    bool set_mv(int mv) { if (mv < 0 || mv > 5000) return false; mv_ = mv; return true; }
    int  get_mv() const { return mv_; }
private:
    int mv_ = 0;  // millivolts; invariant: 0..5000
};
```

## Abstraction

Abstraction says: **show the right level of detail**. An interface hides whether it uses POSIX, Win32, or a custom RTOS underneath.

```cpp
class IFile {
public:
    virtual ~IFile() = default;
    virtual bool   write(const void* buf, size_t n) = 0;
    virtual size_t read (void* buf, size_t n)       = 0;
};
```

## Inheritance

Inheritance says: **reuse and specialize**. A `SerialPort` IS-A `IFile`; it extends the contract without repeating common logic.

```cpp
class SerialPort : public IFile {
public:
    bool   write(const void* buf, size_t n) override { /* transmit bytes */ return true; }
    size_t read (void* buf, size_t n)       override { /* receive bytes  */ return 0; }
};
```

**Prefer composition over inheritance** when the relationship is HAS-A, not IS-A. Over-deep hierarchies are a classic OOP pitfall.

## Polymorphism

Polymorphism says: **let behaviour vary by type, not by switch statement**. Runtime polymorphism (virtual dispatch) and compile-time polymorphism (templates) each have their place.

```cpp
// Runtime polymorphism — chosen at runtime
void log_to(IFile& out, const char* msg) {
    out.write(msg, strlen(msg));  // could be SerialPort, SdCard, UartFile …
}

// Compile-time (generic) polymorphism — zero overhead
template<typename FileT>
void log_to(FileT& out, const char* msg) {
    out.write(msg, strlen(msg));  // resolved at compile time
}
```

## How They Interact

```
           +------------------+
           |   Abstraction    |  "What does it do?" — IFile interface
           +--------+---------+
                    |
           +--------+---------+
           |   Polymorphism   |  "Which one?" — SerialPort or SdCard
           +--------+---------+
                    |
     +--------------+--------------+
     |                             |
+----+-------+           +---------+-------+
| Inheritance |           | Encapsulation  |
| (IS-A)      |           | (owns data +   |
|             |           |  invariants)   |
+-------------+           +----------------+
```

A well-designed class:
1. **Encapsulates** its state (private fields, validating setters).
2. **Abstracts** away its platform specifics (no `#include <windows.h>` leaking out).
3. **Inherits** from an interface rather than a concrete class where possible.
4. Participates in **polymorphism** through virtual methods or template parameters.

## Pitfalls When Mixing the Pillars

- **Inheritance breaking encapsulation** — `protected` data members are accessible to all subclasses, creating hidden coupling. Prefer `private` + accessor methods even for derived classes.
- **Polymorphism hiding bugs** — slicing occurs when a derived object is passed by value to a base parameter; always use references or pointers for polymorphic types.
- **Abstraction without encapsulation** — an abstract interface backed by a class with public data members is incoherent.

## Interview Answer

> "The four pillars work together: encapsulation protects state, abstraction defines clean boundaries, inheritance reuses and specializes behaviour, and polymorphism lets one interface drive many implementations. A design problem usually maps to exactly one pillar — mixing them up leads to over-engineered or fragile code."
