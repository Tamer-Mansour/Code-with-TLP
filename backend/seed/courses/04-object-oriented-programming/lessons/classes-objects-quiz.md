# Quiz: Classes and Objects

**Q1. What is the difference between a class and an object in Python?**

- [ ] A class is created at runtime; an object is defined at design time
- [ ] They are the same thing — "class" and "object" are interchangeable terms
- [x] A class is a blueprint or template; an object is a concrete instance created from that blueprint
- [ ] A class holds behavior only; an object holds state only

**Q2. Which method is automatically called when you create a new instance of a class?**

- [ ] `__new__`
- [x] `__init__`
- [ ] `__create__`
- [ ] `__start__`

**Q3. What does the `self` parameter refer to inside an instance method?**

- [ ] The class itself
- [ ] The parent class
- [x] The specific instance on which the method is being called
- [ ] A global singleton shared across all instances

**Q4. Given the following code, what is printed?**

```python
class Dog:
    def __init__(self, name):
        self.name = name

rex = Dog("Rex")
fido = Dog("Fido")
print(rex is fido)
print(rex.name == fido.name)
```

- [ ] `True` then `True`
- [ ] `True` then `False`
- [x] `False` then `False`
- [ ] `False` then `True`

**Q5. What is an instance attribute?**

- [ ] An attribute shared by all instances of a class
- [x] A piece of data that belongs to one specific object and is set via `self`
- [ ] An attribute defined outside the class body
- [ ] A read-only attribute that cannot be changed after construction

**Q6. Which of the following correctly creates two independent Counter objects, each starting at 0?**

```python
class Counter:
    def __init__(self):
        self.count = 0
```

- [ ] `a = b = Counter()`
- [x] `a = Counter(); b = Counter()`
- [ ] `a = Counter; b = Counter`
- [ ] `a, b = Counter(0, 0)`

**Q7. A class is to a cookie cutter as an object is to a:**

- [ ] Recipe
- [ ] Oven
- [x] Cookie
- [ ] Kitchen
