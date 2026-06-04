# Functions and Abstraction

A **function** is a named, reusable block of code that performs a specific task. Functions are the primary tool for organising programs: they let you write a piece of logic once and call it from many places, name complex operations so they are easy to understand, and test small pieces of code independently.

## Defining and Calling Functions

```python
def greet(name):
    """Return a personalised greeting."""
    return "Hello, " + name + "!"

message = greet("Alice")
print(message)   # Hello, Alice!
```

- `def` introduces the function definition.
- `name` is a **parameter** — a placeholder variable.
- `return` sends a value back to the caller. A function without `return` implicitly returns `None`.
- `"Alice"` is the **argument** — the actual value passed when calling.

## Parameters and Return Values

Functions can accept multiple parameters and return any Python value:

```python
def power(base, exponent):
    result = 1
    for _ in range(exponent):
        result *= base
    return result

print(power(2, 10))   # 1024
```

**Default parameters** provide fallback values:

```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

print(greet("Bob"))            # Hello, Bob!
print(greet("Bob", "Howdy"))  # Howdy, Bob!
```

## Scope: Local vs Global

Variables defined inside a function are **local** — they only exist while the function runs:

```python
def compute():
    x = 42        # local variable
    return x

compute()
print(x)          # NameError: x is not defined outside the function
```

Variables defined outside all functions are **global** and can be read (but not easily written) from inside functions:

```python
PI = 3.14159      # global constant

def area(r):
    return PI * r * r   # reading global is fine
```

Avoid modifying global variables inside functions — it makes code hard to reason about.

## Abstraction and Decomposition

**Abstraction** means hiding implementation details behind a clean interface. Once you write `greet()`, callers do not need to know how the greeting is constructed — they just call the function.

**Decomposition** means breaking a complex problem into smaller sub-problems, each solved by its own function:

```python
def is_leap_year(year):
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

def days_in_month(month, year):
    days = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if month == 2 and is_leap_year(year):
        return 29
    return days[month]
```

`days_in_month` calls `is_leap_year` — each function has one clear responsibility.

## Higher-Order Functions and Lambda

A **higher-order function** takes another function as an argument or returns one. Python's built-ins `map`, `filter`, and `sorted` are higher-order:

```python
numbers = [3, 1, 4, 1, 5, 9, 2, 6]

# map: apply a function to every element
squares = list(map(lambda x: x ** 2, numbers))

# filter: keep elements where the function returns True
evens = list(filter(lambda x: x % 2 == 0, numbers))

# sorted with a key function
words = ["banana", "fig", "apple", "date"]
by_length = sorted(words, key=lambda w: len(w))
print(by_length)   # ['fig', 'fig', 'date', 'apple', 'banana']
```

A **lambda** is a small anonymous function defined inline: `lambda parameters: expression`.

## Common Misconception

> "A function that doesn't `return` is broken."

Not at all — functions that only produce side effects (print to screen, write to a file, modify a list in place) legitimately return `None`. The important thing is that the purpose is clear from the function's name and docstring.

## Further Reading

- **Think Python (Ch. 3 & 6)** — https://greenteapress.com/wp/think-python-2e/
- **MIT 6.0001 Lecture 4: Decomposition, Abstraction, and Functions** — https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/
- **How to Think Like a Computer Scientist: Interactive Edition (Ch. 6)** — https://runestone.academy/ns/books/published/thinkcspy/index.html

## Key Takeaways

- Functions encapsulate logic so it can be reused, tested, and named clearly.
- Parameters are local placeholders; arguments are the values passed at call time.
- **Local** variables only exist inside their function; **global** variables exist for the whole program.
- Decomposition breaks big problems into small, manageable functions.
- Higher-order functions like `map`, `filter`, and `sorted` accept functions as arguments, enabling concise, expressive code.
