# Exercise: FizzBuzz Classic

FizzBuzz is the most famous programming interview warm-up. It tests whether you can combine a loop, conditional logic, and the modulo operator — three fundamentals that appear in almost every real program.

## What You Will Practice

- `for` loops with `range()`
- `if / elif / else` chains
- The `%` (modulo) operator for divisibility testing
- Correct order of condition checks

## The Core Idea

The modulo operator returns the remainder after integer division:

```python
10 % 3   # 1   (10 = 3*3 + 1)
15 % 3   # 0   (divisible)
15 % 5   # 0   (divisible)
```

A number is divisible by `k` when `n % k == 0`.

## Order of Conditions Matters

A common mistake is checking 3 and 5 before checking 15:

```python
# WRONG — prints "Fizz" for 15 instead of "FizzBuzz"
if n % 3 == 0:
    print("Fizz")
elif n % 5 == 0:
    print("Buzz")

# CORRECT — most specific case first
if n % 15 == 0:
    print("FizzBuzz")
elif n % 3 == 0:
    print("Fizz")
elif n % 5 == 0:
    print("Buzz")
else:
    print(n)
```

Alternatively, build the string by concatenation:

```python
result = ""
if n % 3 == 0:
    result += "Fizz"
if n % 5 == 0:
    result += "Buzz"
print(result or n)
```

This approach avoids the ordering problem entirely and is easier to extend.

## Further Reading

For a deeper treatment of loops and conditionals, see MIT OCW 6.100L by Dr. Ana Bell: [https://ocw.mit.edu/courses/6-100l-introduction-to-cs-and-programming-using-python-fall-2022/](https://ocw.mit.edu/courses/6-100l-introduction-to-cs-and-programming-using-python-fall-2022/). Lectures 3 and 4 cover branching and loops in detail.
