# Command-Line Calculator

Write a program that reads a **single line** from standard input containing a simple
arithmetic expression with two integers and one operator, separated by spaces:

```
<a> <op> <b>
```

- `a` and `b` are integers (they may be negative).
- `op` is one of `+`, `-`, `*`, `/`.
- For `/`, perform **integer division that truncates toward zero** (standard Java `/`
  and Python `//`-on-truncation behaviour for the given inputs — division inputs are
  chosen so the result is exact, so you don't need to worry about rounding direction).

Print the resulting integer on its own line.

## Input

```
3 + 4
```

## Output

```
7
```

## Notes

- There is exactly one expression to evaluate.
- You will never be asked to divide by zero.
- Read the operator as a string; don't assume single-digit operands.
