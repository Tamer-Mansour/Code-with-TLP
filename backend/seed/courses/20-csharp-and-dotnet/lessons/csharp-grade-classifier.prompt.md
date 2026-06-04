# Grade Classifier

Read a single integer **score** (0–100) from stdin.

Print the **letter grade** on the first line using standard US grading:

| Score range | Grade |
|-------------|-------|
| 90 – 100    | A     |
| 80 – 89     | B     |
| 70 – 79     | C     |
| 60 – 69     | D     |
| Below 60    | F     |

Print `Pass` or `Fail` on the second line. A score of F is `Fail`; everything else is `Pass`.

## Input

A single integer on one line (0 ≤ score ≤ 100).

## Output

Two lines: the letter grade, then `Pass` or `Fail`.

## Example

**Input:**
```
85
```

**Output:**
```
B
Pass
```

**Input:**
```
55
```

**Output:**
```
F
Fail
```
