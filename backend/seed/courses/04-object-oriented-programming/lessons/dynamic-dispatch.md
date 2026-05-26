# Dynamic Dispatch and Polymorphism

**Polymorphism** means "many forms". In OOP, it lets you write code that operates on objects of different types — as long as those objects share a common interface. **Dynamic dispatch** is the runtime mechanism that makes this work: Python waits until the moment of the call to decide which method implementation to run, based on the actual type of the object.

## The Core Idea

```python
class Notification:
    def send(self, message: str) -> None:
        raise NotImplementedError("Subclasses must implement send()")

class EmailNotification(Notification):
    def __init__(self, address: str):
        self.address = address

    def send(self, message: str) -> None:
        print(f"Email to {self.address}: {message}")

class SMSNotification(Notification):
    def __init__(self, phone: str):
        self.phone = phone

    def send(self, message: str) -> None:
        print(f"SMS to {self.phone}: {message}")

class PushNotification(Notification):
    def __init__(self, device_id: str):
        self.device_id = device_id

    def send(self, message: str) -> None:
        print(f"Push to {self.device_id}: {message}")
```

Now a single function handles every notification type:

```python
def notify_all(notifications: list, message: str) -> None:
    for n in notifications:
        n.send(message)    # dynamic dispatch: the right send() is called at runtime
```

```python
channels = [
    EmailNotification("alice@example.com"),
    SMSNotification("+1-555-0100"),
    PushNotification("device-abc-123"),
]

notify_all(channels, "System maintenance at midnight.")
# Email to alice@example.com: System maintenance at midnight.
# SMS to +1-555-0100: System maintenance at midnight.
# Push to device-abc-123: System maintenance at midnight.
```

`notify_all` never mentions `Email`, `SMS`, or `Push` by name. Adding a new `SlackNotification` class requires zero changes to `notify_all`. This is the **Open/Closed Principle** at work.

## Replacing `isinstance` Chains with Polymorphism

A common anti-pattern is to switch on the type of an object with `isinstance`:

```python
# Bad — type-checking chains scale poorly
def describe_payment(payment):
    if isinstance(payment, CreditCardPayment):
        return f"Credit card ending in {payment.last_four}"
    elif isinstance(payment, BankTransferPayment):
        return f"Bank transfer from {payment.iban}"
    elif isinstance(payment, CryptoPayment):
        return f"Crypto wallet {payment.address}"
    # Every new payment type requires editing this function
```

The polymorphic replacement:

```python
class Payment:
    def description(self) -> str:
        raise NotImplementedError

class CreditCardPayment(Payment):
    def __init__(self, last_four: str):
        self.last_four = last_four
    def description(self) -> str:
        return f"Credit card ending in {self.last_four}"

class BankTransferPayment(Payment):
    def __init__(self, iban: str):
        self.iban = iban
    def description(self) -> str:
        return f"Bank transfer from {self.iban}"

class CryptoPayment(Payment):
    def __init__(self, address: str):
        self.address = address
    def description(self) -> str:
        return f"Crypto wallet {self.address}"

# Single, open-for-extension function
def describe_payment(payment: Payment) -> str:
    return payment.description()
```

Adding a new payment type is purely additive — no existing function is modified.

## Duck Typing

Python's polymorphism is especially flexible because it uses **duck typing**: *if it walks like a duck and quacks like a duck, it is a duck*. You don't need a formal inheritance relationship — only the presence of the right method.

```python
class FileLogger:
    def write(self, text: str) -> None:
        print(f"(writing to file) {text}")

class ConsoleLogger:
    def write(self, text: str) -> None:
        print(f"[CONSOLE] {text}")

class NullLogger:
    def write(self, text: str) -> None:
        pass   # silently discards — useful in tests

def process(output, data: list) -> None:
    """Works with any object that has a .write(str) method."""
    for item in data:
        output.write(str(item))
```

```python
process(FileLogger(),    [1, 2, 3])  # (writing to file) 1 ...
process(ConsoleLogger(), ["a", "b"]) # [CONSOLE] a ...
process(NullLogger(),    [99])       # nothing printed
```

`FileLogger`, `ConsoleLogger`, and `NullLogger` share no common base class; `process` works with all of them. In practice, you can document the expected "interface" with a `typing.Protocol` (see the *Contracts, Protocols, and Interface Design* lesson).

## Polymorphism with Dunder Methods

Python's built-in operators are polymorphic. `a + b` calls `a.__add__(b)`. Defining dunder methods on your class makes it participate in standard Python idioms:

```python
class Vector:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector") -> "Vector":
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vector":
        return Vector(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> "Vector":
        return self.__mul__(scalar)   # support 3 * v as well as v * 3

    def __abs__(self) -> float:
        return (self.x**2 + self.y**2) ** 0.5

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __repr__(self) -> str:
        return f"Vector({self.x}, {self.y})"
```

```python
v1 = Vector(1, 2)
v2 = Vector(3, 4)
print(v1 + v2)      # Vector(4, 6)
print(v2 - v1)      # Vector(2, 2)
print(v1 * 3)       # Vector(3, 6)
print(3 * v1)       # Vector(3, 6)  — __rmul__
print(abs(v2))      # 5.0
```

## A Real-World Example: Shape Renderer

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

    @abstractmethod
    def perimeter(self) -> float: ...

    def summary(self) -> str:
        return (f"{type(self).__name__}: "
                f"area={self.area():.2f}, "
                f"perimeter={self.perimeter():.2f}")

class Circle(Shape):
    def __init__(self, r: float):
        self.r = r
    def area(self) -> float:
        import math
        return math.pi * self.r ** 2
    def perimeter(self) -> float:
        import math
        return 2 * math.pi * self.r

class Rectangle(Shape):
    def __init__(self, w: float, h: float):
        self.w, self.h = w, h
    def area(self) -> float:
        return self.w * self.h
    def perimeter(self) -> float:
        return 2 * (self.w + self.h)

class Triangle(Shape):
    def __init__(self, a: float, b: float, c: float):
        self.a, self.b, self.c = a, b, c
    def area(self) -> float:
        s = (self.a + self.b + self.c) / 2
        return (s * (s-self.a) * (s-self.b) * (s-self.c)) ** 0.5
    def perimeter(self) -> float:
        return self.a + self.b + self.c

def print_report(shapes: list) -> None:
    total_area = sum(s.area() for s in shapes)
    for s in shapes:
        print(s.summary())
    print(f"Total area: {total_area:.2f}")
```

```python
shapes = [Circle(5), Rectangle(4, 6), Triangle(3, 4, 5)]
print_report(shapes)
# Circle: area=78.54, perimeter=31.42
# Rectangle: area=24.00, perimeter=20.00
# Triangle: area=6.00, perimeter=12.00
# Total area: 108.54
```

`print_report` is completely type-agnostic — it works on any `Shape` now and in the future.

## Key Takeaways

- Polymorphism lets one piece of code operate on many different types.
- Dynamic dispatch picks the correct method at runtime based on the object's actual type.
- Duck typing means Python checks for the presence of a method, not the class name.
- Replace `isinstance` chains with polymorphic method calls — the code becomes extensible by adding new classes rather than editing existing ones.
- Dunder methods extend polymorphism to Python's built-in operators and functions.
