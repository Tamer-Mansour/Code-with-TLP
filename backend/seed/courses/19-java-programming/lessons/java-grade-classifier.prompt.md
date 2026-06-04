# Grade Classifier with Exception Handling

Read `N` on the first line. Then read `N` lines, each containing a string that may or may not be a valid integer.

For each line:
- If the string is **not a valid integer**: print `Invalid input`
- If it is a valid integer **outside `[0, 100]`**: print `Out of range`
- If it is a valid integer in `[0, 100]`, print the letter grade:
  - `90-100` → `A`
  - `80-89` → `B`
  - `70-79` → `C`
  - `60-69` → `D`
  - `0-59` → `F`

## Input format

```
N
line1
line2
...
lineN
```

## Output format

One line per input line.

## Example

**Input**
```
6
95
82
abc
55
-5
101
```

**Output**
```
A
B
Invalid input
F
Out of range
Out of range
```

## Constraints

- `1 <= N <= 100`
