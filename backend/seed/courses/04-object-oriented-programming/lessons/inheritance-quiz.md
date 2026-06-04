# Quiz: Inheritance

**Q1. What does Python's `super()` function do inside a method?**

- [ ] Always calls the method on the direct parent class
- [x] Calls the next class in the Method Resolution Order (MRO)
- [ ] Creates a new superclass instance
- [ ] Returns a reference to the base `object` class

**Q2. Which of the following correctly chains `__init__` in a subclass?**

```python
class Animal:
    def __init__(self, name):
        self.name = name

class Dog(Animal):
    def __init__(self, name, breed):
        ___________________
        self.breed = breed
```

- [ ] `Animal.__init__(name)`
- [ ] `super(name).__init__()`
- [x] `super().__init__(name)`
- [ ] `self.__init__(name)`

**Q3. What does Python's C3 linearization algorithm determine?**

- [ ] The order in which modules are imported
- [ ] The memory layout of instance attributes
- [x] The Method Resolution Order (MRO) — the sequence of classes searched when a method is called
- [ ] The order in which `__init__` arguments are evaluated

**Q4. Given the following, what is printed by `print(C.__mro__)`?**

```python
class A: pass
class B(A): pass
class C(B): pass
```

- [ ] `(<class 'C'>, <class 'A'>, <class 'B'>, <class 'object'>)`
- [x] `(<class 'C'>, <class 'B'>, <class 'A'>, <class 'object'>)`
- [ ] `(<class 'A'>, <class 'B'>, <class 'C'>, <class 'object'>)`
- [ ] `(<class 'object'>, <class 'A'>, <class 'B'>, <class 'C'>)`

**Q5. Method overriding in Python means:**

- [ ] Defining a method with the same name but a different number of parameters
- [ ] Preventing a subclass from calling a parent method
- [x] Redefining an inherited method in a subclass so the subclass version is called instead
- [ ] Renaming a method to avoid name conflicts

**Q6. Which best describes the "prefer composition over inheritance" principle?**

- [ ] Inheritance should never be used
- [ ] Composition always runs faster than inheritance
- [ ] Both patterns are identical; the choice is stylistic only
- [x] Use inheritance to model true is-a relationships; use composition (has-a) for code reuse to avoid tight coupling

**Q7. What is the diamond problem in multiple inheritance?**

- [ ] A memory leak caused by circular references between parent classes
- [x] Ambiguity about which parent's method to call when two parents both inherit from the same base class
- [ ] An error that occurs when a class inherits from more than two classes
- [ ] A situation where a subclass cannot call `super()`
