# Factorial via Recursion

Factorial is the canonical example for learning recursion. It has a clear base case (`0! = 1`), a clear recursive case (`n! = n × (n-1)!`), and the call stack unwinds in a way you can trace by hand.

## What You Will Practice

- Writing a recursive function with a correct base case
- Understanding the call stack and how values unwind
- Converting a mathematical definition directly into code

## How Factorial Unfolds

Calling `factorial(4)`:

```
factorial(4)
  = 4 * factorial(3)
  = 4 * (3 * factorial(2))
  = 4 * (3 * (2 * factorial(1)))
  = 4 * (3 * (2 * (1 * factorial(0))))
  = 4 * (3 * (2 * (1 * 1)))
  = 4 * (3 * (2 * 1))
  = 4 * (3 * 2)
  = 4 * 6
  = 24
```

## Starter Structure

```python
def factorial(n):
    if n == 0:
        return 1           # base case
    return n * factorial(n - 1)  # recursive case

n = int(input())
print(factorial(n))
```

## Tip

If you forget the base case, Python will call `factorial` forever until it raises `RecursionError: maximum recursion depth exceeded`. This is the most common recursion bug — always define your stopping condition first.
