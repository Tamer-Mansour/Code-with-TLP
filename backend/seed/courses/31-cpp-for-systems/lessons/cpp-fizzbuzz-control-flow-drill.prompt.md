# Problem: Parameterized FizzBuzz

## Description

Given three integers `A`, `B`, and `N` on a single line, print integers from `1` to `N` (inclusive), one per line, according to these rules:

- If the integer is divisible by both `A` and `B`, print `FizzBuzz`.
- If the integer is divisible by `A` only, print `Fizz`.
- If the integer is divisible by `B` only, print `Buzz`.
- Otherwise, print the integer itself.

## Input Format

A single line containing three space-separated positive integers: `A B N`.

## Output Format

`N` lines, one per integer from `1` to `N`, following the rules above. No trailing spaces. A newline after the last line.

## Constraints

- `1 <= A <= 100`
- `1 <= B <= 100`
- `1 <= N <= 1000`

## Sample Input

```
3 5 15
```

## Sample Output

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

## Notes

- The `FizzBuzz` check must come before the individual `Fizz` and `Buzz` checks.
- When `A == B`, every multiple prints `FizzBuzz` (divisible by both simultaneously).
- When `A == 1`, every number prints `Fizz` or `FizzBuzz` — that is correct behavior.
