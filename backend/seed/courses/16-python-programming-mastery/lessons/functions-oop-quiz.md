# Quiz: Functions and OOP

**Q1. What is printed by the following code?**
```python
def add(x, history=[]):
    history.append(x)
    return history

print(add(1))
print(add(2))
```
- [ ] `[1]` then `[2]`
- [x] `[1]` then `[1, 2]`
- [ ] `[1]` then `[1, 2]` then error on second call
- [ ] A `TypeError` on the first call

**Q2. Which keyword allows a nested function to write to a variable in its enclosing scope?**
- [ ] `global`
- [x] `nonlocal`
- [ ] `outer`
- [ ] `enclosing`

**Q3. What does `super().__init__(...)` do inside a subclass `__init__`?**
- [ ] Creates a new instance of the parent class
- [x] Calls the parent class constructor to initialise inherited attributes
- [ ] Returns the parent class object
- [ ] Overrides the parent class completely

**Q4. What is `self` in a Python instance method?**
- [ ] A keyword reserved by the language (like `this` in Java)
- [x] A conventional first parameter that refers to the instance the method was called on
- [ ] A reference to the class, not the instance
- [ ] Optional — it can be omitted freely

**Q5. Which of the following correctly uses a lambda?**
- [ ] `lambda x, y: return x + y`
- [x] `lambda x, y: x + y`
- [ ] `lambda(x, y): x + y`
- [ ] `def lambda(x, y): x + y`

**Q6. A `@classmethod` receives _______ as its first argument.**
- [ ] `self` (the instance)
- [x] `cls` (the class itself)
- [ ] `type` (the metaclass)
- [ ] Nothing — it takes no implicit first argument

**Q7. When should you use `raise NotImplementedError` in a method?**
- [ ] When the method encounters a `None` value
- [ ] When the method is a lambda
- [x] When defining an abstract interface method that subclasses must override
- [ ] When the method returns `NotImplemented` from a dunder
