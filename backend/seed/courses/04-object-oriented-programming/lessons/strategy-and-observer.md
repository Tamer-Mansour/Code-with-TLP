# Design Patterns: Strategy and Observer

This lesson covers two classic **Behavioral** patterns — patterns that define how objects communicate and collaborate at runtime.

## The Strategy Pattern

**Intent:** Define a family of algorithms, encapsulate each one in its own class, and make them interchangeable. Strategy lets the algorithm vary independently from the clients that use it.

**When to use:** When you have several ways to perform an operation (sort, compress, authenticate, price, route) and want to select the algorithm at runtime without modifying the context class.

### Full Example: Sorting

```python
from abc import ABC, abstractmethod

class SortStrategy(ABC):
    @abstractmethod
    def sort(self, data: list) -> list: ...

class BubbleSort(SortStrategy):
    def sort(self, data: list) -> list:
        arr = data[:]
        n   = len(arr)
        for i in range(n):
            for j in range(n - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        return arr

class MergeSort(SortStrategy):
    def sort(self, data: list) -> list:
        if len(data) <= 1:
            return data[:]
        mid   = len(data) // 2
        left  = self.sort(data[:mid])
        right = self.sort(data[mid:])
        return self._merge(left, right)

    def _merge(self, left, right):
        result, i, j = [], 0, 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i]); i += 1
            else:
                result.append(right[j]); j += 1
        return result + left[i:] + right[j:]

class ReverseSort(SortStrategy):
    def sort(self, data: list) -> list:
        return sorted(data, reverse=True)

class Sorter:
    def __init__(self, strategy: SortStrategy = None):
        self._strategy = strategy or MergeSort()

    def set_strategy(self, strategy: SortStrategy) -> None:
        self._strategy = strategy

    def sort(self, data: list) -> list:
        return self._strategy.sort(data)
```

```python
data = [5, 3, 8, 1, 9, 2]
s = Sorter()                    # defaults to MergeSort
print(s.sort(data))             # [1, 2, 3, 5, 8, 9]

s.set_strategy(ReverseSort())
print(s.sort(data))             # [9, 8, 5, 3, 2, 1]

s.set_strategy(BubbleSort())
print(s.sort(data))             # [1, 2, 3, 5, 8, 9]
```

`Sorter` doesn't know *how* sorting works — it delegates to the strategy. Swapping strategies is a one-liner.

### Strategy in Pricing

```python
from abc import ABC, abstractmethod

class PricingStrategy(ABC):
    @abstractmethod
    def price(self, base: float) -> float: ...

class RegularPrice(PricingStrategy):
    def price(self, base: float) -> float: return base

class BlackFridayPrice(PricingStrategy):
    def price(self, base: float) -> float: return base * 0.5   # 50% off

class MemberPrice(PricingStrategy):
    def price(self, base: float) -> float: return base * 0.85  # 15% off

class Product:
    def __init__(self, name: str, base_price: float, strategy: PricingStrategy = None):
        self.name         = name
        self._base_price  = base_price
        self._strategy    = strategy or RegularPrice()

    def set_pricing(self, strategy: PricingStrategy) -> None:
        self._strategy = strategy

    def current_price(self) -> float:
        return self._strategy.price(self._base_price)
```

```python
widget = Product("Widget", 100.0)
print(widget.current_price())           # 100.0

widget.set_pricing(BlackFridayPrice())
print(widget.current_price())           # 50.0

widget.set_pricing(MemberPrice())
print(widget.current_price())           # 85.0
```

### Python's Built-in Strategy: `key=` and `cmp`

Python's `sorted()` and `list.sort()` accept a `key=` function — this is the Strategy pattern built into the language:

```python
words = ["banana", "apple", "fig", "cherry"]
print(sorted(words, key=len))           # ['fig', 'apple', 'banana', 'cherry']
print(sorted(words, key=str.upper))     # alphabetical, case-insensitive
```

The sorting algorithm is fixed (Timsort); only the comparison strategy changes.

## The Observer Pattern

**Intent:** Define a one-to-many dependency so that when one object (the *subject*) changes state, all its dependents (*observers*) are notified and updated automatically.

**When to use:** Event systems, UI listeners, pub/sub notification pipelines, reactive data models.

### Classic Implementation

