# Abstract Methods and Enforced Interfaces

An **abstract method** is a method declared in a base class with no implementation there. Subclasses are *required* to provide the implementation. This creates a **contract**: any class that inherits from the abstract base must fulfil it by implementing every abstract method — Python raises a `TypeError` at instantiation time if it doesn't.

## Python's `abc` Module

The `abc` (Abstract Base Classes) module provides the tools:

```python
from abc import ABC, abstractmethod

class Serializer(ABC):
    """Contract: any Serializer must implement encode() and decode()."""

    @abstractmethod
    def encode(self, data: object) -> str:
        """Convert data to a string representation."""
        ...

    @abstractmethod
    def decode(self, text: str) -> object:
        """Convert a string back to data."""
        ...

    def round_trip(self, data: object) -> object:
        """Concrete method shared by ALL subclasses — no override needed."""
        return self.decode(self.encode(data))
```

```python
s = Serializer()
# TypeError: Can't instantiate abstract class Serializer
#            with abstract methods decode, encode
```

The protection happens automatically — no extra code needed.

## Implementing the Contract

```python
import json

class JsonSerializer(Serializer):
    def encode(self, data: object) -> str:
        return json.dumps(data)

    def decode(self, text: str) -> object:
        return json.loads(text)


class CsvRowSerializer(Serializer):
    """Serializes a flat list as comma-separated values."""

    def encode(self, data: list) -> str:
        return ",".join(str(x) for x in data)

    def decode(self, text: str) -> list:
        return text.split(",")
```

```python
js  = JsonSerializer()
csv = CsvRowSerializer()

result = js.round_trip({"key": 42, "flag": True})
print(result)              # {'key': 42, 'flag': True}

encoded = csv.encode([1, 2, 3])
print(encoded)             # 1,2,3
print(csv.decode(encoded)) # ['1', '2', '3']
```

`round_trip` is a **concrete method** on the abstract class. It is inherited by every subclass and works correctly because it only calls the abstract `encode`/`decode` methods that every concrete subclass must provide.

## Partial Implementation and the Template Method Pattern

Abstract classes can mix abstract and concrete methods. The **Template Method** pattern defines a fixed algorithm skeleton in the base class and lets subclasses fill in specific steps:

```python
from abc import ABC, abstractmethod

class DataPipeline(ABC):
    def run(self) -> None:
        """Template method — fixed sequence, cannot be overridden here."""
        print(f"[{type(self).__name__}] Starting pipeline...")
        raw   = self.extract()
        clean = self.transform(raw)
        self.load(clean)
        print(f"[{type(self).__name__}] Done.")

    @abstractmethod
    def extract(self) -> list:
        """Pull data from a source."""
        ...

    @abstractmethod
    def transform(self, data: list) -> list:
        """Clean and reshape the data."""
        ...

    @abstractmethod
    def load(self, data: list) -> None:
        """Write data to a destination."""
        ...


class CsvPipeline(DataPipeline):
    def extract(self) -> list:
        return ["1,Alice,30", "2,Bob,25"]

    def transform(self, data: list) -> list:
        return [row.split(",") for row in data]

    def load(self, data: list) -> None:
        for row in data:
            print(f"  id={row[0]}, name={row[1]}, age={row[2]}")


class JsonPipeline(DataPipeline):
    def extract(self) -> list:
        return ['{"id":1,"name":"Carol"}', '{"id":2,"name":"Dave"}']

    def transform(self, data: list) -> list:
        import json
        return [json.loads(row) for row in data]

    def load(self, data: list) -> None:
        for record in data:
            print(f"  -> {record}")
```

```python
CsvPipeline().run()
# [CsvPipeline] Starting pipeline...
#   id=1, name=Alice, age=30
#   id=2, name=Bob, age=25
# [CsvPipeline] Done.

JsonPipeline().run()
# [JsonPipeline] Starting pipeline...
#   -> {'id': 1, 'name': 'Carol'}
#   -> {'id': 2, 'name': 'Dave'}
# [JsonPipeline] Done.
```

The `run()` method is written once. Only the three abstract steps differ between pipeline types.

## Abstract Properties

Properties can also be abstract, forcing subclasses to provide a computed attribute:

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @property
    @abstractmethod
    def area(self) -> float:
        """Surface area of the shape."""
        ...

    @property
    @abstractmethod
    def perimeter(self) -> float:
        ...

    def describe(self) -> str:
        return (f"{type(self).__name__}: "
                f"area={self.area:.3f}, perimeter={self.perimeter:.3f}")


class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    @property
    def area(self) -> float:
        import math
        return math.pi * self.radius ** 2

    @property
    def perimeter(self) -> float:
        import math
        return 2 * math.pi * self.radius


class Square(Shape):
    def __init__(self, side: float):
        self.side = side

    @property
    def area(self) -> float:
        return self.side ** 2

    @property
    def perimeter(self) -> float:
        return 4 * self.side
```

```python
shapes = [Circle(5), Square(4)]
for s in shapes:
    print(s.describe())
# Circle: area=78.540, perimeter=31.416
# Square: area=16.000, perimeter=16.000
```

## Abstract Class Methods and Static Methods

Both class methods and static methods can be made abstract:

```python
from abc import ABC, abstractmethod

class Plugin(ABC):
    @classmethod
    @abstractmethod
    def plugin_name(cls) -> str:
        """Every plugin must declare its human-readable name."""
        ...

    @abstractmethod
    def execute(self, context: dict) -> dict:
        ...


class UpperCasePlugin(Plugin):
    @classmethod
    def plugin_name(cls) -> str:
        return "UpperCase Transformer"

    def execute(self, context: dict) -> dict:
        return {k: v.upper() if isinstance(v, str) else v
                for k, v in context.items()}
```

```python
p = UpperCasePlugin()
print(UpperCasePlugin.plugin_name())  # UpperCase Transformer
print(p.execute({"name": "alice", "score": 95}))
# {'name': 'ALICE', 'score': 95}
```

## The UML-Style View

```
+--------------------------------+
|  <<abstract>>  Serializer      |
+--------------------------------+
|  + encode(data) : str   {abs}  |
|  + decode(text) : obj   {abs}  |
|  + round_trip(data) : obj      |  <- concrete, shared
+--------------------------------+
         ^               ^
         |               |
+----------------+ +-------------------+
| JsonSerializer | | CsvRowSerializer  |
+----------------+ +-------------------+
| encode()       | | encode()          |
| decode()       | | decode()          |
+----------------+ +-------------------+
```

`{abs}` marks abstract methods. Subclasses inherit `round_trip` for free.

## When to Use Abstract Base Classes

- When multiple classes share a common interface but have entirely different implementations.
- When you want Python to catch missing implementations at class-definition time, not at runtime when the method is called.
- When writing a framework or library where others will extend your base class.
- When documenting a contract for future implementers.

## Key Takeaways

- Inherit from `ABC` and decorate methods with `@abstractmethod` to define a contract.
- Any class with un-implemented abstract methods cannot be instantiated.
- Concrete methods on an abstract class are inherited and reused by all subclasses.
- The Template Method pattern uses a concrete `run()` (or `process()`) method that calls abstract steps — a powerful pattern for fixed-sequence workflows with variable steps.
- Abstract properties force subclasses to provide computed attributes.
