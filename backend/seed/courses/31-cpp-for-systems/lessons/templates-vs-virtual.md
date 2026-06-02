# Static Polymorphism: Templates vs Virtual Dispatch

C++ offers two distinct models of polymorphism:

- **Dynamic polymorphism** — virtual functions resolved at run time via a vtable pointer.
- **Static polymorphism** — templates resolved at compile time, with zero run-time overhead.

Understanding when to use each is a key skill for systems and performance-critical code.

## How Virtual Dispatch Works

```cpp
struct Shape {
    virtual double area() const = 0;
    virtual ~Shape() = default;
};

struct Circle : Shape {
    double r;
    explicit Circle(double r) : r(r) {}
    double area() const override { return 3.14159 * r * r; }
};

void print_area(const Shape& s) {
    std::cout << s.area() << "\n";   // vtable lookup at run time
}
```

Every call through a base pointer/reference causes an indirect jump through the vtable. The CPU cannot inline or speculate across an indirect call, so the optimizer's hands are tied.

## Static Polymorphism with Templates (CRTP)

The **Curiously Recurring Template Pattern (CRTP)** achieves polymorphism without virtual functions:

```cpp
template <typename Derived>
struct ShapeBase {
    double area() const {
        // cast to derived — no virtual call
        return static_cast<const Derived*>(this)->area_impl();
    }
};

struct Circle : ShapeBase<Circle> {
    double r;
    explicit Circle(double r) : r(r) {}
    double area_impl() const { return 3.14159 * r * r; }
};

struct Square : ShapeBase<Square> {
    double side;
    explicit Square(double s) : side(s) {}
    double area_impl() const { return side * side; }
};

template <typename S>
void print_area(const ShapeBase<S>& s) {
    std::cout << s.area() << "\n";   // inlined at compile time
}
```

`print_area` is instantiated separately for `Circle` and `Square`. Each call is a direct call — or inlined entirely — by the optimizer.

## Side-by-Side Comparison

| Aspect | Virtual Dispatch | CRTP / Templates |
|---|---|---|
| Resolution time | Run time | Compile time |
| Vtable overhead | 1 pointer indirection per call | None |
| Inlineable | Rarely | Yes |
| Heterogeneous collection | `std::vector<Shape*>` — easy | Requires type erasure (`std::variant`, `std::any`) |
| Binary size | One definition | One instantiation per type |
| Compile time | Fast | Slower (more code generated) |
| Inheritance required | Yes | No (duck typing via templates) |

## Policy-Based Design

Another form of static polymorphism: pass behavior as a template parameter.

```cpp
struct BubbleSort {
    template <typename It>
    static void sort(It first, It last) { /* bubble sort */ }
};

struct QuickSort {
    template <typename It>
    static void sort(It first, It last) { /* quick sort */ }
};

template <typename SortPolicy>
class Sorter {
public:
    template <typename It>
    void sort(It first, It last) {
        SortPolicy::sort(first, last);
    }
};

Sorter<QuickSort> fast_sorter;
```

Swapping the policy changes the algorithm with no run-time cost and no virtual function overhead.

## When to Prefer Which

**Use virtual dispatch when:**
- The concrete type is unknown at compile time (runtime plugin systems, factory patterns).
- You need heterogeneous collections (`std::vector<std::unique_ptr<Base>>`).
- The performance cost is acceptable (most application code).

**Use static polymorphism (CRTP / policies) when:**
- The type is known at compile time (template parameters, local variables).
- You are writing generic library code (containers, algorithms).
- Hot-path performance is critical and the vtable indirection matters.
- You want the compiler to inline and optimize across the call boundary.

## Worked Example: Logger Policy

```cpp
struct StderrLog  { static void log(const char* m) { std::cerr << m << "\n"; } };
struct NullLog    { static void log(const char*) {} };           // zero cost

template <typename Logger = StderrLog>
class Connection {
public:
    void connect(const char* host) {
        Logger::log("connecting...");
        // ... real work
    }
};

Connection<>         prod;   // logs to stderr
Connection<NullLog>  bench;  // zero overhead logging
```

In a benchmark or embedded context, `NullLog` compiles away to nothing. With a virtual `Logger` base, even a no-op call costs an indirect jump.

> **Interview answer:** "Static polymorphism uses templates to resolve dispatch at compile time, enabling inlining and zero run-time overhead. Dynamic polymorphism uses virtual functions resolved via a vtable at run time, which enables runtime flexibility and heterogeneous collections but adds an indirection cost per call. Choose based on whether the type is known at compile time and whether the call is on a hot path."
