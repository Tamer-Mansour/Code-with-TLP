# explicit and Converting Constructors

## Implicit Conversions via Single-Argument Constructors

Any constructor callable with exactly one argument can act as an **implicit conversion sequence** — the compiler uses it to silently convert one type to another. This is sometimes useful, but often surprising and dangerous.

```cpp
class Radius {
public:
    double value;
    Radius(double v) : value(v) {}   // single-argument constructor
};

void draw_circle(Radius r) {
    // ...
}

draw_circle(3.14);   // OK — compiler silently constructs Radius(3.14)
draw_circle(42);     // Also OK — int → double → Radius
```

The silent conversion from `int` (or any numeric type) to `Radius` may or may not be what you want.

## The `explicit` Keyword

Marking a constructor `explicit` disables its use as an implicit conversion. The constructor can still be called directly, but the compiler will not invoke it silently.

```cpp
class Radius {
public:
    double value;
    explicit Radius(double v) : value(v) {}
};

draw_circle(3.14);          // ERROR: no implicit conversion
draw_circle(Radius(3.14));  // OK: explicit construction
draw_circle(Radius{3.14});  // OK: list initialization
```

**Rule of thumb:** mark every single-argument constructor `explicit` unless you intentionally want the implicit conversion.

## Multi-Argument Constructors and `explicit`

In C++11 and later, `explicit` can also apply to constructors with zero or more than one argument — it prevents their use in copy-list initialization contexts:

```cpp
class Vec2 {
public:
    double x, y;
    explicit Vec2(double x, double y) : x(x), y(y) {}
};

Vec2 v1{1.0, 2.0};          // direct-list initialization: OK
Vec2 v2 = {1.0, 2.0};       // copy-list initialization: ERROR (explicit)
void foo(Vec2 v);
foo({1.0, 2.0});             // ERROR: implicit conversion attempt
```

This prevents accidental construction from braced lists, which is useful for types where the conversion semantics would be ambiguous.

## `explicit` on Conversion Operators

The same keyword applies to user-defined conversion operators:

```cpp
class SafeBool {
    bool value;
public:
    explicit operator bool() const { return value; }
};

SafeBool sb;
if (sb) { }              // OK: contextual conversion to bool
bool b = sb;             // ERROR: implicit conversion blocked
int x = sb + 1;         // ERROR: implicit conversion blocked
```

The standard library uses `explicit operator bool()` on `std::unique_ptr`, `std::shared_ptr`, `std::optional`, and streams for exactly this reason.

## A Practical Table

| Scenario | `explicit` present? | Allowed? |
|---|---|---|
| `Radius r(3.14)` | Yes | Yes — direct init |
| `Radius r{3.14}` | Yes | Yes — direct-list init |
| `Radius r = 3.14` | Yes | **No** |
| `void f(Radius); f(3.14)` | Yes | **No** |
| `void f(Radius); f(Radius(3.14))` | Yes | Yes — explicit cast |
| Same as above | No | Yes — implicit conversion |

## Worked Example: Preventing Accidental Unit Confusion

```cpp
#include <iostream>

struct Meters {
    explicit Meters(double v) : value(v) {}
    double value;
};

struct Feet {
    explicit Feet(double v) : value(v) {}
    double value;
};

void set_altitude(Meters m) {
    std::cout << "Altitude: " << m.value << " m\n";
}

int main() {
    set_altitude(Meters(305.0));   // correct
    // set_altitude(305.0);        // compile error — prevented accidental use
    // set_altitude(Feet(1000.0)); // compile error — type mismatch
}
```

This pattern is common in physics and finance code to eliminate unit confusion at compile time with zero runtime cost.

## Common Pitfalls

- **Forgetting `explicit` on wrapper types:** `class Path { Path(std::string s); }` will silently accept any string literal as a `Path`, which may cause incorrect overload resolution.
- **`std::string` is not `explicit`:** `std::string s = "hello";` works because `std::string(const char*)` is intentionally implicit.
- **Copy-initialization subtlety:** `T x = value;` requires an implicit conversion; `T x(value);` or `T x{value};` does not, even when `explicit` is present.

> **Interview answer:** `explicit` prevents a single-argument (or multi-argument in C++11) constructor from being used as an implicit conversion. It is a defensive practice: mark every single-argument constructor `explicit` by default and remove it only when implicit conversion is genuinely useful and safe.
