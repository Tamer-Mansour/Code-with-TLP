# Exercise: Custom Exception Hierarchy

This exercise demonstrates how exceptions in Python are themselves objects organized in a class hierarchy — a direct application of OOP and an important real-world use of inheritance.

## What You Will Practice

- Creating custom exception classes that inherit from `Exception`
- Multi-level exception class hierarchies
- Using `raise` to signal errors
- Catching exceptions at different levels of specificity with `try/except`

## Background: Exceptions are Classes

In Python, every exception is an instance of a class. The hierarchy starts at `BaseException` and most user-defined exceptions should extend `Exception`:

```
BaseException
 └── Exception
       ├── ValueError
       ├── TypeError
       ├── RuntimeError
       └── (your custom exceptions go here)
```

You can create your own exception classes with a single line:

```python
class MyError(Exception):
    pass
```

Because `MyError` inherits from `Exception`, you can `raise` it, `except` it, and even catch it by catching any of its parents:

```python
try:
    raise MyError("something went wrong")
except Exception as e:
    print(type(e).__name__, e)  # MyError something went wrong
```

## Why This Matters

Custom exceptions let callers catch only the errors they care about. A library might define a base `AppError` and then specific subclasses like `NetworkError` and `ParseError`. Callers can catch just `ParseError`, just `NetworkError`, or all `AppError`s at once.

## Sample Run

Input:
```
start
hello

stop
status
```

Output:
```
OK: start
NotFoundError: unknown: hello
ValidationError: empty input
OK: stop
OK: status
```

## Further Reading

- *Introduction to Python Programming* (OpenStax) — Chapter on exceptions covers the built-in hierarchy and creating custom exceptions.
  [https://openstax.org/books/introduction-python-programming/pages/1-introduction](https://openstax.org/books/introduction-python-programming/pages/1-introduction)
- *How to Think Like a Computer Scientist* — Chapter 27 covers exception handling with examples.
  [https://openbookproject.net/thinkcs/python/english3e/](https://openbookproject.net/thinkcs/python/english3e/)
