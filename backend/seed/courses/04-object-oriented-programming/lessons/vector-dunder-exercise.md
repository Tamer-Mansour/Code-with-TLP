# Exercise: Vector Class with Dunder Methods

This exercise solidifies your understanding of Python's object protocol by implementing a 2D vector class with operator overloading.

## What You Will Practice

- `__repr__` for a developer-friendly string representation
- `__add__` for the `+` operator
- `__eq__` for the `==` operator
- Writing a regular method (`magnitude`) alongside dunders

## Background: Operator Overloading

Python allows you to define how built-in operators work on your custom objects by implementing dunder methods. When Python evaluates `a + b`, it calls `a.__add__(b)`. When it evaluates `a == b`, it calls `a.__eq__(b)`.

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

p1 = Point(1, 2)
p2 = Point(3, 4)
print(p1 + p2)   # Point(4, 6)
```

## The Vector Class

Your `Vector(x, y)` class must support:

| Operation | Dunder / Method | Example |
|-----------|-----------------|---------|
| String representation | `__repr__` | `Vector(4, 6)` |
| Addition | `__add__` | `Vector(1,2) + Vector(3,4)` → `Vector(4,6)` |
| Equality | `__eq__` | `Vector(1,2) == Vector(1,2)` → `True` |
| Magnitude | `magnitude()` | `Vector(3,4).magnitude()` → `5.0` |

## Sample Run

Input:
```
add 1 2 3 4
eq 1 2 1 2
eq 1 2 3 4
mag 3 4
```

Output:
```
Vector(4, 6)
True
False
5.0
```

> **Note:** Magnitude is `sqrt(x^2 + y^2)`, rounded to 4 decimal places. For `(3, 4)` this is exactly `5.0`.

## Further Reading

- *Think Python* — Chapter 17 discusses special methods and operator overloading.
  [https://greenteapress.com/thinkpython2/thinkpython2.pdf](https://greenteapress.com/thinkpython2/thinkpython2.pdf)
- *MIT OCW 6.0001* — Lecture 9 includes examples of `__str__` and `__repr__`.
  [https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/](https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/)
