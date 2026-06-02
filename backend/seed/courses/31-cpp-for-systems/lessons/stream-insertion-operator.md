# Overloading << and >> for Streams

Overloading the stream operators lets your types work with `std::cout`, `std::cin`, `std::ofstream`, `std::istringstream`, and any other `std::ostream`/`std::istream` subclass. They must always be non-member functions because the left operand is the stream, not your type.

## Signature Rules

```cpp
// Output (insertion): returns ostream& for chaining
std::ostream& operator<<(std::ostream& os, const MyType& obj);

// Input (extraction): returns istream& for chaining; obj is non-const
std::istream& operator>>(std::istream& is, MyType& obj);
```

Both return a **reference to the stream** so chaining works:

```cpp
std::cout << a << " and " << b << '\n';
// parsed as: ((std::cout << a) << " and ") << b) << '\n';
```

## Basic Output Operator

```cpp
#include <ostream>

struct Point {
    double x, y;

    friend std::ostream& operator<<(std::ostream& os, const Point& p) {
        os << '(' << p.x << ", " << p.y << ')';
        return os;
    }
};

// Usage
Point p{3.0, 4.0};
std::cout << p << '\n';        // prints: (3, 4)
std::cout << "A=" << p << '\n'; // chaining works
```

Using `friend` inside the class body gives access to private members while keeping the function non-member.

## Input Operator with Validation

```cpp
#include <istream>

struct Point {
    double x, y;

    friend std::istream& operator>>(std::istream& is, Point& p) {
        char lp, comma, rp;
        if (!(is >> lp >> p.x >> comma >> p.y >> rp)
            || lp != '(' || comma != ',' || rp != ')') {
            is.setstate(std::ios::failbit);  // signal parse failure
        }
        return is;
    }
};

// Usage
Point p;
std::cin >> p;         // expects "(3.0, 4.0)"
if (!std::cin) {
    // handle bad input
}
```

Always check `is.fail()` / `operator bool()` on the stream after reading; set `failbit` on bad format.

## Respecting Stream Formatting Flags

Output operators should honour the stream's format state where reasonable:

```cpp
friend std::ostream& operator<<(std::ostream& os, const Matrix& m) {
    for (int r = 0; r < m.rows; ++r) {
        for (int c = 0; c < m.cols; ++c) {
            os << std::setw(8) << m(r, c);   // uses current stream width semantics
        }
        os << '\n';
    }
    return os;
}
```

## Common Pitfalls

### 1. Returning the Wrong Type

```cpp
// WRONG — returns ostream by value; copies are not allowed
std::ostream operator<<(std::ostream os, const Point& p);
```

`std::ostream` is not copyable. Always return `std::ostream&`.

### 2. Forgetting to Return the Stream

```cpp
// WRONG — chaining breaks
std::ostream& operator<<(std::ostream& os, const Point& p) {
    os << '(' << p.x << ", " << p.y << ')';
    // missing: return os;
}
```

### 3. Making It a Member

```cpp
// WON'T work as intended — would require: p << std::cout
std::ostream& Point::operator<<(std::ostream& os) const;
```

The left operand of `<<` is always the stream, so this must be a free function.

## Works With Any Stream

Because the parameter is `std::ostream&`, the overload works with every derived stream type:

```cpp
std::ofstream  file("out.txt");
std::ostringstream buf;

file << p;   // write to file
buf  << p;   // write to string buffer
std::cerr << p;  // write to stderr
```

This is the power of programming to the base class.

## Worked Example: CSV-Friendly Point

```cpp
struct Point {
    double x, y;

    friend std::ostream& operator<<(std::ostream& os, const Point& p) {
        return os << p.x << ',' << p.y;
    }

    friend std::istream& operator>>(std::istream& is, Point& p) {
        char comma;
        if (!(is >> p.x >> comma >> p.y) || comma != ',')
            is.setstate(std::ios::failbit);
        return is;
    }
};
```

> **Interview answer:** `<<` and `>>` must be non-member functions because the left operand is the stream object, not your type. They return `std::ostream&` / `std::istream&` by reference to support chaining. Declare them `friend` inside the class when private access is needed.
