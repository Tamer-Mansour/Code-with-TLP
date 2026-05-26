# Subclassing and the `super()` Function

**Inheritance** lets you create a new class (the *subclass*) that automatically acquires all the attributes and methods of an existing class (the *superclass* or *base class*). You then add or override what is specific to the subclass. Done well, inheritance reduces duplication and creates a coherent hierarchy of types.

## Basic Subclassing

```python
class Animal:
    def __init__(self, name: str, sound: str):
        self.name  = name
        self.sound = sound

    def speak(self) -> str:
        return f"{self.name} says {self.sound}"

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.name!r})"


class Dog(Animal):
    def fetch(self, item: str) -> str:
        return f"{self.name} fetches the {item}!"


class Cat(Animal):
    def purr(self) -> str:
        return f"{self.name} purrs..."
```

```python
d = Dog("Rex", "woof")
print(d.speak())          # Rex says woof   — inherited from Animal
print(d.fetch("ball"))    # Rex fetches the ball!
print(isinstance(d, Animal))  # True — Dog IS-A Animal
```

## Using `super()`

When a subclass defines `__init__`, it must call the parent's `__init__` to set up inherited attributes. `super()` provides a proxy to the parent class that correctly follows the MRO:

```python
class Vehicle:
    def __init__(self, make: str, model: str, year: int):
        self.make  = make
        self.model = model
        self.year  = year

    def info(self) -> str:
        return f"{self.year} {self.make} {self.model}"


class ElectricVehicle(Vehicle):
    def __init__(self, make: str, model: str, year: int, range_km: int):
        super().__init__(make, model, year)   # initialize the Vehicle portion
        self.range_km = range_km              # EV-specific attribute

    def info(self) -> str:
        base = super().info()
        return f"{base} (EV, {self.range_km} km range)"

    def charge_time(self, percent: int = 100) -> float:
        """Estimate hours to charge from 0 to `percent` at 50 kW."""
        kWh_needed = (percent / 100) * (self.range_km * 0.2)  # rough: 0.2 kWh/km
        return kWh_needed / 50
```

```python
ev = ElectricVehicle("Tesla", "Model 3", 2024, 570)
print(ev.info())           # 2024 Tesla Model 3 (EV, 570 km range)
print(ev.make)             # Tesla — inherited attribute
print(f"{ev.charge_time():.1f}h")  # 2.3h
```

## Inheritance Hierarchy — UML Sketch

```
                +------------------+
                |     Vehicle      |
                +------------------+
                | make, model,year |
                | info()           |
                +------------------+
                        ^
          _______________|_______________
         |                               |
+---------------------+       +---------------------+
|  ElectricVehicle    |       |   GasolineVehicle   |
+---------------------+       +---------------------+
| range_km            |       | tank_litres         |
| info() (overrides)  |       | fuel_level          |
| charge_time()       |       | refuel()            |
+---------------------+       +---------------------+
```

`^` means "inherits from". Each subclass *extends* the parent without duplicating its code.

## Method Resolution Order (MRO)

Python uses the **C3 linearization** algorithm to determine which method to call when a class has multiple parents. The MRO is the order in which Python searches the class hierarchy:

```python
class A:
    def hello(self): return "A"

class B(A):
    def hello(self): return "B"

class C(A):
    def hello(self): return "C"

class D(B, C):      # multiple inheritance — B before C
    pass

print(D.__mro__)
# (<class 'D'>, <class 'B'>, <class 'C'>, <class 'A'>, <class 'object'>)

print(D().hello())  # "B" — Python finds hello in B before C
```

The MRO guarantees that `super()` always calls the *next class in the MRO*, not necessarily the direct parent. This makes cooperative multiple inheritance work correctly:

```python
class LogMixin:
    def info(self) -> str:
        result = super().info()   # calls whoever is next in the MRO
        print(f"[LOG] {result}")
        return result

class LoggingEV(LogMixin, ElectricVehicle):
    pass

lev = LoggingEV("BMW", "iX", 2024, 600)
lev.info()
# [LOG] 2024 BMW iX (EV, 600 km range)
```

`super()` in `LogMixin.info` calls `ElectricVehicle.info` because the MRO is `LoggingEV → LogMixin → ElectricVehicle → Vehicle → object`.

## The `isinstance` and `issubclass` Checks

```python
d = Dog("Rex", "woof")

print(isinstance(d, Dog))     # True
print(isinstance(d, Animal))  # True  — Dog IS-A Animal
print(isinstance(d, Cat))     # False

print(issubclass(Dog, Animal))   # True
print(issubclass(Cat, Dog))      # False
print(issubclass(Dog, object))   # True — everything inherits from object
```

Use `isinstance` over direct `type(x) == Dog` checks — it respects the entire inheritance chain.

## Composition vs Inheritance

Inheritance can be overused. Apply the **IS-A test**: if you cannot honestly say "a `SubClass` IS-A `ParentClass`", you should use composition instead.

```python
# Inheritance (IS-A): Dog IS-A Animal — correct
class Dog(Animal): ...

# Composition (HAS-A): Car HAS-A Engine — NOT "Car is an Engine"
class Engine:
    def __init__(self, horsepower: int):
        self.hp = horsepower
    def start(self) -> str:
        return "Vroom"

class Car:
    def __init__(self, make: str, engine: Engine):
        self.make   = make
        self.engine = engine          # Car has an Engine

    def drive(self) -> str:
        return f"{self.make}: {self.engine.start()}"
```

```python
v8  = Engine(400)
car = Car("Mustang", v8)
print(car.drive())   # Mustang: Vroom
```

Composition is more flexible: you can swap the `Engine` at runtime, inject a mock in tests, and avoid the fragile base class problem.

## The Fragile Base Class Problem

Deep inheritance hierarchies become fragile when a change to the base class breaks subclasses:

```python
class Base:
    def method_a(self):
        self.method_b()    # Base assumes method_b exists

    def method_b(self):
        print("Base B")

class Child(Base):
    def method_b(self):    # override
        print("Child B")
        # Calling super().method_b() would call Base.method_b
```

If `Base.method_a` changes which methods it calls internally, `Child` may silently break. Prefer shallow hierarchies (1–2 levels) in most designs.

## Mixin Classes

A **mixin** is a class designed to be mixed into another via multiple inheritance to add a specific capability, without being a standalone base class:

```python
class JsonMixin:
    """Adds JSON serialisation to any class that defines to_dict()."""

    def to_json(self) -> str:
        import json
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, text: str):
        import json
        return cls(**json.loads(text))


class Product:
    def __init__(self, name: str, price: float):
        self.name  = name
        self.price = price

    def to_dict(self) -> dict:
        return {"name": self.name, "price": self.price}


class JsonProduct(JsonMixin, Product):
    pass
```

```python
jp = JsonProduct("Widget", 9.99)
print(jp.to_json())   # {"name": "Widget", "price": 9.99}
```

`JsonMixin` adds behaviour without knowing anything about `Product`. It only requires a `to_dict()` method — an informal contract.

## Key Takeaways

- Subclasses inherit all attributes and methods from their parent.
- Always call `super().__init__(...)` in a subclass `__init__` to properly initialize the parent portion.
- `super()` follows the MRO — it is safe to use in cooperative multiple inheritance.
- Use `isinstance()` to check type; prefer it over `type(x) == SomeClass`.
- Apply the IS-A test: if it doesn't hold, use composition instead of inheritance.
- Keep hierarchies shallow (1–2 levels); use mixins for orthogonal capabilities.
