# Student Grade Book

## Problem Statement

Create a `Student` class that tracks individual student grades and a class-wide student count.

**Class requirements:**

- Each student has a `name` (string) and a private list of grades `_grades` (floats), both set in `__init__`.
- A class variable `_count` starts at `0` and increments by 1 each time a new `Student` is created.
- `add_grade(score)` — appends a float grade to `_grades`.
- `average()` — returns the mean of all grades as a float. Returns `0.0` if no grades have been added.
- `student_count()` — a `@classmethod` that returns the current value of `_count`.

**Input format:**

Read commands from stdin until EOF. Each line is one of:

| Command | Action |
|---------|--------|
| `new <name>` | Create a new Student with the given name |
| `grade <name> <score>` | Add `score` (float) to the named student's grades |
| `avg <name>` | Print that student's average rounded to 2 decimal places |
| `count` | Print the total number of Student objects created |

You may assume all student names are unique single words and that `grade`/`avg` commands always refer to previously created students.

**Output format:**

- For `avg`: print a single line with the average formatted to exactly 2 decimal places.
- For `count`: print a single integer.
- `new` and `grade` commands produce no output.

## Examples

**Example 1**

Input:
```
new Alice
new Bob
grade Alice 85
grade Alice 90
grade Alice 78
grade Bob 70
avg Alice
avg Bob
count
```

Output:
```
84.33
70.00
2
```

**Example 2**

Input:
```
new Zara
avg Zara
count
```

Output:
```
0.00
1
```

**Example 3**

Input:
```
new X
new Y
new Z
grade X 100
grade X 100
avg X
count
```

Output:
```
100.00
3
```

## Constraints

- Number of commands: 1 – 200
- Scores are integers or floats in the range 0–100
- Student names are non-empty single words (no spaces)