```python
from abc import ABC, abstractmethod

class Observer(ABC):
    @abstractmethod
    def update(self, event: str, data) -> None: ...

class Subject:
    def __init__(self):
        self._observers: list = []

    def subscribe(self, obs: Observer) -> None:
        if obs not in self._observers:
            self._observers.append(obs)

    def unsubscribe(self, obs: Observer) -> None:
        self._observers.remove(obs)

    def notify(self, event: str, data=None) -> None:
        for obs in list(self._observers):   # copy list; observers may unsubscribe themselves
            obs.update(event, data)


class StockMarket(Subject):
    def __init__(self):
        super().__init__()
        self._prices: dict = {}

    def update_price(self, ticker: str, price: float) -> None:
        old = self._prices.get(ticker)
        self._prices[ticker] = price
        self.notify("price_change", {
            "ticker": ticker,
            "price": price,
            "previous": old,
        })


class AlertObserver(Observer):
    def __init__(self, name: str, threshold: float):
        self.name      = name
        self.threshold = threshold

    def update(self, event: str, data) -> None:
        if event == "price_change" and data["price"] > self.threshold:
            print(f"ALERT [{self.name}]: {data['ticker']} hit "
                  f"{data['price']:.2f} (threshold {self.threshold:.2f})")


class LogObserver(Observer):
    def update(self, event: str, data) -> None:
        print(f"[LOG] {event}: {data}")
```

```python
market = StockMarket()
alert  = AlertObserver("HighAlert", threshold=150.0)
log    = LogObserver()

market.subscribe(alert)
market.subscribe(log)

market.update_price("AAPL", 145.0)
# [LOG] price_change: {'ticker': 'AAPL', 'price': 145.0, 'previous': None}

market.update_price("AAPL", 160.0)
# ALERT [HighAlert]: AAPL hit 160.00 (threshold 150.00)
# [LOG] price_change: {'ticker': 'AAPL', 'price': 160.0, 'previous': 145.0}

market.unsubscribe(log)
market.update_price("AAPL", 170.0)
# ALERT [HighAlert]: AAPL hit 170.00 (threshold 150.00)
# (log is gone — no LOG line)
```

### Observer via Callback Functions

Python lets you skip the abstract `Observer` class and use plain callback functions — a lighter-weight variant:

```python
class EventEmitter:
    """Observer using callable callbacks instead of Observer objects."""

    def __init__(self):
        from collections import defaultdict
        self._handlers: dict = defaultdict(list)

    def on(self, event: str, handler) -> None:
        self._handlers[event].append(handler)

    def off(self, event: str, handler) -> None:
        self._handlers[event].remove(handler)

    def emit(self, event: str, **kwargs) -> None:
        for handler in list(self._handlers[event]):
            handler(**kwargs)
```

```python
emitter = EventEmitter()

def on_login(user, ip):
    print(f"User {user!r} logged in from {ip}")

def on_login_audit(user, ip):
    print(f"[AUDIT] Login: user={user!r}, ip={ip}")

emitter.on("login", on_login)
emitter.on("login", on_login_audit)

emitter.emit("login", user="alice", ip="192.168.1.1")
# User 'alice' logged in from 192.168.1.1
# [AUDIT] Login: user='alice', ip='192.168.1.1'
```

## Pattern Comparison

| Pattern | Category | Varies what? | Key benefit |
|---------|----------|-------------|-------------|
| Strategy | Behavioral | The algorithm used by a context | Swap algorithms at runtime |
| Observer | Behavioral | The set of dependents notified on change | Decouple event sources from handlers |

Both patterns use composition and interfaces to achieve flexibility without subclassing the main class.

## Strategy + Observer Working Together

A realistic use: a monitoring system where the *detection algorithm* (Strategy) and the *notification channels* (Observer) are both configurable:

```python
class AnomalyDetector:
    """Uses a Strategy to detect anomalies, then notifies Observers."""

    def __init__(self, strategy):
        self._strategy = strategy
        self._observers: list = []

    def subscribe(self, obs) -> None:
        self._observers.append(obs)

    def check(self, value: float) -> None:
        if self._strategy.is_anomaly(value):
            for obs in self._observers:
                obs(value)   # simple callable observer
```

```python
class ThresholdStrategy:
    def __init__(self, limit: float):
        self.limit = limit
    def is_anomaly(self, v: float) -> bool:
        return v > self.limit

detector = AnomalyDetector(ThresholdStrategy(100))
detector.subscribe(lambda v: print(f"Email alert: value={v}"))
detector.subscribe(lambda v: print(f"SMS alert: value={v}"))

detector.check(90)    # nothing
detector.check(120)   # Email alert: value=120, SMS alert: value=120
```

## Key Takeaways

- **Strategy**: encapsulate interchangeable algorithms behind a common interface; swap at runtime without touching the context class.
- **Observer**: the subject notifies a list of observers; adding/removing observers requires no change to the subject.
- Both patterns favour composition over inheritance and align with the Open/Closed Principle.
- Python lets you use plain callables as observers — choose ABCs when you need enforced structure, callables when you want flexibility and simplicity.
