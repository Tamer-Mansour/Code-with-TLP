# Properties and Invariants

Properties are Python's built-in mechanism for computed attributes and enforced constraints. They let you start with a plain attribute and upgrade to a full getter/setter *without changing the public API* — callers never notice the difference.

## A Practical Example: Bounded Integer

```python
class Percentage:
    """Stores a value between 0 and 100 (inclusive)."""

    def __init__(self, value: float):
        self.value = value          # calls the setter immediately

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, v: float) -> None:
        if not 0 <= v <= 100:
            raise ValueError(f"Percentage must be 0-100, got {v}")
        self._value = float(v)

    @property
    def as_fraction(self) -> float:
        """Read-only derived property — no setter defined."""
        return self._value / 100.0

    def __repr__(self) -> str:
        return f"Percentage({self._value}%)"
```

```python
p = Percentage(75)
print(p.value)          # 75.0
print(p.as_fraction)    # 0.75

p.value = 50            # OK
p.value = 110           # ValueError: Percentage must be 0-100, got 110
p.as_fraction = 0.5     # AttributeError: can't set attribute (no setter defined)
```

Notice `as_fraction` has no setter — it is **read-only** because only the getter is defined.

## Computed and Cached Properties

A property can compute its result from other attributes:

```python
class Circle:
    import math as _math

    def __init__(self, radius: float):
        self.radius = radius        # setter validates

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, v: float) -> None:
        if v <= 0:
            raise ValueError("Radius must be positive")
        self._radius  = v
        self._area_cache = None     # invalidate cached value when radius changes

    @property
    def area(self) -> float:
        if self._area_cache is None:
            import math
            self._area_cache = math.pi * self._radius ** 2
        return self._area_cache

    @property
    def circumference(self) -> float:
        import math
        return 2 * math.pi * self._radius
```

```python
c = Circle(5)
print(f"{c.area:.4f}")          # 78.5398
c.radius = 10                   # cache is invalidated
print(f"{c.area:.4f}")          # 314.1593  (recomputed)
print(f"{c.circumference:.4f}") # 62.8319
```

## Deleter Properties

Define `@name.deleter` to handle `del obj.attr`:

```python
class CachedResult:
    def __init__(self):
        self._cache = None
        self._hits  = 0

    @property
    def result(self):
        return self._cache

    @result.setter
    def result(self, value):
        self._cache = value
        self._hits += 1

    @result.deleter
    def result(self):
        self._cache = None    # reset the cache

    @property
    def hit_count(self) -> int:
        return self._hits
```

```python
cr = CachedResult()
cr.result = 42
print(cr.result)      # 42
del cr.result
print(cr.result)      # None
print(cr.hit_count)   # 1  (only one set, del doesn't count)
```

## Enforcing Multiple Invariants with Properties

An **invariant** is a rule that must hold true for an object to be in a consistent state. Properties are the natural enforcement point:

```python
class Rectangle:
    def __init__(self, width: float, height: float):
        # Both assignments trigger the setters
        self.width  = width
        self.height = height

    @property
    def width(self) -> float:
        return self._width

    @width.setter
    def width(self, v: float) -> None:
        if v <= 0:
            raise ValueError(f"Width must be positive, got {v}")
        self._width = float(v)

    @property
    def height(self) -> float:
        return self._height

    @height.setter
    def height(self, v: float) -> None:
        if v <= 0:
            raise ValueError(f"Height must be positive, got {v}")
        self._height = float(v)

    @property
    def area(self) -> float:
        return self._width * self._height

    @property
    def perimeter(self) -> float:
        return 2 * (self._width + self._height)

    @property
    def is_square(self) -> bool:
        return self._width == self._height
```

Invariants: **width and height are always positive floats**. There is no way to construct an invalid `Rectangle`:

```python
r = Rectangle(4, 6)
print(r.area)        # 24.0
print(r.perimeter)   # 20.0
print(r.is_square)   # False

r.width = 0          # ValueError: Width must be positive, got 0
Rectangle(-1, 5)     # ValueError: Width must be positive, got -1
```

## A Richer Example: Password Field

Properties can do more than simple range checks:

```python
import hashlib

class Account:
    MIN_PASSWORD_LENGTH = 8

    def __init__(self, username: str, password: str):
        self._username      = username
        self._password_hash = None
        self.password       = password   # triggers setter and hash

    @property
    def username(self) -> str:
        return self._username            # read-only

    @property
    def password(self):
        raise AttributeError("Password is write-only")  # never expose it

    @password.setter
    def password(self, raw: str) -> None:
        if len(raw) < self.MIN_PASSWORD_LENGTH:
            raise ValueError(
                f"Password must be at least {self.MIN_PASSWORD_LENGTH} characters"
            )
        self._password_hash = hashlib.sha256(raw.encode()).hexdigest()

    def verify_password(self, raw: str) -> bool:
        return self._password_hash == hashlib.sha256(raw.encode()).hexdigest()
```

```python
acc = Account("alice", "s3cur3pass!")
print(acc.username)                    # alice
print(acc.password)                    # AttributeError: Password is write-only
print(acc.verify_password("s3cur3pass!"))  # True
print(acc.verify_password("wrong"))        # False
```

The actual password hash is never exposed. The property getter raises `AttributeError` to make reading the password impossible.

## When to Use Properties vs Regular Methods

| Use `@property` when... | Use a regular method when... |
|-------------------------|------------------------------|
| The value *feels* like a noun | The operation *feels* like a verb |
| No significant side effects | Complex computation or I/O |
| Derived from current state | Multiple return values needed |
| Replacing a plain attribute | Takes arguments beyond `self` |

Good properties: `area`, `is_empty`, `name`, `full_name`, `length`.
Good methods: `save()`, `connect()`, `compute_distance(other)`, `send_email()`.

## `__slots__` for Memory-Sensitive Classes

For classes that create thousands of instances, `__slots__` prevents arbitrary attribute creation and reduces per-instance memory overhead by ~40%:

```python
class Vector2D:
    __slots__ = ("x", "y")   # only these two attributes are allowed

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def magnitude(self) -> float:
        return (self.x**2 + self.y**2) ** 0.5

    def __add__(self, other: "Vector2D") -> "Vector2D":
        return Vector2D(self.x + other.x, self.y + other.y)

v = Vector2D(3, 4)
print(v.magnitude())  # 5.0
v.z = 10              # AttributeError: 'Vector2D' object has no attribute 'z'
```

Note: `__slots__` is incompatible with `@property` if you need to store the backing attribute. If you use properties with `__slots__`, list the private name (e.g., `__slots__ = ("_x", "_y")`) and define the property on top.

## Anti-Pattern: Unnecessary Properties for Simple Getters

Wrapping every attribute in a property that does nothing is over-engineering:

```python
# Anti-pattern: useless property with no logic
class Point:
    def __init__(self, x, y):
        self._x = x

    @property
    def x(self):
        return self._x    # no validation, no computation — pointless indirection
```

Start with a plain public attribute. Only add a property when you need validation, derivation, or read-only access.

## Key Takeaways

- `@property` gives attribute syntax with method power — validation, computation, read-only access.
- Define `@name.setter` and `@name.deleter` as needed; omitting the setter makes the property read-only.
- Invariants belong in setters: raise an exception immediately if a rule is violated.
- Prefer properties over raw `get_*` / `set_*` methods for idiomatic Python code.
- Use `__slots__` in high-count small objects for a significant memory saving.
- Don't add properties "just because" — start with plain attributes and upgrade only when logic is needed.
