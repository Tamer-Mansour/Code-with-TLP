# Constructors and Instances

A **constructor** is the special method that runs when a new object is born. In Python, that method is `__init__`. Understanding what happens during object construction helps you write safer, more predictable classes.

## Object Creation: What Really Happens

When you write `obj = MyClass(args)`, Python performs two steps:

1. **`__new__`** allocates a fresh memory slot for the object and returns the bare, uninitialised instance (you rarely override this).
2. **`__init__`** receives that new object (as `self`) and initialises its attributes.

```
MyClass(args)
    |
    v
MyClass.__new__(MyClass)   -> bare object in memory
    |
    v
MyClass.__init__(self, args) -> attributes filled in -> ready to use
    |
    v
 reference returned to caller
```

In practice you only ever override `__init__`:

```python
class Counter:
    def __init__(self, start: int = 0, step: int = 1):
        if step == 0:
            raise ValueError("step cannot be zero")
        self.count    = start
        self.step     = step
        self._history = []       # always define all attributes here

    def increment(self) -> None:
        self.count += self.step
        self._history.append(self.count)

    def reset(self) -> None:
        self.count = 0
        self._history.clear()

    def history(self) -> list:
        return list(self._history)   # return a copy; never expose internals directly
```

```python
c1 = Counter()           # start=0, step=1
c2 = Counter(10, 2)      # start=10, step=2
c3 = Counter(step=5)     # start=0, step=5

c1.increment(); c1.increment()
c2.increment()
print(c1.count)          # 2
print(c2.count)          # 12
print(c1.history())      # [1, 2]
```

Each call to `Counter()` creates an entirely independent object with its own `count`, `step`, and `_history`.

## Overloading Constructors with Default Arguments

Python has no true method overloading, but default arguments give you the same flexibility:

```python
class Rectangle:
    def __init__(self, width: float, height: float = None):
        if width <= 0:
            raise ValueError("Width must be positive")
        self.width  = width
        self.height = height if height is not None else width  # square if omitted

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)

    def is_square(self) -> bool:
        return self.width == self.height

r1 = Rectangle(4, 6)    # 4 × 6 rectangle
r2 = Rectangle(5)       # 5 × 5 square
print(r1.area())        # 24.0
print(r2.is_square())   # True
```

## Factory Class Methods as Named Constructors

When a class has several distinct creation modes, class methods named after their intent read far better than juggling default arguments:

```python
class Color:
    def __init__(self, r: int, g: int, b: int):
        for v, name in ((r, "r"), (g, "g"), (b, "b")):
            if not 0 <= v <= 255:
                raise ValueError(f"Channel {name} must be 0-255, got {v}")
        self.r, self.g, self.b = r, g, b

    @classmethod
    def from_hex(cls, hex_str: str) -> "Color":
        """Create a Color from a hex string like '#0080FF' or '0080FF'."""
        hex_str = hex_str.lstrip("#")
        if len(hex_str) != 6:
            raise ValueError(f"Expected 6 hex digits, got {hex_str!r}")
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
        return cls(r, g, b)

    @classmethod
    def from_hsv(cls, h: float, s: float, v: float) -> "Color":
        """Create from HSV (hue 0-360, saturation 0-1, value 0-1)."""
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(h / 360, s, v)
        return cls(int(r * 255), int(g * 255), int(b * 255))

    @classmethod
    def white(cls)  -> "Color": return cls(255, 255, 255)
    @classmethod
    def black(cls)  -> "Color": return cls(0, 0, 0)
    @classmethod
    def red(cls)    -> "Color": return cls(255, 0, 0)

    def to_hex(self) -> str:
        return f"#{self.r:02X}{self.g:02X}{self.b:02X}"

    def __repr__(self) -> str:
        return f"Color(r={self.r}, g={self.g}, b={self.b})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Color):
            return NotImplemented
        return (self.r, self.g, self.b) == (other.r, other.g, other.b)
```

```python
c1 = Color(0, 128, 255)
c2 = Color.from_hex("#0080FF")
c3 = Color.white()

print(c1)            # Color(r=0, g=128, b=255)
print(c1 == c2)      # True
print(c3.to_hex())   # #FFFFFF
```

