# FizzBuzz Classic

FizzBuzz is a classic programming interview problem that tests your ability to combine conditional logic with loop iteration. The challenge is subtle: you must check the most specific condition (divisible by both 3 and 5) **before** the individual ones, otherwise multiples of 15 will match an earlier branch and never reach the `FizzBuzz` case.

## What You Will Practice

- `for` loop with `range()`
- Chained `if / elif / else` conditions
- Modulo operator `%` for divisibility testing
- The importance of condition ordering

## Approach

Work through this methodically:

1. Loop `i` from 1 to N inclusive.
2. For each `i`, test conditions in order: `i % 15 == 0` first, then `i % 3`, then `i % 5`, then the default.
3. Print the appropriate string (or number).

```python
# Skeleton
n = int(input())
for i in range(1, n + 1):
    if i % 15 == 0:
        print("FizzBuzz")
    elif i % 3 == 0:
        print("Fizz")
    elif i % 5 == 0:
        print("Buzz")
    else:
        print(i)
```

Notice that `i % 15 == 0` is equivalent to `i % 3 == 0 and i % 5 == 0`. Either form works, but checking `% 15` is more concise.
