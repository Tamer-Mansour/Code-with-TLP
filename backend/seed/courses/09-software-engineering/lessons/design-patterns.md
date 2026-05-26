# Design Patterns in Practice

Design patterns are reusable solutions to commonly occurring design problems. They are not code you paste in — they are templates for structuring code in ways that have proven correct in many different contexts. The Gang of Four (GoF) book (Gamma, Helm, Johnson, Vlissides, 1994) catalogued 23 patterns; this lesson focuses on the ones you will encounter and use most often in everyday software engineering.

## Why Patterns Matter

Patterns give teams a shared vocabulary. "Use the Strategy pattern here" communicates a complete design intent in five words. "Inject a callable that takes a Payment and returns a Result, with concrete implementations for Stripe and PayPal" communicates the same intent in twenty. Patterns also encode trade-offs that the community has learned over decades — using them means inheriting that knowledge.

## Creational Patterns

### Singleton

Ensures a class has only one instance and provides a global access point.

**Real use:** a database connection pool, a configuration registry, a logger.

```python
class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self):
        import os
        self.database_url = os.environ["DATABASE_URL"]
        self.debug = os.environ.get("DEBUG", "false") == "true"

# Both return the same object
cfg1 = Config()
cfg2 = Config()
assert cfg1 is cfg2
```

**Caution:** Singletons make testing hard because they carry state across tests. In Python, dependency injection with a module-level instance is often cleaner.

### Factory Method

Defines an interface for creating objects but lets subclasses decide which class to instantiate.

```python
from abc import ABC, abstractmethod

class Notification(ABC):
    @abstractmethod
    def send(self, to: str, message: str) -> None: ...

class EmailNotification(Notification):
    def send(self, to, message):
        print(f"Email to {to}: {message}")

class SlackNotification(Notification):
    def send(self, to, message):
        print(f"Slack to #{to}: {message}")

def get_notifier(channel: str) -> Notification:
    factories = {
        "email": EmailNotification,
        "slack": SlackNotification,
    }
    if channel not in factories:
        raise ValueError(f"Unknown notification channel: {channel}")
    return factories[channel]()

notifier = get_notifier("email")
notifier.send("alice@example.com", "Your order shipped!")
```

Factory methods isolate object creation logic. Adding a new channel (`sms`) only requires adding a new class and registering it in the dict — no changes to calling code.

## Structural Patterns

### Adapter

Converts the interface of one class into the interface expected by another. Useful when integrating third-party libraries.

```python
# Our application expects this interface
class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, amount_cents: int, token: str) -> dict: ...

# Stripe's actual API
import stripe

class StripeAdapter(PaymentGateway):
    def charge(self, amount_cents: int, token: str) -> dict:
        result = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency="usd",
            payment_method=token,
            confirm=True,
        )
        return {"id": result.id, "status": result.status}

# Our application uses PaymentGateway; the Stripe implementation
# is swappable for a PayPalAdapter or a MockGateway in tests
```

### Decorator

Attaches additional behaviour to an object dynamically, without subclassing.

```python
import functools
import time

def timed(func):
    """Decorator that logs how long a function takes."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.3f}s")
        return result
    return wrapper

def retry(max_attempts=3, exceptions=(Exception,)):
    """Decorator that retries a function on exception."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        raise
                    print(f"Attempt {attempt} failed: {e}. Retrying...")
        return wrapper
    return decorator

@timed
@retry(max_attempts=3, exceptions=(ConnectionError,))
def fetch_user(user_id: int) -> dict:
    # calls external API
    ...
```

Python's `@functools.wraps` is essential in decorators — it preserves the original function's name and docstring, which matters for debugging and introspection.

## Behavioural Patterns

### Strategy

Defines a family of algorithms, encapsulates each one, and makes them interchangeable. The context uses whichever strategy is configured.

