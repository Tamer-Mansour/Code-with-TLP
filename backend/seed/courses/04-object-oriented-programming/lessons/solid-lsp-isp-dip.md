# SOLID: Liskov Substitution, Interface Segregation, and Dependency Inversion

This lesson covers the remaining three SOLID principles. Together with SRP and OCP, these five principles form a complete toolkit for designing maintainable, testable object-oriented code.

## L — Liskov Substitution Principle (LSP)

> If S is a subtype of T, then objects of type T may be replaced with objects of type S without altering the correctness of the program.

In plain terms: **a subclass must be usable anywhere its parent class is used**. If code works with a `Bird`, it must still work when given a `Parrot` (a subclass of `Bird`) — without the caller knowing or caring.

### LSP Checklist

A subclass violates LSP if it:
- Throws exceptions the parent never throws
- Strengthens preconditions (requires more from callers than the parent does)
- Weakens postconditions (delivers less to callers than the parent promises)
- Overrides a method in a way that fundamentally changes its contract

### Violation — the classic Rectangle/Square trap

```python
class Rectangle:
    def __init__(self, w: float, h: float):
        self.w = w
        self.h = h

    def area(self) -> float:
        return self.w * self.h


class Square(Rectangle):
    def __init__(self, side: float):
        super().__init__(side, side)

    # Attempt to keep w == h at all times:
    @Rectangle.w.setter   # doesn't actually work cleanly — shown as concept
    def w(self, v):
        self._w = v
        self._h = v    # also changes height!
```

Code that assumes "setting width doesn't change height" will break when handed a `Square`:

```python
def stretch_horizontally(rect: Rectangle) -> None:
    rect.w = 10
    # Expects: area = 10 * rect.h
    # With Square: rect.h was also set to 10 — contract violated!
    print(rect.area())

r = Rectangle(4, 5)
stretch_horizontally(r)    # 50 — correct

s = Square(4)
stretch_horizontally(s)    # 100 — violates the caller's expectation
```

### Fix: don't force the inheritance

A Square is *geometrically* a rectangle, but it is **not** a `Rectangle` in the substitutable sense because it has different invariants (`w == h` always).

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

class Rectangle(Shape):
    def __init__(self, w: float, h: float):
        self.w, self.h = w, h
    def area(self) -> float:
        return self.w * self.h

class Square(Shape):            # Square IS-A Shape, NOT a Rectangle
    def __init__(self, side: float):
        self.side = side
    def area(self) -> float:
        return self.side ** 2
```

Both satisfy `Shape.area()` correctly; neither breaks the other's contract.

### Another LSP Violation: Strengthening a Precondition

```python
class FileReader:
    def read(self, path: str) -> str:
        # Accepts any path
        with open(path) as f:
            return f.read()

class SecureFileReader(FileReader):
    ALLOWED_DIR = "/safe/"

    def read(self, path: str) -> str:
        # Violation: rejects paths the parent accepts — caller breaks unexpectedly
        if not path.startswith(self.ALLOWED_DIR):
            raise PermissionError(f"Path not allowed: {path!r}")
        return super().read(path)
```

The fix: either document that `SecureFileReader` is not a substitute for `FileReader`, or use a separate interface for "safe reading".

## I — Interface Segregation Principle (ISP)

> Clients should not be forced to depend on methods they do not use.

### Violation

```python
from abc import ABC, abstractmethod

class Machine(ABC):
    @abstractmethod
    def print_doc(self, doc): ...
    @abstractmethod
    def scan_doc(self, doc): ...
    @abstractmethod
    def fax_doc(self, doc): ...

class OldPrinter(Machine):
    def print_doc(self, doc): print(f"Printing: {doc}")
    def scan_doc(self, doc):  raise NotImplementedError("No scanner")  # forced stub
    def fax_doc(self, doc):   raise NotImplementedError("No fax")       # forced stub
```

`OldPrinter` is forced to implement methods it physically cannot support. If a caller invokes `scan_doc` on it — perhaps not knowing it's an old printer — the error surfaces at runtime with a confusing message.

### Fixed

```python
class Printer(ABC):
    @abstractmethod
    def print_doc(self, doc): ...

class Scanner(ABC):
    @abstractmethod
    def scan_doc(self, doc): ...

class Fax(ABC):
    @abstractmethod
    def fax_doc(self, doc): ...

class OldPrinter(Printer):              # only what it can do
    def print_doc(self, doc): print(f"Printing: {doc}")

class MultiFunctionPrinter(Printer, Scanner, Fax):
    def print_doc(self, doc): print(f"Printing: {doc}")
    def scan_doc(self, doc):  print(f"Scanning: {doc}")
    def fax_doc(self, doc):   print(f"Faxing: {doc}")
