# Classes and Dataclasses

## A basic class

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance_to(self, other):
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def __repr__(self):
        return f"Point(x={self.x}, y={self.y})"
```

- `__init__` is the constructor.
- The first parameter of any method is `self` — the instance.
- `__repr__` (and `__str__`) control how the object prints.

## Class vs instance state

```python
class Counter:
    total = 0                  # class variable, shared across instances

    def __init__(self):
        self.n = 0             # instance variable

    def inc(self):
        self.n += 1
        Counter.total += 1
```

Use `cls` to refer to the class inside class methods:

```python
class Foo:
    @classmethod
    def from_dict(cls, d):
        return cls(**d)
```

## Inheritance

```python
class Animal:
    def speak(self):
        return "..."

class Dog(Animal):
    def speak(self):
        return "woof"

class Cat(Animal):
    def speak(self):
        return "meow"
```

Call the parent:

```python
class Dog(Animal):
    def speak(self):
        return super().speak() + " woof"
```

## Properties

Computed attributes that look like fields:

```python
class Temp:
    def __init__(self, c):
        self._c = c

    @property
    def celsius(self):
        return self._c

    @celsius.setter
    def celsius(self, value):
        if value < -273.15: raise ValueError
        self._c = value

    @property
    def fahrenheit(self):
        return self._c * 9/5 + 32
```

## Dataclasses — the modern way

Most "classes that hold data" should be `@dataclass`:

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class User:
    id: int
    name: str
    email: Optional[str] = None
    tags: list[str] = field(default_factory=list)

u = User(id=1, name="Alice")
# auto-generates __init__, __repr__, __eq__
```

Useful flags:

```python
@dataclass(frozen=True)        # immutable + hashable
@dataclass(slots=True)         # smaller, faster attribute access
@dataclass(kw_only=True)       # force keyword arguments
@dataclass(order=True)         # adds <, <=, >, >=
```

Use `field(default_factory=list)` for mutable defaults — `[]` directly is the same trap as `def f(x, history=[])`.

## Magic methods (dunder methods)

A handful that come up often:

| Method                | Purpose                          |
|-----------------------|----------------------------------|
| `__init__`            | Constructor                      |
| `__repr__`            | Debug/dev string                 |
| `__str__`             | User-facing string               |
| `__eq__`, `__hash__`  | Equality and hashability         |
| `__lt__`, `__le__`... | Ordering                         |
| `__len__`             | `len(x)`                         |
| `__iter__`            | Make iterable                    |
| `__contains__`        | `x in obj`                       |
| `__getitem__`         | `obj[key]`                       |
| `__enter__`/`__exit__`| `with` statement                 |
| `__call__`            | Make instance callable           |

## When NOT to write a class

Python is happy without OOP. Functions + dataclasses + dicts cover most needs. Reach for classes when:

- You're modeling a thing with both state and behavior.
- You want polymorphism (multiple types share an interface).
- You need a context manager or iterator.

Avoid classes that are just a namespace with no state — those are modules.
