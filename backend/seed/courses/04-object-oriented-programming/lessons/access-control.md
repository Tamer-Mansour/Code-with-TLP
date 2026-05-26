# Access Control and Encapsulation

**Encapsulation** means bundling state and behavior together *and* controlling who can access the internals. The goal is to hide implementation details so that the outside world only sees a clean, stable interface. Changes to internals should be invisible to callers — that is the whole point.

## Why Hide Internals?

Imagine a `Temperature` class that stores degrees in Celsius internally. If outside code reads `obj.celsius` directly and you later decide to store Kelvin instead, every caller breaks. Encapsulation protects callers from such internal changes.

A concrete demonstration of the problem:

```python
# No encapsulation — internals exposed
class BrokenStack:
    def __init__(self):
        self.items = []   # public — caller can violate any invariant

stack = BrokenStack()
stack.items = None           # oops — now all methods crash
stack.items.append(1)
stack.items.append(2)
stack.items = stack.items[::-1]   # caller decides to reverse internals
```

The caller can reach in and break the object. Encapsulation prevents this.

## Python's Naming Conventions

Python has no hard access modifiers like `private` in Java. Instead it uses naming conventions that communicate intent:

| Convention | Meaning | Example |
|------------|---------|---------|
| `name` | Public — free to use from anywhere | `self.balance` |
| `_name` | Protected — "internal use" hint; subclasses may use it | `self._cache` |
| `__name` | Private — name-mangled by Python to deter external access | `self.__secret` |

```python
class Vault:
    def __init__(self, code: str):
        self.label   = "Main Vault"  # public
        self._log    = []            # protected — part of internal implementation
        self.__code  = code          # private — Python renames to _Vault__code

    def open(self, attempt: str) -> bool:
        self._log.append(attempt)
        return attempt == self.__code

    def audit_log(self) -> list:
        return list(self._log)       # expose a copy through a controlled method
```

```python
v = Vault("XK-47")
print(v.label)         # "Main Vault"  — OK, public
print(v._log)          # []            — works but signals "you shouldn't"
# print(v.__code)      # AttributeError — Python renamed it
print(v._Vault__code)  # "XK-47"  — mangled name bypasses it; avoid in real code
```

Name-mangling is not true privacy — it is a speed-bump that prevents accidental access, especially in inheritance hierarchies where a subclass might inadvertently shadow a parent's attribute.

## Getters and Setters (the Java Way)

A common encapsulation pattern is to make attributes private and expose them through methods:

```python
class Temperature:
    def __init__(self, celsius: float):
        self._validate(celsius)
        self._celsius = celsius

    @staticmethod
    def _validate(value: float) -> None:
        if value < -273.15:
            raise ValueError(f"Temperature below absolute zero: {value}")

    def get_celsius(self) -> float:
        return self._celsius

    def set_celsius(self, value: float) -> None:
        self._validate(value)
        self._celsius = value

    def get_fahrenheit(self) -> float:
        return self._celsius * 9 / 5 + 32
```

This works but is verbose and un-Pythonic. The Pythonic alternative is `@property`.

## The Pythonic Way: Properties

Python's `@property` decorator gives you the *syntax* of direct attribute access while running method code behind the scenes:

```python
class Temperature:
    def __init__(self, celsius: float):
        self.celsius = celsius     # triggers the setter — validates immediately

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < -273.15:
            raise ValueError(f"{value}°C is below absolute zero")
        self._celsius = value

    @property
    def fahrenheit(self) -> float:
        """Read-only derived value — no setter defined."""
        return self._celsius * 9 / 5 + 32

    @property
    def kelvin(self) -> float:
        return self._celsius + 273.15
```

```python
t = Temperature(100)
print(t.celsius)      # 100   — looks like attribute access, runs getter
print(t.fahrenheit)   # 212.0
print(t.kelvin)       # 373.15

t.celsius = 0         # triggers setter, validates
print(t.fahrenheit)   # 32.0

t.celsius = -300      # raises ValueError: -300°C is below absolute zero
```

The caller never knows — or needs to know — that validation is happening.

## Upgrading a Plain Attribute to a Property Without Breaking Callers

One major benefit: you can start with a plain public attribute and switch to a property later without changing any calling code:

```python
# Version 1 — simple, no validation
class Circle:
    def __init__(self, radius: float):
        self.radius = radius  # plain attribute

# Calling code:  c.radius = 5   works fine

# Version 2 — add validation; calling code unchanged
class Circle:
    def __init__(self, radius: float):
        self.radius = radius  # still works because setter is called

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, v: float) -> None:
        if v <= 0:
            raise ValueError("Radius must be positive")
        self._radius = v
```

Every existing line that writes `c.radius = ...` or reads `c.radius` keeps working — a seamless upgrade.

## Invariants

An **invariant** is a condition that must always be true for an object to be in a valid state. Encapsulation enforces invariants by routing all writes through setters or methods:

```python
class BankAccount:
    def __init__(self, owner: str, balance: float = 0.0):
        if balance < 0:
            raise ValueError("Opening balance cannot be negative")
        self._owner   = owner
        self._balance = balance
        # Invariant: _balance >= 0 at all times

    @property
    def owner(self) -> str:
        return self._owner      # read-only

    @property
    def balance(self) -> float:
        return self._balance    # read-only via property

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self._balance += amount
        # Invariant maintained: balance only increases here

    def withdraw(self, amount: float) -> bool:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self._balance:
            return False
        self._balance -= amount
        # Invariant maintained: only decreases when enough funds exist
        return True
```

Outside code can **never** accidentally push the balance negative:

```python
account = BankAccount("Alice", 100)
account.withdraw(200)     # returns False, balance stays 100
# account._balance = -50  # works in Python but clearly a violation — "you shouldn't"
```

## Refactoring: Before and After Encapsulation

**Before** — raw data, no control:

```python
class User:
    def __init__(self, name, email, age):
        self.name  = name
        self.email = email
        self.age   = age   # nothing stops age = -5 or age = "hello"
```

**After** — encapsulated with validation:

```python
import re

class User:
    _EMAIL_RE = re.compile(r"^[^@]+@[^@]+\.[^@]+$")

    def __init__(self, name: str, email: str, age: int):
        self.name  = name    # simple string, no constraint
        self.email = email   # triggers setter
        self.age   = age     # triggers setter

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, v: str) -> None:
        if not self._EMAIL_RE.match(v):
            raise ValueError(f"Invalid email: {v!r}")
        self._email = v

    @property
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, v: int) -> None:
        if not isinstance(v, int) or v < 0 or v > 150:
            raise ValueError(f"Age must be an integer 0-150, got {v!r}")
        self._age = v
```

```python
u = User("Alice", "alice@example.com", 30)
u.age = 31          # OK
u.age = -5          # ValueError: Age must be an integer 0-150, got -5
u.email = "bad"     # ValueError: Invalid email: 'bad'
```

## Key Takeaways

- Use `_name` for "please don't touch from outside" and `__name` for name-mangled attributes that resist accidental shadowing in subclasses.
- Prefer `@property` over raw `get_*` / `set_*` methods — it is idiomatic Python and lets you start simple and add logic later without breaking callers.
- Encapsulation enforces **invariants**: the object's state remains consistent at all times.
- A clean public interface hides implementation details and makes future refactoring safe and invisible to callers.