```python
from abc import ABC, abstractmethod
from typing import List

class SortStrategy(ABC):
    @abstractmethod
    def sort(self, data: List[int]) -> List[int]: ...

class QuickSort(SortStrategy):
    def sort(self, data):
        if len(data) <= 1:
            return data
        pivot = data[len(data) // 2]
        left = [x for x in data if x < pivot]
        middle = [x for x in data if x == pivot]
        right = [x for x in data if x > pivot]
        return self.sort(left) + middle + self.sort(right)

class MergeSort(SortStrategy):
    def sort(self, data):
        if len(data) <= 1:
            return data
        mid = len(data) // 2
        left = self.sort(data[:mid])
        right = self.sort(data[mid:])
        return self._merge(left, right)

    def _merge(self, left, right):
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i]); i += 1
            else:
                result.append(right[j]); j += 1
        return result + left[i:] + right[j:]

class Sorter:
    def __init__(self, strategy: SortStrategy):
        self.strategy = strategy

    def sort(self, data: List[int]) -> List[int]:
        return self.strategy.sort(data)

sorter = Sorter(QuickSort())
print(sorter.sort([3, 1, 4, 1, 5]))   # [1, 1, 3, 4, 5]
```

The Strategy pattern is why your code should depend on interfaces (abstract classes), not on concrete implementations. Swapping strategies is trivial; swapping hardcoded algorithms requires changing the caller.

### Observer

Defines a one-to-many dependency: when one object (the subject) changes state, all its observers are notified automatically.

```python
from typing import List, Callable

class EventBus:
    """Simple synchronous event bus (Observer pattern)."""

    def __init__(self):
        self._handlers: dict[str, List[Callable]] = {}

    def subscribe(self, event: str, handler: Callable) -> None:
        self._handlers.setdefault(event, []).append(handler)

    def publish(self, event: str, payload: dict) -> None:
        for handler in self._handlers.get(event, []):
            handler(payload)

bus = EventBus()

# Subscribers
bus.subscribe("order.placed", lambda p: print(f"Send confirmation email to {p['email']}"))
bus.subscribe("order.placed", lambda p: print(f"Update inventory for order {p['order_id']}"))
bus.subscribe("order.placed", lambda p: print(f"Notify fulfilment service"))

# Publisher
bus.publish("order.placed", {"order_id": "ORD-99", "email": "alice@example.com"})
# → Send confirmation email to alice@example.com
# → Update inventory for order ORD-99
# → Notify fulfilment service
```

The Observer pattern decouples the order service from email, inventory, and fulfilment — it doesn't need to know they exist. Adding a new subscriber (e.g., analytics) requires zero changes to the publisher.

### Repository

Abstracts the data access layer behind a collection-like interface. Business logic talks to a repository, not to SQL or ORM code directly.

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class User:
    id: int
    email: str
    is_active: bool

class UserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]: ...

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]: ...

    @abstractmethod
    def save(self, user: User) -> None: ...

    @abstractmethod
    def find_active(self) -> List[User]: ...

# Production implementation
class SQLUserRepository(UserRepository):
    def __init__(self, session):
        self.session = session

    def get_by_id(self, user_id):
        return self.session.get(UserORM, user_id)
    # ...

# Test implementation (no database required)
class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self._store: dict[int, User] = {}

    def get_by_id(self, user_id):
        return self._store.get(user_id)

    def get_by_email(self, email):
        return next((u for u in self._store.values() if u.email == email), None)

    def save(self, user):
        self._store[user.id] = user

    def find_active(self):
        return [u for u in self._store.values() if u.is_active]
```

## Patterns to Avoid Overusing

**Every pattern is a trade-off.** They add indirection and abstraction — justified when the complexity is real, harmful when applied prematurely.

- **Over-engineering with patterns** is a common mistake in Java-influenced codebases: an `AbstractSingletonProxyFactoryBean` when a function would suffice
- **YAGNI** (You Ain't Gonna Need It): don't introduce a Strategy pattern because you *might* need multiple strategies someday; introduce it when the second strategy actually arrives
- **Simple code beats clever code**: a `for` loop you can read in 5 seconds beats a pattern that requires knowing the pattern to decode

The right question is not "which pattern should I use?" but "is this code hard to understand, test, or change, and would a pattern fix that?" If the answer is no, keep it simple.
