# Multiple Inheritance and Ambiguity

C++ allows a class to inherit from more than one base class simultaneously. This is a powerful feature used in real systems (mixins, interfaces, policy classes), but it comes with well-known hazards that must be managed carefully.

## Basic Syntax

```cpp
class Flyable {
public:
    virtual void fly() { std::cout << "Flying\n"; }
    virtual ~Flyable() = default;
};

class Swimmable {
public:
    virtual void swim() { std::cout << "Swimming\n"; }
    virtual ~Swimmable() = default;
};

class Duck : public Flyable, public Swimmable {
public:
    void fly()  override { std::cout << "Duck flies\n"; }
    void swim() override { std::cout << "Duck swims\n"; }
};
```

`Duck` has two separate base sub-objects in its memory layout, one per base class.

## Construction Order with Multiple Bases

Bases are constructed **left to right** in the order they appear in the inheritance list, regardless of the order in the derived class's member initializer list:

```cpp
struct A { A() { std::cout << "A\n"; } };
struct B { B() { std::cout << "B\n"; } };
struct C : A, B { C() : B(), A() { std::cout << "C\n"; } };
// Still prints: A  B  C
```

## Ambiguity: Same Name in Multiple Bases

The most common hazard. If two base classes provide a member with the same name, the unqualified call is ambiguous:

```cpp
struct Logger {
    void log(const std::string& msg) { std::cout << "[LOG] " << msg << "\n"; }
};

struct Auditor {
    void log(const std::string& msg) { std::cout << "[AUDIT] " << msg << "\n"; }
};

struct Service : Logger, Auditor {
    void process() {
        // log("event");        // ERROR: ambiguous — Logger::log or Auditor::log?
        Logger::log("event");   // OK: explicit qualification
        Auditor::log("event");  // OK
    }
};
```

Even if both functions have **identical signatures**, the compiler does not pick one — you must qualify. This applies even if one version is exactly what you want.

## Memory Layout

```
Duck object:
+-----------------+
| vptr (Flyable)  |   <- Flyable sub-object
+-----------------+
| vptr (Swimmable)|   <- Swimmable sub-object
+-----------------+
| Duck members    |
+-----------------+
```

A `Duck*` implicitly converts to `Flyable*` (no offset adjustment needed if Flyable is first) and to `Swimmable*` (compiler adds an offset). This pointer arithmetic is done by the compiler but has a real cost when casting across non-first bases.

## Slicing and Pointer Adjustments

```cpp
Duck* d = new Duck();
Swimmable* s = d;   // compiler adjusts pointer by sizeof(Flyable sub-object)
Flyable*   f = d;   // no adjustment if Flyable is listed first
```

Casting between unrelated bases (`static_cast<Logger*>(auditor_ptr)`) is undefined behavior; use `dynamic_cast` when the types could be related through a common derived class.

## Mixin Pattern — a Good Use of Multiple Inheritance

Mixins are small, orthogonal classes that add specific capabilities without their own state (or with minimal state). They are one of the most justified uses of multiple inheritance in modern C++:

```cpp
struct Serializable {
    virtual std::string serialize() const = 0;
};

struct Loggable {
    void log_self() const { std::cout << to_string() << "\n"; }
    virtual std::string to_string() const = 0;
};

class Config : public Serializable, public Loggable {
    std::string data_;
public:
    std::string serialize()  const override { return data_; }
    std::string to_string()  const override { return "Config(" + data_ + ")"; }
};
```

Mixins work well because:

- Each base has a single, focused responsibility.
- They rarely have the same member names (avoiding ambiguity).
- They are often pure-abstract, so there is no state duplication.

## Pitfalls to Watch For

| Pitfall | Symptom | Fix |
|---|---|---|
| Name ambiguity | Compile error | Qualify with `Base::name` or `using` |
| Duplicate base sub-objects | Diamond problem | Virtual inheritance (next lesson) |
| Wrong base pointer arithmetic | Subtle UB at runtime | Use `dynamic_cast` for cross-casts |
| Constructor order surprises | Initialization bugs | Remember: left-to-right in declaration |

> **Interview answer:** Multiple inheritance is legal in C++ and useful for mixins and interfaces, but identical member names in two base classes create ambiguity that must be resolved with explicit scope qualification. The bigger danger is the diamond problem, which requires virtual inheritance to solve.
