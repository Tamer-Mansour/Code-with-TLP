# Operator Overloading for Data Types

SystemC's custom integer types (`sc_int<N>`, `sc_uint<N>`, `sc_bv<N>`, `sc_lv<N>`) support arithmetic, comparison, bitwise, and stream operators. These work because SystemC overloads C++ operators for these types. Understanding operator overloading lets you read library headers fluently and design your own hardware data types correctly.

## What Is Operator Overloading?

An operator overload is a function with the special name `operator@` where `@` is the symbol (`+`, `==`, `<<`, etc.). When the compiler sees `a + b`, it looks for a function named `operator+` that accepts the types of `a` and `b`.

```cpp
struct Vector2D {
    double x, y;

    // Member operator: left operand is implicitly *this
    Vector2D operator+(const Vector2D& rhs) const {
        return {x + rhs.x, y + rhs.y};
    }

    // Comparison
    bool operator==(const Vector2D& rhs) const {
        return x == rhs.x && y == rhs.y;
    }
};

Vector2D a{1, 2}, b{3, 4};
Vector2D c = a + b;   // calls a.operator+(b) → {4, 6}
```

## Member vs Free-Function Operators

| Form | When to use |
|------|-------------|
| Member function | Left operand must be your type; can access `private` members |
| Free function | Either operand may be a built-in or third-party type; symmetric operators like `+` |

Arithmetic assignment operators (`+=`, `-=`) are almost always members. The corresponding binary operators (`+`, `-`) are best written as free functions in terms of the assignment form:

```cpp
// Member
MyInt& operator+=(const MyInt& rhs) { val += rhs.val; return *this; }

// Free function — reuses +=
inline MyInt operator+(MyInt lhs, const MyInt& rhs) {
    lhs += rhs;   // lhs is a copy
    return lhs;
}
```

## Stream Operators

`operator<<` for `std::ostream` must be a free function because the left operand is `std::ostream`, not your type:

```cpp
std::ostream& operator<<(std::ostream& os, const Vector2D& v) {
    return os << "(" << v.x << ", " << v.y << ")";
}

std::cout << a;   // prints (1, 2)
```

SystemC overloads `<<` for `sc_uint<N>` so you can print bus values directly:

```cpp
sc_uint<8> byte(0xAB);
std::cout << byte;   // prints 10101011 (binary by default)
```

## Conversion Operators

A conversion operator lets an object implicitly or explicitly convert to another type:

```cpp
struct Fixed {
    int raw;
    explicit operator double() const { return raw / 256.0; }
};

Fixed f{512};
double d = static_cast<double>(f);   // 2.0
```

`explicit` prevents silent implicit conversions that can mask bugs. SystemC uses explicit conversion operators in `sc_signal_in_if` to let you read a signal value with a cast.

## Subscript and Call Operators

- `operator[]` — subscript, used in `sc_lv<N>` to access individual bits.
- `operator()` — call, turns an object into a functor (see the Functors lesson).

```cpp
sc_lv<8> word("10110010");
sc_logic bit = word[3];   // operator[] on sc_lv
```

## Rules and Limitations

- You **cannot** overload `::`, `.*`, `.` (dot), `?:`, or `sizeof`.
- You **cannot** change the **arity** of an operator (unary stays unary).
- You **cannot** change **precedence** or **associativity**.
- Overloading `&&` and `||` loses short-circuit evaluation — avoid it.

## Common Pitfalls

- **Asymmetric equality** — if `a == b` works but `b == a` doesn't (because one side is a built-in), define the operator as a `friend` free function.
- **Returning a reference to a local** — `operator+` must return *by value*, not reference; the result is a temporary.
- **Missing `const`** — comparison and arithmetic operators should be `const` member functions; forgetting `const` prevents use on `const` objects and `const` references.

## Worked Example: Fixed-Point Type Skeleton

```cpp
template<int FRAC_BITS>
struct Fixed {
    int32_t raw;

    Fixed(double v = 0.0) : raw(static_cast<int32_t>(v * (1 << FRAC_BITS))) {}

    Fixed operator+(const Fixed& rhs) const { Fixed r; r.raw = raw + rhs.raw; return r; }
    Fixed operator*(const Fixed& rhs) const { Fixed r; r.raw = (raw * rhs.raw) >> FRAC_BITS; return r; }
    bool  operator==(const Fixed& rhs) const { return raw == rhs.raw; }
    explicit operator double() const { return raw / double(1 << FRAC_BITS); }
};
```

> **Interview answer:** Operator overloading lets user-defined types behave like built-in types syntactically. SystemC relies on it so that `sc_uint<8>` supports `+`, `&`, `|`, `<<`, and comparison with the same syntax as plain integers, enabling clean algorithmic code that maps directly to hardware intent.
