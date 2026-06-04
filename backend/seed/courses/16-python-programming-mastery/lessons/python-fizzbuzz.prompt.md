# FizzBuzz Classic

Read a single integer `N` from standard input. Print every integer from 1 to `N` (inclusive), one per line, but apply the following substitution rules:

- If the number is divisible by **both** 3 and 5, print `FizzBuzz`.
- If the number is divisible by **only** 3, print `Fizz`.
- If the number is divisible by **only** 5, print `Buzz`.
- Otherwise, print the number itself.

## Input

A single integer `N` (1 ≤ N ≤ 100).

## Output

`N` lines, one per number from 1 to `N`, applying the substitution rules above.

## Examples

**Example 1**
```
Input:  15
Output:
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

**Example 2**
```
Input:  5
Output:
1
2
Fizz
4
Buzz
```

## Hints

- Check divisibility by 15 **first** — if you check 3 first you'll print `Fizz` instead of `FizzBuzz` for 15.
- The modulo operator `%` returns the remainder: `15 % 3 == 0` is `True`.
- Use `range(1, N + 1)` to iterate from 1 through N inclusive.
