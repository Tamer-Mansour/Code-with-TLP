# Exercise: Property-Validated Account

This exercise puts `@property` and encapsulation into practice. You will build a `BankAccount` class that uses Python properties to validate every deposit and withdrawal, preventing the account from ever entering an invalid state.

## What You Will Practice

- Using `_balance` (single-underscore private attribute) to signal internal state
- Defining a `@property` to expose read-only access to balance
- Writing a setter that enforces a class invariant
- Raising `ValueError` inside a setter when validation fails

## Background: @property

The `@property` decorator lets you expose a computed or validated attribute using normal attribute-access syntax:

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if value <= 0:
            raise ValueError("Radius must be positive")
        self._radius = value
```

```python
c = Circle(5)
print(c.radius)   # 5
c.radius = 10     # calls the setter
c.radius = -1     # raises ValueError
```

## Sample Run

The exercise uses uppercase command names and prints formatted messages matching the `deposit`/`withdraw`/`balance` protocol:

Input:
```
5
DEPOSIT 500
DEPOSIT 200
WITHDRAW 100
WITHDRAW 1000
BALANCE
```

Output:
```
Deposited 500. Balance: 700
Withdrew 100. Balance: 600
Insufficient funds. Balance: 600
Balance: 600
```

> Notice the first `DEPOSIT 500` and `DEPOSIT 200` both run before the first `WITHDRAW`, so the balance after both deposits is 700.

## Further Reading

- *Introduction to Python Programming* (OpenStax) — the chapter on OOP discusses `@property` and encapsulation in Python.
  [https://openstax.org/books/introduction-python-programming/pages/1-introduction](https://openstax.org/books/introduction-python-programming/pages/1-introduction)
- *MIT OCW 6.0001* — Lecture 8 covers getters, setters, and properties.
  [https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/](https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/)
