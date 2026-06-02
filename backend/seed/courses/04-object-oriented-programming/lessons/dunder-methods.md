# Dunder Methods: Python's Object Protocol

Python's **dunder methods** (double-underscore methods, also called *magic methods* or *special methods*) are the hooks that let your custom classes integrate seamlessly with the Python language itself — operators, built-in functions, containers, context managers, and more. Understanding dunders is what separates a class that *works* from a class that *feels native*.

## What Are Dunder Methods?

A dunder method is any method whose name starts and ends with two underscores: `__init__`, `__repr__`, `__len__`, etc. Python calls these implicitly when you use operators or built-ins on an object. You never call them directly (usually); instead, Python does.

```python
x = 5
y = 3
result = x + y   # Python calls int.__add__(x, y) internally
```

## The Most Essential Dunders

| Dunder | Triggered by | Purpose |
|--------|-------------|---------|
| `__init__` | `MyClass()` | Initialise a new instance |
| `__repr__` | `repr(obj)`, REPL display | Unambiguous developer string |
| `__str__` | `str(obj)`, `print(obj)` | Readable user-facing string |
| `__len__` | `len(obj)` | Return integer length |
| `__getitem__` | `obj[key]` | Indexing / slicing |
| `__setitem__` | `obj[key] = val` | Index assignment |
| `__contains__` | `item in obj` | Membership test |
| `__iter__` / `__next__` | `for x in obj` | Iteration protocol |
| `__eq__`, `__lt__` | `==`, `<` | Equality and ordering |
| `__add__`, `__mul__` | `+`, `*` | Arithmetic operators |
| `__enter__` / `__exit__` | `with obj:` | Context manager protocol |
| `__call__` | `obj(args)` | Make an instance callable |

## Building a Rich Class: `Vector2D`

Here is a 2D vector class that implements many dunders to feel completely native:

```python
import math

class Vector2D:
    """An immutable 2-D vector supporting arithmetic and comparison."""

    def __init__(self, x: float, y: float) -> None:
        self._x = float(x)
        self._y = float(y)

    # --- display ---
    def __repr__(self) -> str:
        return f"Vector2D({self._x}, {self._y})"

    def __str__(self) -> str:
        return f"({self._x}, {self._y})"

    # --- arithmetic ---
    def __add__(self, other: "Vector2D") -> "Vector2D":
        return Vector2D(self._x + other._x, self._y + other._y)

    def __sub__(self, other: "Vector2D") -> "Vector2D":
        return Vector2D(self._x - other._x, self._y - other._y)

    def __mul__(self, scalar: float) -> "Vector2D":
        return Vector2D(self._x * scalar, self._y * scalar)

    def __rmul__(self, scalar: float) -> "Vector2D":
        return self.__mul__(scalar)   # handles  3 * v  (scalar on left)

    # --- comparison ---
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector2D):
            return NotImplemented
        return self._x == other._x and self._y == other._y

    def __abs__(self) -> float:
        """Magnitude: abs(v)"""
        return math.sqrt(self._x ** 2 + self._y ** 2)

    # --- length via len ---
    def __len__(self) -> int:
        """Number of dimensions — always 2."""
        return 2

    # --- indexing ---
    def __getitem__(self, index: int) -> float:
        return (self._x, self._y)[index]

    # --- properties ---
    @property
    def x(self) -> float: return self._x

    @property
    def y(self) -> float: return self._y
```

Usage feels completely natural:

```python
a = Vector2D(3, 4)
b = Vector2D(1, 2)

print(a + b)      # (4.0, 6.0)
print(a - b)      # (2.0, 2.0)
print(3 * a)      # (9.0, 12.0)
print(abs(a))     # 5.0
print(a == b)     # False
print(len(a))     # 2
print(a[0])       # 3.0
print(repr(a))    # Vector2D(3.0, 4.0)
```

## Context Managers with `__enter__` / `__exit__`

The `with` statement calls `__enter__` on entry and `__exit__` on exit (even after exceptions):

```python
class Timer:
    """Measures elapsed time for a block of code."""

    import time as _time

    def __enter__(self):
        self._start = self._time.perf_counter()
        return self   # the value bound in  `as`

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = self._time.perf_counter() - self._start
        print(f"Elapsed: {elapsed:.4f}s")
        return False  # do not suppress exceptions
```

```python
with Timer() as t:
    total = sum(range(10_000_000))
# Prints: Elapsed: 0.3421s  (approximate)
```

If `__exit__` returns `True`, any exception raised inside the `with` block is suppressed. Return `False` (or `None`) to let it propagate.

## Callable Objects with `__call__`

Defining `__call__` makes an instance behave like a function. This is the foundation of the **Strategy** and **Command** patterns in Python:

```python
class Multiplier:
    """Returns a callable that multiplies its argument by a fixed factor."""

    def __init__(self, factor: float) -> None:
        self.factor = factor

    def __call__(self, value: float) -> float:
        return value * self.factor

double = Multiplier(2)
triple = Multiplier(3)

print(double(5))          # 10.0
print(triple(5))          # 15.0
print(list(map(double, [1, 2, 3])))  # [2.0, 4.0, 6.0]
```

## Returning `NotImplemented`

When a dunder cannot handle the operand type, return `NotImplemented` (not `raise NotImplementedError`). This signals Python to try the reflected operation on the other operand:

```python
def __add__(self, other):
    if not isinstance(other, Vector2D):
        return NotImplemented   # let Python try other.__radd__(self)
    return Vector2D(self._x + other._x, self._y + other._y)
```

## Key Takeaways

- Dunder methods are how your class participates in Python's operator and protocol system.
- `__repr__` should return an unambiguous string; `__str__` the user-friendly version.
- Implement `__eq__` whenever you define comparison logic; Python will also handle `!=` automatically.
- Use `__enter__`/`__exit__` to write clean resource-management context managers.
- Return `NotImplemented` (not raise) from operator dunders to allow Python to try the reflected operation.
