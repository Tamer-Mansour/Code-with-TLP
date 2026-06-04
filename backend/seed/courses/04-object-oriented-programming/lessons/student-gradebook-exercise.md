# Exercise: Student Grade Book

In this exercise you will build a `Student` class that uses both **instance variables** (per-student data) and a **class variable** (shared counter) to track students and their grades.

## What You Will Practice

- Class variables vs. instance variables
- The `@classmethod` decorator
- Encapsulation: keeping internal data private with a leading underscore
- Computing a running average from a list of grades

## Background

A **class variable** is declared directly in the class body (not inside `__init__`). It is shared across all instances unless shadowed by an instance attribute with the same name:

```python
class Example:
    shared = 0          # class variable

    def __init__(self):
        self.own = 0    # instance variable
```

A **class method** receives the class (`cls`) as its first argument instead of an instance (`self`). Decorated with `@classmethod`, it can read and modify class variables:

```python
@classmethod
def class_method(cls):
    return cls.shared
```

## Task

Implement the `Student` class and the command loop described in the prompt.

## Sample Run

Input:
```
new Alice
new Bob
grade Alice 85
grade Alice 90
grade Alice 78
grade Bob 70
avg Alice
avg Bob
count
```

Output:
```
84.33
70.00
2
```

> **Tip:** `84.33` is `(85 + 90 + 78) / 3 = 253 / 3 ≈ 84.333...`. Round the output to 2 decimal places with `f"{value:.2f}"`.

## Further Reading

- *Think Python* (Allen B. Downey) — Chapter 17 covers class methods and class variables in depth.
  [https://greenteapress.com/thinkpython2/thinkpython2.pdf](https://greenteapress.com/thinkpython2/thinkpython2.pdf)
- *MIT OCW 6.0001* — Lecture 9 slides discuss class vs. instance data.
  [https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/](https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/)
