# What Is Operator Overloading and When to Use It

Operator overloading lets you define what built-in operators (`+`, `-`, `==`, `<<`, `[]`, etc.) mean when applied to your own types. The compiler translates `a + b` into a function call — you just write that function.

## How It Works

Every operator expression is syntactic sugar for a function call:

```cpp
a + b       // calls operator+(a, b)  or  a.operator+(b)
a == b      // calls operator==(a, b) or  a.operator==(b)
a[i]        // calls a.operator[](i)
```

You define an **operator function** with the special name `operator@`, where `@` is the symbol.

```cpp
struct Vector2D {
    double x, y;

    // member operator+
    Vector2D operator+(const Vector2D& rhs) const {
        return {x + rhs.x, y + rhs.y};
    }
};

int main() {
    Vector2D a{1.0, 2.0}, b{3.0, 4.0};
    Vector2D c = a + b;   // calls a.operator+(b)
    // c.x == 4.0, c.y == 6.0
}
```

## When to Use Operator Overloading

Use it when the operator has a **clear, unsurprising meaning** for your type:

| Type | Useful operators |
|------|-----------------|
| `Vector`, `Matrix` | `+`, `-`, `*`, `==` |
| `String` | `+`, `==`, `<`, `[]` |
| `BigInt` | `+`, `-`, `*`, `/`, `%`, `<=>` |
| `SmartPointer` | `*`, `->`, `bool` |
| `Iterator` | `++`, `--`, `*`, `->`, `==` |
| `Stream wrapper` | `<<`, `>>` |

The guiding principle: **operator overloading should make code more readable, not more clever.**

## Rules You Cannot Break

- You **cannot** invent new operators (`**` for power does not exist in C++).
- You **cannot** change operator **arity** (unary stays unary, binary stays binary).
- You **cannot** change operator **precedence or associativity**.
- At least **one operand must be a user-defined type** — you cannot redefine `int + int`.
- These operators **cannot** be overloaded: `::`, `.`, `.*`, `?:`.

## The "Principle of Least Surprise"

If overloading an operator would confuse a reader, don't do it. Classic bad examples:

```cpp
// BAD: operator+ used for "add element to container"
myList + element;   // surprising — this is what push_back() is for
```

Good overloads make expressions look like natural math or match STL conventions.

## Common Pitfall: Ignoring Const Correctness

A query operator that does not modify the object must be `const`:

```cpp
struct Point {
    int x, y;
    bool operator==(const Point& o) const { return x == o.x && y == o.y; }
    //                                ^^^^^ required so const Points can be compared
};
```

Forgetting `const` causes compilation errors whenever the left operand is `const` or a temporary.

## Worked Example: A Simple Fraction Class

```cpp
struct Fraction {
    int num, den;

    Fraction operator+(const Fraction& rhs) const {
        return {num * rhs.den + rhs.num * den, den * rhs.den};
    }

    bool operator==(const Fraction& rhs) const {
        return num * rhs.den == rhs.num * den;
    }
};

Fraction a{1, 2}, b{1, 3};
Fraction c = a + b;   // {5, 6}
bool eq  = (a == b);  // false
```

This is exactly how `std::complex` works internally.

> **Interview answer:** Operator overloading defines function bodies for built-in operator symbols so user-defined types support natural syntax. Use it when the meaning is unambiguous and matches mathematical or STL convention; avoid it when the operator's intent would surprise a reader.
