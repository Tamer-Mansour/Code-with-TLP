# Lifetime Region Checker

Given a set of variable declarations with their alive scope ranges (line numbers), and a set of references that borrow from those variables, determine for each reference whether it is valid or dangling.

## Input Format

```
N
<name> <start_line> <end_line>
...  (N lines, one per variable)
M
<ref_name> borrows <var_name> <start_line> <end_line>
...  (M lines, one per reference)
```

- Variables are alive from `start_line` to `end_line` inclusive.
- Each reference borrows from an existing variable and is itself alive from its own `start_line` to `end_line`.

## Output

For each reference (in order), print one line:

- `VALID` — if the variable's lifetime fully covers the reference's lifetime (variable start <= ref start AND variable end >= ref end)
- `DANGLING: <ref_name> outlives <var_name>` — if the reference exists outside the variable's alive range

## Sample Input

```
3
x 1 10
y 3 7
z 5 15
4
ref1 borrows x 2 9
ref2 borrows y 4 8
ref3 borrows z 6 14
ref4 borrows y 3 7
```

## Sample Output

```
VALID
DANGLING: ref2 outlives y
VALID
VALID
```

## Explanation

- `ref1` borrows `x` (lines 2–9): `x` alive 1–10. Fully covers 2–9. **VALID**.
- `ref2` borrows `y` (lines 4–8): `y` alive 3–7. Ref ends at 8, but `y` ends at 7. **DANGLING**.
- `ref3` borrows `z` (lines 6–14): `z` alive 5–15. Fully covers 6–14. **VALID**.
- `ref4` borrows `y` (lines 3–7): `y` alive 3–7. Exactly covered. **VALID**.

## Constraints

- `1 <= N <= 20` variables
- `1 <= M <= 20` references
- Line numbers are positive integers
- All referenced variable names exist in the variable declarations
