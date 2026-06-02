# Member vs Non-Member Operator Overloads

Every overloaded operator is either a **member function** of the class or a **non-member (free) function**. Choosing correctly affects symmetry, const correctness, and whether implicit conversions apply to the left operand.

## Member Operator Functions

A member operator is declared inside the class. The left operand is always `*this`.

```cpp
struct Vec {
    double x, y;

    Vec operator+(const Vec& rhs) const {   // left = *this
        return {x + rhs.x, y + rhs.y};
    }
};
```

`v1 + v2` compiles as `v1.operator+(v2)`. The compiler only looks up `operator+` on the type of `v1`.

### Problem: No Implicit Conversion on the Left

```cpp
struct Celsius {
    double value;
    Celsius(double v) : value(v) {}          // implicit constructor
    Celsius operator+(const Celsius& rhs) const {
        return {value + rhs.value};
    }
};

Celsius c = 20.0 + Celsius{5.0};  // ERROR — 20.0 is not a Celsius, left side fails
Celsius d = Celsius{20.0} + 5.0;  // OK   — right side converts 5.0 to Celsius
```

The left operand of a member operator is always `*this`, so it must already be the class type.

## Non-Member Operator Functions

A non-member operator is a free function. Both operands go through normal overload resolution — implicit conversions apply to **both sides**.

```cpp
struct Celsius {
    double value;
    Celsius(double v) : value(v) {}
};

// Free function — both operands may be implicitly converted
Celsius operator+(const Celsius& lhs, const Celsius& rhs) {
    return {lhs.value + rhs.value};
}

Celsius c = 20.0 + Celsius{5.0};  // OK — 20.0 converts to Celsius{20.0}
Celsius d = Celsius{20.0} + 5.0;  // OK — 5.0 converts to Celsius{5.0}
```

This is why **arithmetic operators are almost always non-member**.

## The `friend` Keyword for Access

If the non-member operator needs access to private data, declare it `friend`:

```cpp
class Vec {
    double x, y;
public:
    Vec(double x, double y) : x(x), y(y) {}

    friend Vec operator+(const Vec& a, const Vec& b) {
        return {a.x + b.x, a.y + b.y};   // accesses private x, y
    }
};
```

`friend` grants access without making the function a member.

## Decision Table

| Operator | Preferred form | Reason |
|----------|---------------|--------|
| `=`, `[]`, `()`, `->` | **Must** be member | Language rule |
| `+=`, `-=`, `*=` | Member | Modifies `*this` |
| `+`, `-`, `*`, `/` | Non-member | Symmetric conversion |
| `==`, `!=`, `<`, `>` | Non-member | Symmetric conversion |
| `<<`, `>>` | Non-member | Left operand is `ostream`/`istream` |
| `++`, `--` | Member | Modifies `*this` |
| `bool`, `int` (conversion) | Member | Language convention |

## Worked Example: Putting It Together

```cpp
class Money {
    long cents;
public:
    explicit Money(long c) : cents(c) {}
    long value() const { return cents; }

    // Compound assignment — member (modifies *this)
    Money& operator+=(const Money& rhs) {
        cents += rhs.cents;
        return *this;
    }
};

// Binary + built from +=, non-member (symmetric)
Money operator+(Money lhs, const Money& rhs) {
    lhs += rhs;   // reuse +=
    return lhs;
}

// Comparison, non-member
bool operator==(const Money& a, const Money& b) {
    return a.value() == b.value();
}
```

Implementing `+` in terms of `+=` (by taking `lhs` by value) is the canonical idiom — it avoids code duplication and is exception-safe.

> **Interview answer:** Member operators bind the left operand to `*this`, so implicit conversions cannot apply to it. Non-member operators allow implicit conversion on both sides, making arithmetic and comparison operators symmetric. Compound assignment (`+=`) should be a member; binary arithmetic (`+`) should be a non-member built from it.
