# Exercise: Fibonacci Sequence

The Fibonacci sequence is one of the most studied sequences in mathematics and computer science. It appears in nature (sunflower spirals, shell growth), algorithm analysis, and dynamic programming. Implementing it correctly requires understanding loops, multiple assignment, and list building.

## What You Will Practice

- Iterative sequence generation
- Python's simultaneous tuple assignment: `a, b = b, a + b`
- Building a list inside a loop
- Formatting output with `' '.join(map(str, ...))`

## The Iterative Approach

```python
def fibonacci(n):
    result = []
    a, b = 0, 1
    for _ in range(n):
        result.append(a)
        a, b = b, a + b
    return result
```

The magic is `a, b = b, a + b` — Python evaluates the right-hand side **before** doing any assignment, so both updates happen simultaneously without needing a temporary variable.

## Why Not Recursion Here?

Naive recursion for Fibonacci has exponential time complexity — `fib(40)` makes over a billion recursive calls. The iterative version runs in O(n). If you need recursion, add memoisation:

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
```

`@lru_cache` stores previously computed results, reducing the work to O(n) with O(n) extra memory.

## Generator Version

For very large sequences, a generator avoids building the whole list:

```python
def fib_gen():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

import itertools
first_10 = list(itertools.islice(fib_gen(), 10))
```

## Further Reading

Generators and iterators are covered in depth in the [Interactive Edition of *How to Think Like a Computer Scientist*](https://runestone.academy/ns/books/published/thinkcspy/index.html) (Runestone Academy, free). The Fibonacci sequence also appears as a canonical example in MIT OCW 6.100L by Dr. Ana Bell: [https://ocw.mit.edu/courses/6-100l-introduction-to-cs-and-programming-using-python-fall-2022/](https://ocw.mit.edu/courses/6-100l-introduction-to-cs-and-programming-using-python-fall-2022/).
