# User-Defined Conversion Operators and explicit

Conversion operators let your type convert implicitly or explicitly to another type. The `explicit` keyword prevents silent, unexpected conversions that can hide bugs.

## Syntax

```cpp
operator TargetType() const;
```

No return type is written — it is implied by the operator name.

```cpp
struct Celsius {
    double value;

    // Implicit conversion to double
    operator double() const { return value; }
};

Celsius c{100.0};
double d = c;        // OK — calls operator double()
double e = c + 0.0;  // OK — c converts to double first
```

## The Danger of Implicit Conversions

Implicit conversions interact with overload resolution in surprising ways:

```cpp
struct MyBool {
    bool flag;
    operator bool() const { return flag; }
};

MyBool a{true}, b{false};
int sum = a + b;      // Compiles! Both convert to int (via bool→int)
// This is almost never what you want
```

The classic example of this problem was `std::istream` in older C++ — it had an implicit `operator void*`, which led to expressions like `if (cin >> x)` working, but also allowed accidental comparisons between streams.

## The `explicit` Keyword

Mark a conversion `explicit` to require a cast:

```cpp
struct Celsius {
    double value;

    explicit operator double() const { return value; }
};

Celsius c{100.0};
double d = c;               // ERROR — implicit conversion not allowed
double e = static_cast<double>(c);  // OK — explicit cast
double f = (double)c;               // OK — C-style cast (avoid)
```

### When `explicit` Still Triggers Implicitly

Despite the keyword, an `explicit` conversion **does** fire in contexts where a boolean is directly needed:

```cpp
struct Handle {
    void* ptr;
    explicit operator bool() const { return ptr != nullptr; }
};

Handle h{some_ptr};
if (h) { ... }         // OK — bool context, explicit fires
bool b = h;            // ERROR — assignment is not a bool context
```

This is the idiomatic pattern for smart pointers and stream classes.

## Conversion Constructor vs Conversion Operator

There are two directions:

```cpp
struct Foo {
    // Conversion FROM double TO Foo  (via constructor)
    explicit Foo(double v) : val(v) {}

    // Conversion FROM Foo TO double  (via operator)
    explicit operator double() const { return val; }

    double val;
};
```

Use `explicit` on both unless you have a strong reason for implicit conversion (e.g., `std::string` allows implicit conversion from `const char*`).

## Worked Example: Safe Integer Wrapper

```cpp
class SafeInt {
    int value;
public:
    explicit SafeInt(int v) : value(v) {}

    // Allow read-back but only when explicitly requested
    explicit operator int() const { return value; }

    // Allow use in boolean context
    explicit operator bool() const { return value != 0; }

    SafeInt& operator+=(SafeInt rhs) { value += rhs.value; return *this; }
};

SafeInt a{5}, b{0};

int raw = static_cast<int>(a);   // explicit — intentional
if (b) { /* false */ }           // explicit bool fires in if-condition
// int x = a;                    // ERROR — prevents accidental narrowing
```

## Common Pitfalls

| Mistake | Problem |
|---------|---------|
| Implicit `operator bool()` | Allows `obj + 1`, `obj < 3`, etc. |
| Implicit `operator int()` on enum wrapper | Silent narrowing in arithmetic |
| Multiple implicit conversion chains | Ambiguous overload resolution |

## Rules of Thumb

- Prefer `explicit` for all user-defined conversions.
- Use implicit conversion only when the semantics are truly transparent (e.g., `std::string_view` from `std::string`).
- Always mark `operator bool()` as `explicit`.

> **Interview answer:** A conversion operator `operator T() const` lets an object convert to type `T`. Marking it `explicit` prevents silent implicit conversions while still allowing `static_cast<T>(obj)` and direct boolean-context use (like `if (obj)`). The `explicit operator bool()` pattern is the standard idiom for smart pointers and stream handles.
