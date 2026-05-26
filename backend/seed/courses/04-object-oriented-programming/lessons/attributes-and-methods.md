# Attributes and Methods in Depth

Every Python class is built from two raw materials: **attributes** (data) and **methods** (functions bound to an object). Understanding both thoroughly is essential before tackling more advanced OOP topics.

## Instance Attributes vs Class Attributes

Python distinguishes between attributes that belong to a *specific instance* and attributes that belong to the *class itself*.

```python
class Dog:
    species = "Canis lupus familiaris"   # class attribute — shared by ALL instances

    def __init__(self, name: str, breed: str):
        self.name  = name    # instance attribute — unique to each dog
        self.breed = breed
```

```python
rex  = Dog("Rex",  "German Shepherd")
fido = Dog("Fido", "Labrador")

print(rex.species)   # "Canis lupus familiaris"  (from class)
print(fido.species)  # "Canis lupus familiaris"  (same class attribute)

print(rex.name)      # "Rex"   (rex's own attribute)
print(fido.name)     # "Fido"  (fido's own attribute)
```

**Important trap — mutable class attributes:** If a class attribute is a mutable object (like a list), all instances share the same object:

```python
class Buggy:
    items = []    # shared list — danger!

    def add(self, x):
        self.items.append(x)

a = Buggy()
b = Buggy()
a.add(1)
print(b.items)   # [1]  — b sees a's change! Bug!
```

Fix: always initialize mutable attributes in `__init__`:

```python
class Fixed:
    def __init__(self):
        self.items = []   # each instance gets its own list
```

**Rule of thumb:** If all instances share the same *immutable* value (a constant), use a class attribute. If it can vary per object or is mutable, use an instance attribute.

## The `__init__` Constructor

`__init__` is called automatically when you write `Dog("Rex", "GS")`. Its job is to set up the object's initial state by assigning instance attributes via `self`.

```python
class Rectangle:
    def __init__(self, width: float, height: float = None):
        if width <= 0:
            raise ValueError(f"Width must be positive, got {width}")
        self.width  = width
        self.height = height if height is not None else width  # square if no height
        self._area  = None   # cached, computed lazily

    def area(self) -> float:
        if self._area is None:
            self._area = self.width * self.height
        return self._area
```

`self` is always the first parameter of an instance method. Python passes the new object automatically — you never supply `self` when calling.

Best practice: assign **every** attribute in `__init__`, even if the initial value is `None`. This makes the object's "shape" clear at a glance.

## Regular Methods, Class Methods, and Static Methods

```python
import math

class Circle:
    PI = math.pi   # class constant

    def __init__(self, radius: float):
        if radius <= 0:
            raise ValueError("Radius must be positive")
        self.radius = radius

    # Regular (instance) method — receives the instance via self
    def area(self) -> float:
        return Circle.PI * self.radius ** 2

    def circumference(self) -> float:
        return 2 * Circle.PI * self.radius

    # Class method — receives the class via cls; perfect for alternate constructors
    @classmethod
    def unit(cls) -> "Circle":
        """Create a unit circle (radius = 1)."""
        return cls(radius=1.0)

    @classmethod
    def from_diameter(cls, diameter: float) -> "Circle":
        return cls(radius=diameter / 2)

    # Static method — no implicit first argument; a pure utility tied to the class
    @staticmethod
    def is_valid_radius(r: float) -> bool:
        return r > 0

    def __repr__(self) -> str:
        return f"Circle(radius={self.radius})"
```

```python
c1 = Circle(5)
print(f"Area: {c1.area():.4f}")           # Area: 78.5398
print(f"Circumference: {c1.circumference():.4f}")  # Circumference: 31.4159

c2 = Circle.unit()                 # alternate constructor
print(c2.radius)                   # 1.0

c3 = Circle.from_diameter(10)
print(c3.radius)                   # 5.0

print(Circle.is_valid_radius(-3))  # False
```

### When to use each type

| Decorator | First arg | Use when |
|-----------|-----------|----------|
| *(none)* | `self` (instance) | Method needs to read/modify instance state |
| `@classmethod` | `cls` (class) | Alternative constructors; factory methods; accessing class-level state |
| `@staticmethod` | *(nothing)* | A utility logically grouped with the class but needing no instance or class |

## The `__str__` and `__repr__` Methods

These special (dunder) methods control how an object is displayed:

```python
class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        # Goal: unambiguous, ideally eval-able
        return f"Point({self.x!r}, {self.y!r})"

    def __str__(self) -> str:
        # Goal: human-friendly
        return f"({self.x}, {self.y})"

    def distance_to(self, other: "Point") -> float:
        return ((self.x - other.x)**2 + (self.y - other.y)**2) ** 0.5
```

