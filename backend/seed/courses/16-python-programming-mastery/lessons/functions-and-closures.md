# Functions, Defaults, Closures

## Defining a function

```python
def greet(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"
```

- `name: str` — type hint (optional, not enforced at runtime).
- `greeting="Hello"` — default value.
- `-> str` — return type hint.

Call positionally or by keyword:

```python
greet("Alice")
greet("Alice", greeting="Hi")
greet(greeting="Hi", name="Alice")
```

## *args and **kwargs

```python
def log(*args, **kwargs):
    print(args, kwargs)

log(1, 2, 3, level="DEBUG")
# args=(1, 2, 3), kwargs={'level': 'DEBUG'}
```

- `*args` packs extra positional args into a tuple.
- `**kwargs` packs extra keyword args into a dict.

Unpacking at the call site uses the same `*`/`**`:

```python
xs = [1, 2, 3]
print(*xs)        # print(1, 2, 3)

config = {"name": "Alice", "age": 30}
greet(**config)   # greet(name="Alice", age=30)
```

## Positional-only and keyword-only

```python
def f(a, b, /, c, d, *, e, f):
    ...
# a, b: positional-only (must NOT be passed by name)
# c, d: either
# e, f: keyword-only (must be passed by name)
```

Useful for stable APIs — you can rename `a` later without breaking callers.

## Default arguments are evaluated once

A classic Python footgun:

```python
def bad(x, history=[]):
    history.append(x)
    return history

bad(1)   # [1]
bad(2)   # [1, 2]   ← surprise! same list
```

Fix:

```python
def good(x, history=None):
    if history is None:
        history = []
    history.append(x)
    return history
```

Rule: **never use mutable defaults.**

## Closures

A function defined inside another captures the enclosing variables:

```python
def counter():
    n = 0
    def inc():
        nonlocal n
        n += 1
        return n
    return inc

c = counter()
c(); c(); c()       # 1, 2, 3
```

`nonlocal` is needed when you want to *write* to the captured variable. Reading is automatic.

## first-class functions

Functions are values — pass them around like data:

```python
def apply(f, xs):
    return [f(x) for x in xs]

apply(str.upper, ["a", "b"])    # ["A", "B"]
```

## Lambdas

Anonymous one-expression functions:

```python
sorted(words, key=lambda w: len(w))
```

Don't over-use. A named function is usually clearer.

## Higher-order helpers in the stdlib

```python
from functools import reduce, partial, lru_cache

reduce(lambda acc, x: acc + x, [1, 2, 3], 0)   # 6, but use sum() instead
add5 = partial(add, 5)                         # pre-bound first arg

@lru_cache(maxsize=128)
def fib(n):
    return n if n < 2 else fib(n-1) + fib(n-2)
```

`lru_cache` adds memoization in one line. Game-changer for recursive problems.
