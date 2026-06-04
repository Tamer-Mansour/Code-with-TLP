# Exercise: Animal Hierarchy with super()

This exercise practices building a **three-level class hierarchy** where every `__init__` correctly chains to its parent using `super()`, and each class overrides the `speak()` method.

## What You Will Practice

- Defining a multi-level inheritance chain (Animal → Dog → GuideDog)
- Using `super().__init__()` to reuse parent initialization code
- Overriding methods at each level
- Implementing `__str__` for a custom string representation

## Background: Why super()?

When a subclass defines `__init__`, Python does **not** automatically call the parent's `__init__`. You must call it explicitly using `super()`:

```python
class Animal:
    def __init__(self, name):
        self.name = name

class Dog(Animal):
    def __init__(self, name):
        super().__init__(name)   # forwards 'name' to Animal.__init__
        # Dog-specific setup can follow here
```

Without `super().__init__(name)`, `self.name` would never be set, and `Dog` would lack the attribute defined in `Animal`.

## The Hierarchy

```
Animal          speak() -> "Some sound"
  └── Dog       speak() -> "Woof"
        └── GuideDog   speak() -> "Woof woof"
                       __str__ -> "<name> guides <owner>"
```

`GuideDog` adds an `owner` attribute in its own `__init__`.

## Sample Run

Input:
```
animal Cat
dog Rex
guidedog Buddy Alice
```

Output:
```
Some sound
Woof
Woof woof
Buddy guides Alice
```

## Further Reading

- *How to Think Like a Computer Scientist: Learning with Python 3* — Chapter 21 covers advanced OOP including multi-level hierarchies.
  [https://openbookproject.net/thinkcs/python/english3e/](https://openbookproject.net/thinkcs/python/english3e/)
- *Think Python* — Chapter 18 covers inheritance and `super()`.
  [https://greenteapress.com/thinkpython2/thinkpython2.pdf](https://greenteapress.com/thinkpython2/thinkpython2.pdf)
