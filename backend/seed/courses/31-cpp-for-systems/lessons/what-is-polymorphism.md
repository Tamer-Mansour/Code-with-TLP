# What Is Polymorphism? Compile-Time vs Runtime

Polymorphism means "many forms." In C++, it lets a single interface operate on objects of different types, choosing the right behavior automatically. The language offers two distinct flavors: **compile-time (static)** polymorphism, resolved when the program is built, and **runtime (dynamic)** polymorphism, resolved while the program executes.

## Compile-Time Polymorphism

The compiler decides which function to call at compile time based on the types and number of arguments it can see in the source code.

**Function overloading** is the simplest example:

```cpp
void print(int x)    { std::cout << "int: " << x << '\n'; }
void print(double x) { std::cout << "double: " << x << '\n'; }
void print(const std::string& s) { std::cout << "string: " << s << '\n'; }

print(42);        // calls print(int)
print(3.14);      // calls print(double)
print("hello");   // calls print(const std::string&)
```

**Templates** are the most powerful form of compile-time polymorphism. The compiler instantiates a separate version for each type it encounters:

```cpp
template<typename T>
T maximum(T a, T b) { return (a > b) ? a : b; }

maximum(3, 7);          // int version
maximum(2.5, 1.9);      // double version
```

No virtual dispatch overhead — everything is resolved and often inlined at compile time.

## Runtime Polymorphism

Runtime polymorphism uses **virtual functions** and **base-class pointers or references**. The decision of which function to call is deferred until the program runs and the actual object type is known.

```cpp
struct Shape {
    virtual double area() const = 0;  // pure virtual
    virtual ~Shape() = default;
};

struct Circle : Shape {
    double r;
    Circle(double r) : r(r) {}
    double area() const override { return 3.14159 * r * r; }
};

struct Square : Shape {
    double side;
    Square(double s) : side(s) {}
    double area() const override { return side * side; }
};

void printArea(const Shape& s) {
    std::cout << s.area() << '\n';  // resolved at runtime
}

Circle c(5.0);
Square sq(4.0);
printArea(c);   // 78.54
printArea(sq);  // 16.0
```

The function `printArea` has no idea which concrete type it receives; the vtable resolves it at runtime.

## Side-by-Side Comparison

| Feature | Compile-Time | Runtime |
|---------|-------------|---------|
| Mechanism | Overloading, templates | Virtual functions |
| When resolved | Build time | Execution time |
| Performance cost | Zero | Indirect function call + possible cache miss |
| Flexibility | Types must be known statically | Works with unknown types (plugins, factories) |
| Code bloat | Template instantiation | Minimal (one vtable per class) |

## Which One to Use?

- Prefer **compile-time** polymorphism when all types are known at build time. It is faster and enables inlining.
- Use **runtime** polymorphism when you need to store heterogeneous objects behind a common interface or when types are determined dynamically (e.g., loading plugins, deserialization, command patterns).

A common systems-programming pitfall: reaching for virtual functions by habit when templates would deliver the same flexibility with zero runtime overhead.

**Interview answer:** Compile-time polymorphism (overloading/templates) is resolved by the compiler with no runtime cost; runtime polymorphism uses virtual functions and vtables to dispatch to the correct override while the program executes, enabling open-ended extensibility at the price of an indirect call.