```

A function that needs only printing accepts `Printer`. One that needs all three accepts `MultiFunctionPrinter`. They are independent contracts.

### ISP in Practice: Splitting a "God Service"

```python
# Before — fat interface that every microservice must implement
class DataService(ABC):
    @abstractmethod
    def get_user(self, uid): ...
    @abstractmethod
    def get_product(self, pid): ...
    @abstractmethod
    def get_order(self, oid): ...
    @abstractmethod
    def save_log(self, entry): ...
    @abstractmethod
    def send_notification(self, msg): ...

# After — each service only implements what it actually provides
class UserService(ABC):
    @abstractmethod
    def get_user(self, uid): ...

class ProductService(ABC):
    @abstractmethod
    def get_product(self, pid): ...

class OrderService(ABC):
    @abstractmethod
    def get_order(self, oid): ...

class LoggingService(ABC):
    @abstractmethod
    def save_log(self, entry): ...

class NotificationService(ABC):
    @abstractmethod
    def send_notification(self, msg): ...
```

A new team building the notification service no longer has to implement `get_user` or `get_product`.

## D — Dependency Inversion Principle (DIP)

> High-level modules should not depend on low-level modules. Both should depend on abstractions. Abstractions should not depend on details. Details should depend on abstractions.

In practice: inject dependencies (database, emailer, logger) as abstractions so that high-level logic is insulated from low-level implementation details.

### Violation

```python
class MySQLDatabase:
    def query(self, sql: str) -> list:
        return []   # hard-coded MySQL call

class ReportService:
    def __init__(self):
        self.db = MySQLDatabase()    # hard-wired — cannot test without MySQL

    def generate(self) -> list:
        return self.db.query("SELECT * FROM reports")
```

`ReportService` is permanently coupled to MySQL. Running a unit test requires a real MySQL server.

### Fixed

```python
from abc import ABC, abstractmethod
from typing import List

class Database(ABC):               # the abstraction
    @abstractmethod
    def query(self, sql: str) -> List[dict]: ...

class MySQLDatabase(Database):     # low-level detail
    def query(self, sql: str) -> List[dict]:
        print(f"[MySQL] {sql}")
        return []   # real implementation would use a DB driver

class PostgresDatabase(Database):  # alternative low-level detail
    def query(self, sql: str) -> List[dict]:
        print(f"[Postgres] {sql}")
        return []

class InMemoryDatabase(Database):  # fast fake for tests
    def __init__(self, data: List[dict]):
        self._data = data
    def query(self, sql: str) -> List[dict]:
        return self._data

class ReportService:               # high-level — depends only on the abstraction
    def __init__(self, db: Database):
        self._db = db

    def generate(self) -> List[dict]:
        return self._db.query("SELECT * FROM reports")
```

```python
# Production
svc = ReportService(MySQLDatabase())

# Tests — no real database needed
test_svc = ReportService(InMemoryDatabase([
    {"id": 1, "title": "Q1", "total": 50000},
    {"id": 2, "title": "Q2", "total": 62000},
]))
print(test_svc.generate())
# [{'id': 1, 'title': 'Q1', 'total': 50000},
#  {'id': 2, 'title': 'Q2', 'total': 62000}]
```

`ReportService` is fully testable without a database. Switching from MySQL to Postgres requires only changing the injected object.

### Dependency Injection Container Pattern

In larger applications, a simple registry wires up dependencies automatically:

```python
class Container:
    """Minimal dependency injection container."""

    def __init__(self):
        self._bindings: dict = {}

    def bind(self, abstract, concrete) -> None:
        self._bindings[abstract] = concrete

    def make(self, abstract):
        if abstract not in self._bindings:
            raise KeyError(f"No binding for {abstract}")
        factory = self._bindings[abstract]
        return factory()

# Wiring
container = Container()
container.bind(Database, lambda: InMemoryDatabase([{"id": 1}]))
container.bind(ReportService, lambda: ReportService(container.make(Database)))

service = container.make(ReportService)
print(service.generate())   # [{'id': 1}]
```

## SOLID Summary

| Letter | Principle | One-line rule | Key benefit |
|--------|-----------|--------------|-------------|
| S | Single Responsibility | One class, one job | Easier to change, understand |
| O | Open/Closed | Extend by adding, not editing | Safe to add features |
| L | Liskov Substitution | Subclasses are drop-in replacements | Trust inherited contracts |
| I | Interface Segregation | Small, focused interfaces | Only implement what you use |
| D | Dependency Inversion | Depend on abstractions, not concretions | Testable, swappable components |

Following SOLID produces code that is easier to test (each class has one job and accepts injected dependencies), extend (add without modifying), and maintain (changes are localised and predictable).

## Key Takeaways

- **LSP**: a subclass must not throw new exceptions, must not strengthen preconditions, and must not weaken postconditions relative to its parent.
- **ISP**: fat interfaces force unnecessary stubs; split them by capability.
- **DIP**: inject dependencies as abstract interfaces; the high-level policy should never name a concrete class directly.
