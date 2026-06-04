# Student Grade Classifier

Read an integer `N` (the number of students) from standard input, then `N` lines each containing a student name and an integer score separated by a single space.

For each student, classify the score into a letter grade:

| Score Range | Grade |
|-------------|-------|
| 90 – 100    | A     |
| 80 – 89     | B     |
| 70 – 79     | C     |
| 60 – 69     | D     |
| Below 60    | F     |

Print each student's name and grade on a separate line in the format `Name: Grade`, sorted alphabetically by name.

## Input

- First line: integer `N` (1 ≤ N ≤ 20)
- Next `N` lines: `<Name> <Score>` where Name is a single word and Score is an integer 0–100.

## Output

`N` lines, each `Name: Grade`, sorted alphabetically by name.

## Examples

**Example 1**
```
Input:
4
Alice 92
Bob 73
Carol 58
Dave 85

Output:
Alice: A
Bob: C
Carol: F
Dave: B
```

**Example 2**
```
Input:
3
Zara 60
Ana 100
Ben 79

Output:
Ana: A
Ben: C
Zara: D
```

## Hints

- Read the first line with `int(input())`.
- Split each subsequent line: `name, score = input().split()`.
- Use `sorted()` on the list of `(name, score)` tuples — Python sorts tuples by the first element by default.
- Define a `classify(score)` function to keep the grading logic separate.
