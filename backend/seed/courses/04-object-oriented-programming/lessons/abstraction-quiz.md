# Quiz: Abstraction and Interfaces

**Q1. Which decorator marks a method as abstract in Python?**

- [ ] `@abstract`
- [ ] `@interface`
- [x] `@abstractmethod`
- [ ] `@override`

**Q2. To create an abstract base class (ABC) in Python, your class should:**

- [ ] Inherit from `Interface`
- [x] Inherit from `ABC` (from the `abc` module) or use `ABCMeta` as its metaclass
- [ ] Define at least one method starting with double underscores
- [ ] Use the `@abstract` class decorator

**Q3. What is a "protocol" in Python's type system (introduced by PEP 544)?**

- [ ] A formal contract enforced at runtime like an ABC
- [x] A structural subtyping mechanism — any class with the required methods satisfies the protocol, without explicit inheritance
- [ ] A synonym for ABC
- [ ] A way to enforce method signatures at class definition time

**Q4. Given the following, which statement is TRUE?**

```python
from abc import ABC, abstractmethod

class Drawable(ABC):
    @abstractmethod
    def draw(self): ...

class Circle(Drawable):
    def draw(self):
        print("Drawing circle")

class Square(Drawable):
    pass
```

- [ ] Both `Circle()` and `Square()` can be instantiated
- [ ] Neither `Circle()` nor `Square()` can be instantiated
- [x] `Circle()` can be instantiated; `Square()` raises `TypeError`
- [ ] `Square()` can be instantiated but calling `draw()` raises `NotImplementedError`

**Q5. What is the main advantage of programming to an interface (abstract class) rather than a concrete class?**

- [ ] It makes the code run faster
- [ ] It reduces the number of classes needed
- [x] It decouples the caller from specific implementations, making it easy to swap in different concrete classes
- [ ] It prevents subclasses from overriding methods

**Q6. Which of the following is the best use of an abstract base class?**

- [ ] When you want to prevent any class from being instantiated
- [ ] When you need to share state across all subclasses
- [x] When you want to define a required interface that all concrete subclasses must implement
- [ ] When you want to combine behavior from multiple unrelated classes
