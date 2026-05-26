# Abstract Base Classes and Interfaces

In many languages, an **interface** is a pure contract — a list of method signatures with no implementation. Python achieves the same goal with **Abstract Base Classes (ABCs)** from the `abc` module, and with structural protocols via `typing.Protocol`. Understanding both gives you the full toolkit for interface design in Python.

## Interfaces as Contracts

An interface answers: *What can this object do?* It says nothing about *how* — that is the implementing class's job.

```python
from abc import ABC, abstractmethod

class Drawable(ABC):
    """Anything that can draw itself to a canvas."""

    @abstractmethod
    def draw(self, canvas) -> None: ...

    @abstractmethod
    def bounding_box(self) -> tuple: ...   # returns (x, y, width, height)


class Resizable(ABC):
    """Anything that can be resized by a scale factor."""

    @abstractmethod
    def resize(self, factor: float) -> None: ...


class Serializable(ABC):
    """Anything that can be saved and restored."""

    @abstractmethod
    def to_dict(self) -> dict: ...

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict) -> "Serializable": ...
```

## Multiple Inheritance for Interface Composition

Python allows a class to inherit from multiple ABCs, modelling "implements multiple interfaces":

```python
class Widget(Drawable, Resizable, Serializable):
    """A UI widget that can be drawn, resized, and persisted."""

    def __init__(self, x: int, y: int, w: int, h: int, label: str):
        self.x, self.y  = x, y
        self.w, self.h  = w, h
        self.label      = label

    def draw(self, canvas) -> None:
        print(f"Drawing {self.label!r} at ({self.x},{self.y}) size {self.w}x{self.h}")

    def bounding_box(self) -> tuple:
        return (self.x, self.y, self.w, self.h)

    def resize(self, factor: float) -> None:
        self.w = int(self.w * factor)
        self.h = int(self.h * factor)

    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y, "w": self.w, "h": self.h, "label": self.label}

    @classmethod
    def from_dict(cls, data: dict) -> "Widget":
        return cls(data["x"], data["y"], data["w"], data["h"], data["label"])
```

```python
btn = Widget(10, 20, 100, 40, "OK")
btn.draw(None)           # Drawing 'OK' at (10,20) size 100x40
btn.resize(2.0)
btn.draw(None)           # Drawing 'OK' at (10,20) size 200x80

data = btn.to_dict()
restored = Widget.from_dict(data)
restored.draw(None)      # Drawing 'OK' at (10,20) size 200x80
```

## Python's Built-in ABCs (`collections.abc`)

The standard library ships with many ready-made ABCs. Implementing a few methods grants many more for free:

| ABC | Required methods | Provided for free |
|-----|-----------------|-------------------|
| `Iterable` | `__iter__` | — |
| `Sized` | `__len__` | — |
| `Container` | `__contains__` | — |
| `Sequence` | `__getitem__`, `__len__` | `__iter__`, `__reversed__`, `index()`, `count()`, `__contains__` |
| `MutableSequence` | + `__setitem__`, `__delitem__`, `insert` | `append()`, `clear()`, `reverse()`, etc. |
| `Mapping` | `__getitem__`, `__len__`, `__iter__` | `keys()`, `values()`, `items()`, `get()`, etc. |

```python
from collections.abc import Sequence

class FibSequence(Sequence):
    """An immutable sequence of the first n Fibonacci numbers."""

    def __init__(self, n: int):
        a, b, data = 0, 1, []
        for _ in range(n):
            data.append(a)
            a, b = b, a + b
        self._data = data

    def __getitem__(self, index):
        return self._data[index]

    def __len__(self) -> int:
        return len(self._data)
```

```python
fib = FibSequence(8)
print(list(fib))           # [0, 1, 1, 2, 3, 5, 8, 13]
print(fib[3])              # 2
print(len(fib))            # 8
print(5 in fib)            # True  — __contains__ provided for free by Sequence
print(list(reversed(fib))) # [13, 8, 5, 3, 2, 1, 1, 0]
print(fib.count(1))        # 2
print(fib.index(5))        # 5
```

By implementing just `__getitem__` and `__len__`, we automatically get iteration, containment testing, reversal, index lookup, and counting — all provided by `Sequence`.

