# Quiz: Polymorphism and Abstraction

**Q1. What does polymorphism mean in OOP?**

- [ ] An object that can belong to multiple classes at once
- [x] The same interface (method name) producing different behavior depending on the actual object type
- [ ] A class that inherits from more than one parent
- [ ] A method that accepts arguments of any type

**Q2. What is "duck typing" in Python?**

- [ ] A strict type-checking mechanism that enforces interfaces at compile time
- [ ] A pattern where classes inherit from a base `Duck` class
- [x] If an object has the required methods/attributes, it is treated as compatible — regardless of its class
- [ ] A way to cast one type to another automatically

**Q3. Which module provides abstract base classes in Python?**

- [ ] `typing`
- [ ] `collections`
- [x] `abc`
- [ ] `inspect`

**Q4. What happens if a concrete subclass of an ABC does NOT implement all `@abstractmethod` methods?**

- [ ] Python silently ignores the missing methods
- [ ] The missing methods are inherited from `object` as no-ops
- [x] Attempting to instantiate the subclass raises `TypeError`
- [ ] Python raises a `NotImplementedError` at class definition time

**Q5. Given this code, what is printed?**

```python
class Shape:
    def area(self):
        return 0

class Square(Shape):
    def __init__(self, side):
        self.side = side
    def area(self):
        return self.side ** 2

shapes = [Shape(), Square(3), Square(5)]
for s in shapes:
    print(s.area())
```

- [ ] `0` then `0` then `0`
- [ ] `TypeError` because `Shape.area` cannot be called on `Square`
- [x] `0` then `9` then `25`
- [ ] `0` then `3` then `5`

**Q6. What is the key difference between abstraction and encapsulation?**

- [ ] Abstraction is about hiding methods; encapsulation is about hiding data
- [ ] They are the same concept, just different terms
- [x] Encapsulation bundles data with the methods that operate on it; abstraction hides implementation complexity behind a simple interface
- [ ] Abstraction applies only to abstract classes; encapsulation applies to all classes
