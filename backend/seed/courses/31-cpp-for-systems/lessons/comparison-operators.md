# Comparison Operators and the Spaceship Operator

Comparison operators let your types work with `std::sort`, `std::map`, range-based algorithms, and plain `if` statements. C++20's three-way comparison operator (`<=>`) — nicknamed the "spaceship operator" — generates all six comparisons from one definition.

## Pre-C++20: Writing All Six

Before C++20, you had to write `==`, `!=`, `<`, `>`, `<=`, `>=` manually — or derive five from two:

```cpp
struct Point {
    int x, y;

    // 1. Define == and <
    friend bool operator==(const Point& a, const Point& b) {
        return a.x == b.x && a.y == b.y;
    }
    friend bool operator< (const Point& a, const Point& b) {
        if (a.x != b.x) return a.x < b.x;
        return a.y < b.y;
    }

    // 2. Derive the rest
    friend bool operator!=(const Point& a, const Point& b) { return !(a == b); }
    friend bool operator> (const Point& a, const Point& b) { return  b < a;    }
    friend bool operator<=(const Point& a, const Point& b) { return !(b < a);  }
    friend bool operator>=(const Point& a, const Point& b) { return !(a < b);  }
};
```

This is boilerplate-heavy and error-prone.

## C++20: The Spaceship Operator `<=>`

`operator<=>` returns a **comparison category type** that encodes the relationship:

| Return type | Meaning | Example |
|-------------|---------|---------|
| `std::strong_ordering` | Total order, no ties | integers, pointers |
| `std::weak_ordering` | Total order, equivalent but not equal | case-insensitive strings |
| `std::partial_ordering` | Not every pair comparable | floating-point (NaN) |

```cpp
#include <compare>

struct Point {
    int x, y;

    // Defaulted: compiler generates memberwise <=>
    auto operator<=>(const Point&) const = default;
    // Also generates == automatically in C++20
};

Point a{1, 2}, b{1, 3};
bool less = (a < b);    // true  (x equal, y: 2 < 3)
bool eq   = (a == b);   // false
```

When defaulted, the compiler compares members in declaration order using their own `<=>`.

## Custom Spaceship Implementation

When you need custom logic:

```cpp
#include <compare>
#include <string>

struct Employee {
    std::string name;
    int         id;

    // Sort by id; treat same id as equivalent
    std::strong_ordering operator<=>(const Employee& rhs) const {
        return id <=> rhs.id;
    }

    // Must still define == explicitly if <=> is not defaulted
    bool operator==(const Employee& rhs) const {
        return id == rhs.id;
    }
};
```

> **Rule:** If you write a custom `<=>`, also write `==`. Defaulting `<=>` auto-generates `==`.

## Using the Result

```cpp
auto cmp = a <=> b;
if (cmp < 0)  { /* a < b  */ }
if (cmp == 0) { /* a == b */ }
if (cmp > 0)  { /* a > b  */ }

// Or use named constants:
cmp == std::strong_ordering::less;
cmp == std::strong_ordering::equal;
cmp == std::strong_ordering::greater;
```

## Floating-Point: `partial_ordering`

```cpp
struct Temp {
    double celsius;
    auto operator<=>(const Temp& rhs) const = default;
    // returns std::partial_ordering because double uses partial_ordering
};

Temp nan{std::numeric_limits<double>::quiet_NaN()};
// nan <=> nan  is  std::partial_ordering::unordered
```

## Common Pitfall: Forgetting `==` When Customising `<=>`

```cpp
struct Foo {
    int a, b;
    std::strong_ordering operator<=>(const Foo& rhs) const {
        return a <=> rhs.a;   // only compare a
    }
    // Forgot operator==!
    // foo1 == foo2 will NOT compile — rewriting == from <=> is not automatic
    // when <=> is user-defined (not defaulted).
};
```

Always pair a custom `<=>` with a matching `==`.

## STL Integration

Types with `<=>` or at least `<` and `==` work with:

```cpp
std::sort(vec.begin(), vec.end());          // needs <
std::map<Point, int> m;                     // needs <
std::find(vec.begin(), vec.end(), target);  // needs ==
```

> **Interview answer:** The spaceship operator `<=>` returns a comparison category (`strong_ordering`, `weak_ordering`, or `partial_ordering`) from which the compiler derives all six relational operators. Defaulting it generates memberwise comparison and also generates `==`. For custom logic, implement `<=>` and provide `==` separately.