## Checking for Interface Compliance

```python
from collections.abc import Sequence, Mapping, Iterable

print(isinstance([], Sequence))               # True
print(isinstance({}, Mapping))                # True
print(isinstance(FibSequence(5), Sequence))   # True
print(isinstance(FibSequence(5), Iterable))   # True — Sequence implies Iterable
print(isinstance((1, 2), Sequence))           # True — tuples are sequences
print(isinstance("hello", Sequence))          # True — strings too
```

## Protocols: Structural Subtyping

Python 3.8+ offers `typing.Protocol` for **structural** (duck-typed) interfaces. No explicit inheritance is required; a class satisfies a Protocol simply by having the right attributes:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Drawable(Protocol):
    def draw(self) -> None: ...

class Button:
    def draw(self) -> None:
        print("Drawing button")

class Icon:
    def draw(self) -> None:
        print("Drawing icon")

class TextNode:
    def render(self) -> None:   # different method — does NOT satisfy Drawable
        print("Rendering text")

def render_ui(components: list) -> None:
    for c in components:
        c.draw()

render_ui([Button(), Icon()])
# Drawing button
# Drawing icon

# With @runtime_checkable you can use isinstance:
print(isinstance(Button(), Drawable))    # True
print(isinstance(TextNode(), Drawable))  # False — no .draw() method
```

Protocols are especially useful in library code where you don't control the classes that will be passed in.

## ABCs vs Protocols: When to Use Each

| | Abstract Base Class (ABC) | Protocol |
|---|---|---|
| Enforces interface | At instantiation time | Statically (mypy/pyright) or at runtime with `@runtime_checkable` |
| Inheritance required | Yes | No |
| Provides concrete methods | Yes — shared helpers | No |
| Best for | Framework base classes; shared default implementations | Third-party classes; structural typing; static analysis |

**Use ABCs** when you control the class hierarchy and want to share implementation code or catch errors early.
**Use Protocols** when you want to describe what an object can *do* without constraining its class hierarchy.

## A Practical Pattern: Repository Interface

```python
from abc import ABC, abstractmethod
from typing import List, Optional

class UserRepository(ABC):
    """Abstract repository — the contract every storage backend must satisfy."""

    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[dict]: ...

    @abstractmethod
    def find_all(self) -> List[dict]: ...

    @abstractmethod
    def save(self, user: dict) -> None: ...

    @abstractmethod
    def delete(self, user_id: int) -> bool: ...


class InMemoryUserRepository(UserRepository):
    """In-memory implementation — ideal for unit tests."""

    def __init__(self):
        self._store: dict = {}
        self._next_id = 1

    def save(self, user: dict) -> None:
        if "id" not in user:
            user["id"] = self._next_id
            self._next_id += 1
        self._store[user["id"]] = user.copy()

    def find_by_id(self, user_id: int) -> Optional[dict]:
        return self._store.get(user_id)

    def find_all(self) -> List[dict]:
        return list(self._store.values())

    def delete(self, user_id: int) -> bool:
        if user_id in self._store:
            del self._store[user_id]
            return True
        return False
```

```python
repo = InMemoryUserRepository()
repo.save({"name": "Alice", "email": "alice@example.com"})
repo.save({"name": "Bob",   "email": "bob@example.com"})

print(repo.find_all())
# [{'name': 'Alice', 'email': 'alice@example.com', 'id': 1},
#  {'name': 'Bob',   'email': 'bob@example.com',   'id': 2}]

print(repo.find_by_id(1))   # {'name': 'Alice', ...}
print(repo.delete(2))       # True
print(repo.find_all())      # only Alice
```

Production code would inject a `SQLUserRepository` instead — `UserRepository` is the stable, abstract contract that both share.

## Key Takeaways

- ABCs define a **contract** that subclasses must fulfil; Python enforces it at instantiation time.
- Multiple ABC inheritance models "implements multiple interfaces".
- `collections.abc` provides useful built-in ABCs; implementing a few methods grants many more for free via mixin logic.
- `typing.Protocol` offers structural subtyping — compliance checked by structure, not inheritance.
- Use ABCs for shared base classes; use Protocols for duck-typed interfaces and static analysis.
