# Multiple Inheritance and the Method Resolution Order

Python supports **multiple inheritance** — a class can inherit from more than one parent simultaneously. This is a powerful but easily misused feature. Understanding the **Method Resolution Order (MRO)** is essential to using it safely and to writing correct `super()` calls in class hierarchies with more than one parent.

## Basic Multiple Inheritance

```python
class Flyable:
    def move(self) -> str:
        return "flying"

    def describe(self) -> str:
        return "I can fly"

class Swimmable:
    def move(self) -> str:
        return "swimming"

    def describe(self) -> str:
        return "I can swim"

class Duck(Flyable, Swimmable):
    pass

d = Duck()
print(d.move())      # "flying"  — Flyable wins (listed first)
print(d.describe())  # "I can fly"
```

When `Duck` inherits from both `Flyable` and `Swimmable`, Python must decide which `move()` to call. The answer is determined by the **MRO**.

## The C3 Linearization Algorithm

Python uses the **C3 linearization** algorithm to compute a deterministic, consistent MRO for every class. You can inspect any class's MRO with:

```python
print(Duck.__mro__)
# (<class 'Duck'>, <class 'Flyable'>, <class 'Swimmable'>, <class 'object'>)

print([cls.__name__ for cls in Duck.__mro__])
# ['Duck', 'Flyable', 'Swimmable', 'object']
```

Python searches this list **left to right**, stopping at the first class that defines the method. The rules that C3 guarantees:

| Rule | Meaning |
|------|---------|
| Child before parents | `Duck` is checked before `Flyable` or `Swimmable` |
| Left-to-right among parents | `Flyable` is checked before `Swimmable` |
| Monotonicity | The same relative order is preserved in all subclasses |

## The Diamond Problem

The classic pitfall of multiple inheritance is the **diamond problem**: a method is reachable via two paths, and calling it naively would invoke it twice.

```
       Animal
      /      \
  Mammal    Bird
      \      /
       Platypus
```

```python
class Animal:
    def __init__(self):
        print("Animal.__init__")
        self.alive = True

class Mammal(Animal):
    def __init__(self):
        print("Mammal.__init__")
        super().__init__()   # cooperative — delegates up the MRO
        self.warm_blooded = True

class Bird(Animal):
    def __init__(self):
        print("Bird.__init__")
        super().__init__()   # cooperative
        self.has_wings = True

class Platypus(Mammal, Bird):
    def __init__(self):
        print("Platypus.__init__")
        super().__init__()   # cooperative
```

```python
p = Platypus()
# Platypus.__init__
# Mammal.__init__
# Bird.__init__
# Animal.__init__
```

`Animal.__init__` runs **once**, not twice. This is because every class uses `super()`, which follows the MRO (`Platypus -> Mammal -> Bird -> Animal`). Without `super()`, `Animal.__init__` would run twice and complex hierarchies would break.

## Mixins: The Safe Use of Multiple Inheritance

The most practical and least error-prone use of multiple inheritance is the **mixin pattern**: small, focused classes that add a specific capability to any class that inherits them.

```python
class LoggingMixin:
    """Adds a .log() helper to any class."""

    def log(self, message: str) -> None:
        print(f"[{type(self).__name__}] {message}")

class SerializationMixin:
    """Adds basic dict serialization to any class."""

    def to_dict(self) -> dict:
        return {k: v for k, v in vars(self).items() if not k.startswith("_")}

class User(LoggingMixin, SerializationMixin):
    def __init__(self, name: str, email: str) -> None:
        self.name  = name
        self.email = email

    def register(self) -> None:
        self.log(f"Registering {self.name}")
        # ... registration logic ...
```

```python
u = User("Alice", "alice@example.com")
u.register()         # [User] Registering Alice
print(u.to_dict())   # {'name': 'Alice', 'email': 'alice@example.com'}
```

Mixin best practices:

- Mixins should not have their own `__init__` (or if they do, they must call `super().__init__()`).
- A mixin should add one focused capability.
- Name mixins with the `Mixin` suffix to signal their purpose.
- Place mixins to the **left** of the base class in the inheritance list so they are checked first.

## When to Avoid Multiple Inheritance

Multiple inheritance quickly becomes confusing when:

- Each parent has its own `__init__` with different signatures.
- Two parents define a method with the same name but incompatible semantics.
- You need to trace the MRO across four or more classes to understand behavior.

In these cases, **composition** (holding a parent-like object as an attribute) is almost always clearer:

```python
# Composition alternative to mixin
class Logger:
    def log(self, source: str, message: str) -> None:
        print(f"[{source}] {message}")

class User:
    def __init__(self, name: str) -> None:
        self.name = name
        self._logger = Logger()

    def register(self) -> None:
        self._logger.log("User", f"Registering {self.name}")
```

## Key Takeaways

- Python resolves multiple inheritance using **C3 linearization** — inspect `ClassName.__mro__` to see the order.
- Use `super()` consistently in every class so the MRO is followed correctly and methods like `__init__` run exactly once.
- The **mixin pattern** — small, single-purpose classes added via multiple inheritance — is the most practical and safe use case.
- When the inheritance graph becomes complex or parent `__init__` signatures differ, switch to **composition**.
