# Overloading Arithmetic and Compound Assignment

Arithmetic overloading follows a strict hierarchy: implement compound assignment (`+=`, `-=`, `*=`, `/=`) as members first, then derive binary operators (`+`, `-`, `*`, `/`) from them as non-members. This avoids code duplication and keeps consistency.

## The Canonical Pattern

```cpp
class Vector2D {
public:
    double x, y;

    // 1. Compound assignment — member, returns *this by reference
    Vector2D& operator+=(const Vector2D& rhs) {
        x += rhs.x;
        y += rhs.y;
        return *this;
    }

    Vector2D& operator-=(const Vector2D& rhs) {
        x -= rhs.x;
        y -= rhs.y;
        return *this;
    }

    Vector2D& operator*=(double scalar) {
        x *= scalar;
        y *= scalar;
        return *this;
    }
};

// 2. Binary operators — non-member, built from compound assignment
// lhs is taken BY VALUE so we can modify it freely
Vector2D operator+(Vector2D lhs, const Vector2D& rhs) { return lhs += rhs; }
Vector2D operator-(Vector2D lhs, const Vector2D& rhs) { return lhs -= rhs; }
Vector2D operator*(Vector2D v,   double scalar)       { return v  *= scalar; }
Vector2D operator*(double scalar, Vector2D v)          { return v  *= scalar; }  // commutative
```

Taking `lhs` by value serves as the copy — no explicit `tmp` variable needed.

## Why Return `*this` from Compound Assignment

Returning a reference to `*this` enables chaining:

```cpp
Vector2D a, b, c;
a += b += c;   // right-associative chaining works correctly
```

Returning by value would create a temporary and break this pattern.

## Unary Minus and Plus

```cpp
class Vector2D {
    // ...
public:
    Vector2D operator-() const { return {-x, -y}; }   // unary minus
    Vector2D operator+() const { return *this; }       // unary plus (rarely needed)
};
```

Unary operators are always members and return by value.

## Pitfall: Returning a Reference from Binary `+`

A common beginner mistake:

```cpp
// WRONG — returns a reference to a local
Vector2D& operator+(const Vector2D& lhs, const Vector2D& rhs) {
    Vector2D result{lhs.x + rhs.x, lhs.y + rhs.y};
    return result;   // undefined behaviour — result is destroyed on return
}
```

Binary `+` must return **by value**.

## Mixed-Type Arithmetic

When the operands have different types, provide overloads for each combination:

```cpp
class Seconds {
    double val;
public:
    explicit Seconds(double v) : val(v) {}
    double count() const { return val; }

    Seconds& operator*=(double factor) { val *= factor; return *this; }
};

Seconds operator*(Seconds s, double f) { return s *= f; }
Seconds operator*(double f, Seconds s) { return s *= f; }  // commutative form
```

Without the second overload, `2.0 * duration` would not compile.

## Full Worked Example: BigInt Addition Sketch

```cpp
#include <vector>
#include <algorithm>

class BigUInt {
    std::vector<uint32_t> digits;  // base-2^32, little-endian
public:
    explicit BigUInt(uint64_t v) { digits.push_back(v); }

    BigUInt& operator+=(const BigUInt& rhs) {
        if (rhs.digits.size() > digits.size())
            digits.resize(rhs.digits.size(), 0);

        uint64_t carry = 0;
        for (size_t i = 0; i < rhs.digits.size() || carry; ++i) {
            if (i == digits.size()) digits.push_back(0);
            uint64_t sum = (uint64_t)digits[i] + carry
                         + (i < rhs.digits.size() ? rhs.digits[i] : 0);
            digits[i] = (uint32_t)sum;
            carry     = sum >> 32;
        }
        return *this;
    }
};

BigUInt operator+(BigUInt lhs, const BigUInt& rhs) { return lhs += rhs; }
```

The real `+=` logic lives in one place; `+` reuses it for free.

## Summary Table

| Operator | Form | Return type |
|----------|------|-------------|
| `+=`, `-=`, `*=`, `/=` | Member | `T&` (`*this`) |
| `+`, `-`, `*`, `/` | Non-member | `T` (by value) |
| Unary `-`, `+` | Member | `T` (by value) |

> **Interview answer:** Implement `+=` as a member returning `*this`, then implement `+` as a non-member that takes the left operand by value and delegates to `+=`. This pattern avoids code duplication and ensures both operands can undergo implicit conversion.