The named constructors (`from_hex`, `from_hsv`, `white`) communicate their intent clearly; `Color(0, 128, 255)` tells you nothing about the colour model being used.

## Instance Identity and Equality

Two different instances are not the same object, even if they hold identical data:

```python
a = Counter(10)
b = Counter(10)

print(a is b)   # False — different objects in memory
print(a == b)   # False — by default, == uses identity (same as `is`)
```

To give a class **value-based equality**, override `__eq__`:

```python
class Counter:
    def __init__(self, start: int = 0, step: int = 1):
        self.count = start
        self.step  = step
        self._history = []

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Counter):
            return NotImplemented
        return self.count == other.count and self.step == other.step

    def __hash__(self) -> int:
        # Must define __hash__ if you define __eq__
        # Use a tuple of the fields that determine equality
        return hash((self.count, self.step))
```

**Important:** whenever you override `__eq__`, Python sets `__hash__` to `None` (making objects un-hashable) unless you explicitly define it. If instances should be usable as dict keys or set members, define `__hash__` as well.

## The `__post_init__` Pattern

For dataclasses (Python 3.7+), initialization hooks are common via `__post_init__`:

```python
from dataclasses import dataclass, field

@dataclass
class Vector:
    x: float
    y: float
    _magnitude: float = field(init=False, repr=False)

    def __post_init__(self):
        # Runs after __init__; safe to use self here
        self._magnitude = (self.x**2 + self.y**2) ** 0.5

    @property
    def magnitude(self) -> float:
        return self._magnitude

v = Vector(3.0, 4.0)
print(v.magnitude)   # 5.0
```

`dataclass` auto-generates `__init__`, `__repr__`, and `__eq__` from the field annotations.

## Object Lifecycle Diagram

```
MyClass(args)
     |
     v
__new__()  -------> allocates memory -> raw object
     |
     v
__init__(self, args) -> assigns attributes -> ready object
     |
     v
   [in use — methods called, state changes]
     |
     v
reference count drops to 0 -> __del__() -> garbage collected
```

`__del__` is rarely needed; Python's reference-counting garbage collector handles cleanup automatically in most cases.

## Best Practices for `__init__`

1. **Define every attribute** — even those starting as `None`. Readers and tools (IDEs, type checkers) need to know the object's shape.
2. **Validate early** — raise `ValueError` or `TypeError` with a clear message before storing bad data.
3. **Keep it short** — `__init__` should initialize, not perform heavy computation or I/O.
4. **Use named constructors** (`@classmethod`) when there are multiple distinct creation modes.

```python
class Temperature:
    ABSOLUTE_ZERO_C = -273.15

    def __init__(self, celsius: float):
        if celsius < self.ABSOLUTE_ZERO_C:
            raise ValueError(
                f"Temperature {celsius}°C is below absolute zero ({self.ABSOLUTE_ZERO_C}°C)"
            )
        self._celsius = float(celsius)

    @classmethod
    def from_fahrenheit(cls, f: float) -> "Temperature":
        return cls((f - 32) * 5 / 9)

    @classmethod
    def from_kelvin(cls, k: float) -> "Temperature":
        return cls(k - 273.15)

    @property
    def celsius(self) -> float:
        return self._celsius

    @property
    def fahrenheit(self) -> float:
        return self._celsius * 9 / 5 + 32

    @property
    def kelvin(self) -> float:
        return self._celsius + 273.15

    def __repr__(self) -> str:
        return f"Temperature({self._celsius}°C)"
```

```python
t1 = Temperature(100)
t2 = Temperature.from_fahrenheit(212)
t3 = Temperature.from_kelvin(373.15)

print(t1.fahrenheit)  # 212.0
print(t2.celsius)     # 100.0
print(t1 == t2)       # False (no custom __eq__ — uses identity)
```

## Summary

- `__init__` initialises every instance attribute — define them all here, validate early.
- Use default parameters for optional fields; use `@classmethod` for distinct construction paths.
- Two instances are independent: changing one never affects the other.
- Override `__eq__` for value-based equality and remember to also define `__hash__`.
- `dataclass` auto-generates boilerplate for simple value objects.
