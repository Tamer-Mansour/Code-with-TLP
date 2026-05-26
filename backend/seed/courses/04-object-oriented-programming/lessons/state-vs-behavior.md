# State vs Behavior: The Core of OOP

Object-Oriented Programming organizes code around **objects** — self-contained units that bundle together two things: **state** (the data an object holds) and **behavior** (the actions an object can perform). This bundling is not just a convenience; it is a fundamental design philosophy that keeps code comprehensible as systems grow.

## What is State?

State is the data stored inside an object at any given moment. Think of a bank account: its state is the current balance, the account number, and the owner's name. State changes over time as the object is used. Without OOP, this data would live in unrelated variables scattered across a program — easy to lose track of, easy to corrupt.

```python
# Without OOP — state scattered in disconnected variables
account_number_alice = "ACC-1001"
owner_alice          = "Alice"
balance_alice        = 500.00

account_number_bob   = "ACC-1002"
owner_bob            = "Bob"
balance_bob          = 0.00
```

As soon as you have dozens of accounts this becomes unmaintainable.

## What is Behavior?

Behavior describes what an object *can do* — the operations it exposes to the outside world. For a bank account: deposit, withdraw, and check balance. Behavior that is tied directly to the data it operates on is called a **method** (as opposed to a free-standing function).

```python
# Behavior without coupling to state — hard to use safely
def deposit(balance, amount):
    return balance + amount

def withdraw(balance, amount):
    if amount > balance:
        return balance, False
    return balance - amount, True

balance_alice, ok = withdraw(balance_alice, 300)
```

Nothing stops the caller from mutating `balance_alice` directly or calling `withdraw` with the wrong variable. The state and its logic are not bonded.

## Bringing Them Together: A Class

A **class** is a blueprint that defines what state and behavior its instances will have. An **instance** (or object) is a concrete realization of that blueprint, with its own independent state.

```python
class BankAccount:
    """
    Represents a single bank account.

    State:    owner (str), balance (float)
    Behavior: deposit, withdraw, get_balance
    """

    def __init__(self, owner: str, initial_balance: float = 0.0):
        if initial_balance < 0:
            raise ValueError("Initial balance cannot be negative")
        self.owner   = owner
        self._balance = initial_balance   # _ signals "don't touch directly"

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self._balance += amount

    def withdraw(self, amount: float) -> bool:
        """Returns True on success, False if insufficient funds."""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self._balance:
            return False
        self._balance -= amount
        return True

    def get_balance(self) -> float:
        return self._balance

    def __repr__(self) -> str:
        return f"BankAccount(owner={self.owner!r}, balance={self._balance:.2f})"
```

Creating and using instances:

```python
alice = BankAccount("Alice", 500.00)
bob   = BankAccount("Bob")          # balance starts at 0.0

alice.deposit(200)
bob.deposit(1000)
bob.withdraw(300)

print(alice.get_balance())  # 700.0
print(bob.get_balance())    # 700.0
print(alice)                # BankAccount(owner='Alice', balance=700.00)
print(alice is bob)         # False — independent objects
```

`alice` and `bob` share the same class definition (blueprint) but each has its own state. Changing Alice's balance has zero effect on Bob's.

## UML-Style Sketch

UML (Unified Modeling Language) class diagrams are a standard way to visualize class structure. A simplified text version:

```
+----------------------------------+
|          BankAccount             |
+----------------------------------+
| - owner    : str                 |  <- state (attributes)
| - _balance : float               |
+----------------------------------+
| + __init__(owner, balance=0)     |  <- behavior (methods)
| + deposit(amount) : None         |
| + withdraw(amount) : bool        |
| + get_balance() : float          |
+----------------------------------+
```

Convention: `-` = private/protected, `+` = public. The UML box cleanly separates *what the object knows* from *what it can do*.

## Why Separate State from Behavior?

| Concern | Without OOP | With OOP |
|---------|-------------|----------|
| Locating data | Scattered variables, naming guesses | Grouped in one object |
| Locating logic | Free functions anywhere | Methods on the relevant class |
| Reuse | Copy-paste code | Instantiate another object |
| Change | Touch many unrelated files | Change the class once |
| Safety | Caller can corrupt data | Class guards its own invariants |
| Testing | Hard to isolate | Create one instance per test |

## A Second Example: A Shopping Cart

Consider how naturally state and behavior map to a real-world entity:

```python
class ShoppingCart:
    """
    State:    _items (list of dicts with 'name' and 'price')
    Behavior: add_item, remove_item, total, item_count
    """

    def __init__(self):
        self._items: list = []

    def add_item(self, name: str, price: float) -> None:
        if price < 0:
            raise ValueError("Price cannot be negative")
        self._items.append({"name": name, "price": price})

    def remove_item(self, name: str) -> bool:
        for i, item in enumerate(self._items):
            if item["name"] == name:
                del self._items[i]
                return True
        return False

    def total(self) -> float:
        return sum(item["price"] for item in self._items)

    def item_count(self) -> int:
        return len(self._items)

    def __repr__(self) -> str:
        return f"ShoppingCart({self._items})"
```

```python
cart = ShoppingCart()
cart.add_item("Apple",  0.99)
cart.add_item("Bread",  2.49)
cart.add_item("Milk",   1.75)

print(cart.total())       # 5.23
print(cart.item_count())  # 3

cart.remove_item("Bread")
print(cart.total())       # 3.74
```

## Anti-Pattern: Anemic Domain Model

One classic OOP anti-pattern is the **Anemic Domain Model**: classes that hold state but have no meaningful behavior — just bare getters and setters. This defeats the purpose of OOP:

```python
# Anti-pattern: state without behavior
class Order:
    def __init__(self):
        self.items = []
        self.status = "pending"

# All the logic lives as free functions outside the class
def calculate_total(order):
    return sum(i["price"] for i in order.items)

def ship_order(order):
    order.status = "shipped"
```

The `Order` class is just a bag of data. Logic is scattered in free functions. Compare to the richer design:

```python
# Better: behavior belongs where the state lives
class Order:
    def __init__(self):
        self._items  = []
        self._status = "pending"

    def add_item(self, name: str, price: float) -> None:
        if self._status != "pending":
            raise RuntimeError("Cannot add items to a non-pending order")
        self._items.append({"name": name, "price": price})

    def calculate_total(self) -> float:
        return sum(i["price"] for i in self._items)

    def ship(self) -> None:
        if not self._items:
            raise RuntimeError("Cannot ship an empty order")
        self._status = "shipped"

    @property
    def status(self) -> str:
        return self._status
```

Now the business rules (cannot ship empty, cannot add to shipped) live inside the class that owns the state.

## Key Takeaways

- **State** = instance variables that capture what an object *knows*.
- **Behavior** = methods that describe what an object *does*.
- A **class** is the blueprint; an **instance** is the living object.
- Objects are independent: changing one does not affect another.
- Keep behavior close to the state it operates on — avoid the Anemic Domain Model.
- Guard state through methods and properties to enforce business rules as invariants.