```python
p = Point(3, 4)
print(repr(p))   # Point(3, 4)    -- used in debugger, REPL, containers
print(str(p))    # (3, 4)         -- used by print()
print(p)         # (3, 4)         -- print() calls __str__

points = [Point(1, 0), Point(0, 1)]
print(points)    # [Point(1, 0), Point(0, 1)]  -- list uses __repr__ for items
```

**Rule:** Always define `__repr__`. Define `__str__` only when you want a different display for end-users.

## Rich Comparison Methods

Python lets you define all comparison operators through dunder methods, enabling natural sorting of custom objects:

```python
class Student:
    def __init__(self, name: str, gpa: float):
        self.name = name
        self.gpa  = gpa

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Student):
            return NotImplemented
        return self.gpa == other.gpa

    def __lt__(self, other: "Student") -> bool:
        return self.gpa < other.gpa

    def __repr__(self) -> str:
        return f"Student({self.name!r}, gpa={self.gpa})"
```

```python
from functools import total_ordering   # generates <=, >, >= from __eq__ and __lt__

students = [Student("Alice", 3.9), Student("Bob", 3.7), Student("Carol", 3.95)]
print(sorted(students))
# [Student('Bob', gpa=3.7), Student('Alice', gpa=3.9), Student('Carol', gpa=3.95)]
```

The `functools.total_ordering` class decorator (not shown above since `Student` defines only `__eq__` and `__lt__`) can auto-generate the remaining comparison operators.

## Key Method Naming Conventions

| Dunder | Purpose | Triggered by |
|--------|---------|--------------|
| `__init__` | Constructor — set up initial state | `MyClass(args)` |
| `__str__` | Human-readable string | `print(obj)`, `str(obj)` |
| `__repr__` | Developer string / unambiguous | `repr(obj)`, REPL display, lists |
| `__len__` | Length | `len(obj)` |
| `__eq__` | Equality | `obj == other` |
| `__lt__` | Less-than | `obj < other` (sorting) |
| `__hash__` | Hashability | `hash(obj)`, use in sets/dicts |
| `__bool__` | Truth value | `if obj:` |
| `__contains__` | Membership | `x in obj` |
| `__getitem__` | Subscripting | `obj[key]` |

These are called **dunder** (double-underscore) methods and form the backbone of Python's data model.

## A Complete Example: Inventory Item

Putting it all together:

```python
class InventoryItem:
    """Tracks a product in a warehouse."""

    LOW_STOCK_THRESHOLD = 10   # class constant

    def __init__(self, sku: str, name: str, quantity: int, unit_price: float):
        self.sku        = sku
        self.name       = name
        self.quantity   = quantity
        self.unit_price = unit_price

    @classmethod
    def from_dict(cls, data: dict) -> "InventoryItem":
        return cls(data["sku"], data["name"], data["quantity"], data["unit_price"])

    @property
    def total_value(self) -> float:
        return self.quantity * self.unit_price

    @property
    def is_low_stock(self) -> bool:
        return self.quantity < InventoryItem.LOW_STOCK_THRESHOLD

    def restock(self, units: int) -> None:
        if units <= 0:
            raise ValueError("Restock amount must be positive")
        self.quantity += units

    def sell(self, units: int) -> bool:
        if units > self.quantity:
            return False
        self.quantity -= units
        return True

    def __repr__(self) -> str:
        return f"InventoryItem({self.sku!r}, qty={self.quantity})"

    def __str__(self) -> str:
        return f"{self.name} (SKU: {self.sku}) x{self.quantity} @ ${self.unit_price:.2f}"
```

```python
item = InventoryItem.from_dict({
    "sku": "WDG-001", "name": "Widget", "quantity": 5, "unit_price": 9.99
})
print(item)               # Widget (SKU: WDG-001) x5 @ $9.99
print(item.total_value)   # 49.95
print(item.is_low_stock)  # True  (5 < 10)
item.restock(20)
print(item.quantity)      # 25
item.sell(3)
print(item.quantity)      # 22
```

## Summary

- **Instance attributes** live on each object; **class attributes** are shared — watch out for mutable class attributes.
- `__init__` is the constructor — assign all attributes here, validate early.
- Use `@classmethod` for alternate constructors, `@staticmethod` for class-related utilities.
- Always define `__repr__`; define `__str__` when a user-friendly display differs.
- Dunder methods let your objects participate naturally in Python's built-in operations.
