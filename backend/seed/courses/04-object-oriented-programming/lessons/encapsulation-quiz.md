# Quiz: Encapsulation

**Q1. What does the `__name` (double-underscore prefix) naming convention do in Python?**

- [ ] Makes the attribute completely inaccessible from outside the class
- [x] Triggers name-mangling, renaming it to `_ClassName__name`
- [ ] Makes the attribute read-only
- [ ] Marks the attribute as a class attribute

**Q2. Which Python feature lets you use attribute-access syntax (`obj.x = val`) while running validation code behind the scenes?**

- [ ] `@staticmethod`
- [ ] `@classmethod`
- [x] `@property` with a `@name.setter`
- [ ] `__slots__`

**Q3. What happens if you define a `@property` getter but no `@name.setter`?**

- [ ] Python raises a `SyntaxError`
- [ ] The property defaults to returning `None` on assignment
- [x] The attribute is read-only; assigning to it raises `AttributeError`
- [ ] The setter is automatically generated with no validation

**Q4. An invariant in OOP refers to:**

- [ ] A constant value that never changes
- [ ] A method that takes no arguments
- [x] A condition that must always be true for an object to be in a valid state
- [ ] An attribute that cannot be overridden in subclasses

**Q5. Given the following class, what is printed?**

```python
class Box:
    def __init__(self, size):
        self._size = size

    @property
    def size(self):
        return self._size * 2

b = Box(5)
print(b.size)
```

- [ ] `5`
- [x] `10`
- [ ] `AttributeError`
- [ ] `None`

**Q6. Which of the following is the most Pythonic way to enforce that an attribute `radius` must always be positive?**

- [ ] Document that callers must not set a negative radius
- [ ] Define `get_radius()` and `set_radius()` methods
- [x] Define `@property` with a setter that raises `ValueError` for non-positive values
- [ ] Use `__slots__` to restrict which attributes can be set
