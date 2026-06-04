# FizzBuzz Classic

Read a single integer **N** from standard input.

Print all integers from **1 to N** (inclusive), one per line, with the following substitutions:

- If the number is divisible by **both 3 and 5**, print `FizzBuzz`.
- If the number is divisible by **3 only**, print `Fizz`.
- If the number is divisible by **5 only**, print `Buzz`.
- Otherwise, print the number itself.

## Input format

A single integer `N` (1 ≤ N ≤ 100).

## Output format

N lines, one per number from 1 to N, with substitutions applied.

## Example

**Input:**
```
15
```

**Output:**
```
1
2
Fizz
4
Buzz
Fizz
7
8
Fizz
Buzz
11
Fizz
13
14
FizzBuzz
```

## Hints

- Check the combined condition (`n % 15 == 0`) **before** checking the individual ones.
- `range(1, N + 1)` produces 1, 2, 3, …, N.
