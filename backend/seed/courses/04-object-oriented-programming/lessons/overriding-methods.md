# Overriding Methods

**Method overriding** allows a subclass to provide its own implementation of a method already defined in the parent class. The subclass version is called instead of the parent version when the method is invoked on a subclass instance. This is one of the main mechanisms that makes polymorphism work.

## Basic Override

```python
class Shape:
    def area(self) -> float:
        return 0.0

    def describe(self) -> str:
        return f"I am a {type(self).__name__} with area {self.area():.2f}"


class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:               # overrides Shape.area
        import math
        return math.pi * self.radius ** 2


class Rectangle(Shape):
    def __init__(self, w: float, h: float):
        self.w = w
        self.h = h

    def area(self) -> float:               # overrides Shape.area
        return self.w * self.h


class Triangle(Shape):
    def __init__(self, base: float, height: float):
        self.base   = base
        self.height = height

    def area(self) -> float:
        return 0.5 * self.base * self.height
```

```python
shapes = [Circle(5), Rectangle(4, 6), Triangle(3, 8), Shape()]

for s in shapes:
    print(s.describe())
# I am a Circle with area 78.54
# I am a Rectangle with area 24.00
# I am a Triangle with area 12.00
# I am a Shape with area 0.00
```

`describe()` is defined once in `Shape` and never overridden. But it calls `self.area()`, and `self` is always the concrete subclass object — so the right `area()` is called. This is **dynamic dispatch**.

## Two Override Patterns: Replace vs Extend

**Replace** — the subclass completely rewrites the behaviour:

```python
class SilentList(list):
    def append(self, item):
        # Completely replaces list.append — no logging
        super().append(item)   # still does the actual work
```

**Extend** — the subclass adds behaviour before or after calling the parent:

```python
class BankAccount:
    def __init__(self, owner: str):
        self.owner   = owner
        self._balance = 0.0

    def deposit(self, amount: float) -> None:
        self._balance += amount

    @property
    def balance(self) -> float:
        return self._balance


class PremiumAccount(BankAccount):
    CASHBACK_RATE = 0.02   # 2% cashback

    def deposit(self, amount: float) -> None:
        cashback = round(amount * self.CASHBACK_RATE, 2)
        super().deposit(amount + cashback)   # extend: add cashback before delegating
        print(f"Cashback applied: {cashback:.2f}")
```

```python
acc = PremiumAccount("Alice")
acc.deposit(100)    # prints: Cashback applied: 2.00
print(acc.balance)  # 102.0
```

## Calling the Parent Version Explicitly

Use `super().method_name(args)` to invoke the parent's implementation from within an override:

```python
class Animal:
    def __init__(self, name: str):
        self.name = name

    def describe(self) -> str:
        return f"Animal named {self.name}"


class Dog(Animal):
    def __init__(self, name: str, breed: str):
        super().__init__(name)    # initialize the Animal part
        self.breed = breed

    def describe(self) -> str:
        parent_desc = super().describe()     # reuse parent logic
        return f"{parent_desc}, breed: {self.breed}"
```

```python
d = Dog("Rex", "Labrador")
print(d.describe())  # Animal named Rex, breed: Labrador
```

## Overriding Dunder Methods

You can override any dunder method to make your objects integrate naturally with Python's built-ins:

```python
class BoundedList:
    """A list with a maximum capacity."""

    def __init__(self, capacity: int):
        self._items    = []
        self._capacity = capacity

    def add(self, item) -> None:
        if len(self._items) >= self._capacity:
            raise OverflowError(f"BoundedList is full (capacity {self._capacity})")
        self._items.append(item)

    def __len__(self) -> int:
        return len(self._items)

    def __contains__(self, item) -> bool:
        return item in self._items

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, index):
        return self._items[index]

    def __repr__(self) -> str:
        return f"BoundedList(capacity={self._capacity}, items={self._items!r})"
```

```python
bl = BoundedList(3)
bl.add("a")
bl.add("b")
print(len(bl))         # 2
print("a" in bl)       # True
print(list(bl))        # ['a', 'b']
bl.add("c")
bl.add("d")            # OverflowError: BoundedList is full (capacity 3)
```

## Before/After Refactoring: Adding Logging to an Existing Class

A common real-world scenario: you inherit from a third-party or framework class and need to add logging without modifying the original.

**Before** (without override):

```python
# We would have to edit the original class, or duplicate it
class DataProcessor:
    def process(self, data: list) -> list:
        return [x * 2 for x in data]
```

**After** (clean override via subclass):

```python
class LoggingDataProcessor(DataProcessor):
    def process(self, data: list) -> list:
        print(f"[LOG] Processing {len(data)} items")
        result = super().process(data)   # delegate actual work
        print(f"[LOG] Done. Result has {len(result)} items")
        return result
```

```python
p = LoggingDataProcessor()
p.process([1, 2, 3])
# [LOG] Processing 3 items
# [LOG] Done. Result has 3 items
```

The original `DataProcessor` is untouched. This is the **Open/Closed Principle** in action.

## Method Override Pitfalls

### Forgetting to call `super()`

```python
class Child(Parent):
    def __init__(self, x, y):
        # BUG: Parent.__init__ never called — parent attributes missing
        self.y = y
```

Always call `super().__init__(...)` unless you have a very specific reason not to.

### Changing the method signature

```python
class Base:
    def process(self, data: list) -> list: ...

class Sub(Base):
    def process(self, data: list, extra: str) -> list:  # added required arg
        ...
```

Callers who pass a `Sub` where a `Base` is expected will crash. This violates the **Liskov Substitution Principle** (covered in the SOLID module).

### Weakening preconditions in the wrong direction

A subclass override must accept at least as much as the parent (don't add new required checks that callers don't know about) and must deliver at least as much as the parent promises.

## Composition vs Inheritance

Inheritance should express an IS-A relationship. When the relationship is HAS-A, prefer composition:

```python
# Inheritance (IS-A): LoggingList IS-A list — reasonable
class LoggingList(list):
    def append(self, item):
        print(f"Appending: {item}")
        super().append(item)

# Composition (HAS-A): Logger HAS-A list — better design
class Logger:
    def __init__(self):
        self._entries: list = []

    def log(self, message: str) -> None:
        self._entries.append(message)
        print(f"[LOG] {message}")

    def history(self) -> list:
        return list(self._entries)
```

`Logger` does not need to be a `list`; it just happens to use one internally.

## Key Takeaways

- Override a method by redefining it in the subclass with the same name.
- Use `super().method()` to reuse the parent's logic inside the override.
- Dynamic dispatch ensures the correct (most-derived) method is always called on `self`.
- Do not change the method signature (parameter count/types) in ways that break callers.
- Prefer composition over deep inheritance hierarchies for better flexibility and testability.
