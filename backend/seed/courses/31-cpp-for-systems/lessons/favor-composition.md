# Why Favor Composition Over Inheritance

"Favor composition over inheritance" is one of the most repeated design principles in software engineering — it appears in the Gang of Four book, in Effective C++, and in virtually every modern style guide. This lesson explains precisely why, with concrete C++ examples.

## The Core Problem with Inheritance

Inheritance creates a **tight coupling** between base and derived classes. The derived class depends on the base's implementation details, not just its interface. This coupling manifests in several ways:

### 1. Fragile Base Class Problem

When you change a base class, you can silently break derived classes — even if the change seems local.

```cpp
class Collection {
public:
    int count_ = 0;
    virtual void add(int x)        { data_.push_back(x); ++count_; }
    virtual void addAll(const std::vector<int>& v) {
        for (int x : v) add(x);    // calls virtual add() — seems fine
    }
private:
    std::vector<int> data_;
};

class InstrumentedCollection : public Collection {
    int add_calls_ = 0;
public:
    void add(int x) override { ++add_calls_; Collection::add(x); }
};

InstrumentedCollection ic;
ic.addAll({1, 2, 3});
// add_calls_ is 3 — correct here
// But if Collection::addAll is changed to not call add() internally,
// add_calls_ silently becomes 0 without any change to InstrumentedCollection
```

The derived class is relying on the internal behavior of `addAll` (that it calls `add`). That is a dependency on implementation, not interface.

### 2. Violating Encapsulation

A derived class can call `protected` methods and see internal state. This exposes the base class's internals to an unbounded set of subclasses, making the base class harder to refactor.

### 3. Inheritance Cannot Be Changed at Runtime

Once an object is constructed, its class hierarchy is fixed. Composition allows you to swap components at runtime:

```cpp
// Inheritance: fixed behavior
class Logger : public ConsoleOutput { /* ... */ };

// Composition: swappable behavior
class Logger {
    std::unique_ptr<Output> out_;   // can be Console, File, Network, ...
public:
    explicit Logger(std::unique_ptr<Output> o) : out_(std::move(o)) {}
    void log(const std::string& msg) { out_->write(msg); }
};
```

## Composition-Based Rewrite

Take the `InstrumentedCollection` example. With composition:

```cpp
class InstrumentedCollection {
    Collection inner_;
    int add_calls_ = 0;
public:
    void add(int x)        { ++add_calls_; inner_.add(x); }
    void addAll(const std::vector<int>& v) { for (int x : v) add(x); }
    int  addCallCount() const { return add_calls_; }
    // forward only the methods you want to expose
};
```

Now `InstrumentedCollection` controls its own loop in `addAll`, so any change to `Collection::addAll` does not break the count. The coupling is through the **public interface** of `Collection`, not its implementation.

## When Inheritance Still Wins

Composition cannot replace inheritance in every situation:

| Need | Composition | Inheritance |
|---|---|---|
| Code reuse | Yes | Yes |
| Runtime polymorphism (virtual dispatch) | Only with an interface | Yes |
| Override a virtual function | No | Yes |
| Access to `protected` members | No | Yes |
| Empty base optimization | No | Yes |

The clearest case for inheritance is a framework **extension point** — the library provides a base class with virtual methods, and you subclass it to inject behavior. Examples: `std::exception`, `QObject`, device driver base classes in OS kernels.

## The Strategy Pattern: Composition for Behavior Variation

Instead of subclassing to vary behavior, inject the varying behavior as a component:

```cpp
// Instead of:
class Sorter { virtual void sort(std::vector<int>&) = 0; };
class QuickSorter : public Sorter { ... };
class MergeSorter : public Sorter { ... };

// Use composition with a function object:
class DataPipeline {
    std::function<void(std::vector<int>&)> sort_;
public:
    explicit DataPipeline(std::function<void(std::vector<int>&)> s) : sort_(s) {}
    void process(std::vector<int>& v) { sort_(v); /* ... */ }
};

DataPipeline p([](auto& v){ std::sort(v.begin(), v.end()); });
```

This is more flexible, requires no inheritance hierarchy, and is easier to test.

## Practical Guidelines

- Default to composition. Add inheritance only when you need substitutability or virtual dispatch.
- Keep inheritance hierarchies shallow (1-2 levels).
- Prefer pure-abstract interfaces (no data members, all pure-virtual) as base classes when you need polymorphism.
- Never inherit from a concrete class that was not designed for inheritance (no virtual destructor, no documented extension points).

> **Interview answer:** Composition is preferred over inheritance because it couples classes only through public interfaces rather than implementation details, avoids the fragile base-class problem, and allows behavior to be swapped at runtime. Inheritance is appropriate when you genuinely need runtime polymorphism or must extend a framework's extension point.
