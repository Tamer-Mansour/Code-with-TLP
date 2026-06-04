# SOLID Principles

The **SOLID** principles are five design guidelines for object-oriented software that make systems easier to understand, test, and modify over time. Coined by Robert C. Martin (Uncle Bob) and popularised through his 2003 book *Agile Software Development*, these principles have become a near-universal checklist for evaluating code quality.

**Free resource:** *Software Engineering: A Modern Approach* by Marco Tulio Valente — [softengbook.org](https://softengbook.org/) — covers SOLID in Chapter 5 with worked Java examples that translate directly to Python.

## S — Single Responsibility Principle

> A class should have one, and only one, reason to change.

"Reason to change" means stakeholder concern. If a class handles both business logic *and* email formatting, two different teams own it — and their changes will conflict.

```python
# Violates SRP — User does too many things
class User:
    def save_to_db(self): ...
    def send_welcome_email(self): ...
    def render_profile_html(self): ...

# Follows SRP — each class has one concern
class UserRepository:
    def save(self, user): ...

class WelcomeEmailService:
    def send(self, user): ...

class UserProfileRenderer:
    def render(self, user) -> str: ...
```

A practical test: describe what a class does. If you use the word "and", it likely violates SRP.

## O — Open/Closed Principle

> Software entities should be open for extension but closed for modification.

Adding new behaviour should not require editing existing, tested code. Achieve this through polymorphism and abstraction.

```python
from abc import ABC, abstractmethod

class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, price: float) -> float: ...

class NoDiscount(DiscountStrategy):
    def apply(self, price): return price

class PercentDiscount(DiscountStrategy):
    def __init__(self, pct: float): self.pct = pct
    def apply(self, price): return price * (1 - self.pct / 100)

class BuyOneGetOne(DiscountStrategy):
    def apply(self, price): return price / 2

# Adding a new discount type never modifies existing code
def checkout_total(price: float, strategy: DiscountStrategy) -> float:
    return strategy.apply(price)
```

## L — Liskov Substitution Principle

> Objects of a superclass should be replaceable with objects of a subclass without breaking the program.

A subclass must honour the *contract* of its parent. If `Bird` has a `fly()` method, a `Penguin` subclass must not raise `NotImplementedError` — it violates the caller's expectation.

```python
# Violation: Rectangle and Square
class Rectangle:
    def set_width(self, w): self.width = w
    def set_height(self, h): self.height = h
    def area(self): return self.width * self.height

class Square(Rectangle):
    # Square forces equal sides — breaks the Rectangle contract
    def set_width(self, w):
        self.width = w
        self.height = w   # caller doesn't expect this!

# Fix: model them separately, or use an immutable shape interface
```

The LSP is often violated when inheritance is used for code reuse rather than to model an "is-a" relationship. Prefer composition over inheritance when in doubt.

## I — Interface Segregation Principle

> Clients should not be forced to depend on interfaces they do not use.

One fat interface forces implementors to define methods they don't need. Split it into focused interfaces.

```python
# Too broad — a read-only cache must implement write methods it doesn't need
class Storage(ABC):
    def read(self, key): ...
    def write(self, key, value): ...
    def delete(self, key): ...
    def clear_all(self): ...   # dangerous!

# Segregated interfaces
class Readable(ABC):
    @abstractmethod
    def read(self, key): ...

class Writable(ABC):
    @abstractmethod
    def write(self, key, value): ...

class ReadOnlyCache(Readable):
    def read(self, key): return self._store.get(key)

class FullStore(Readable, Writable):
    def read(self, key): ...
    def write(self, key, value): ...
```

## D — Dependency Inversion Principle

> High-level modules should not depend on low-level modules. Both should depend on abstractions.

Business logic (high-level) should not import database drivers or email libraries (low-level) directly. Inject dependencies through interfaces.

```python
# Violation: high-level OrderService depends on low-level MySQLRepository
class OrderService:
    def __init__(self):
        self.repo = MySQLOrderRepository()  # hard dependency!

# Correct: inject an abstraction
class OrderRepository(ABC):
    @abstractmethod
    def save(self, order): ...
    @abstractmethod
    def find_by_id(self, order_id): ...

class OrderService:
    def __init__(self, repo: OrderRepository):  # depends on abstraction
        self.repo = repo

# Production
service = OrderService(repo=MySQLOrderRepository())

# Test — no database needed
service = OrderService(repo=InMemoryOrderRepository())
```

Dependency injection containers (like Python's `dependency-injector` library or FastAPI's `Depends`) automate this wiring in real applications.

## Putting It All Together

SOLID principles are not rules to follow blindly — they are heuristics for identifying pain. Apply them when:
- A class is hard to test (likely violates SRP or DIP)
- Adding a feature requires editing many existing files (likely violates OCP)
- A subclass silently misbehaves (likely violates LSP)
- Implementing an interface requires writing empty methods (likely violates ISP)

**Further reading:** MIT 6.102 Software Construction readings ([ocw.mit.edu/courses/6-005-software-construction-spring-2016/](https://ocw.mit.edu/courses/6-005-software-construction-spring-2016/)) cover abstract data types and representation invariants — the theoretical foundation underlying SOLID.
