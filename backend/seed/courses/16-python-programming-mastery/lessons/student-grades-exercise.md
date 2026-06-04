# Exercise: Student Grade Classifier

This exercise combines several Python fundamentals: reading multi-line input, defining helper functions, using lists of tuples, and sorting. It mirrors the kind of data-processing script you will write constantly in real projects.

## What You Will Practice

- Reading structured multi-line input
- Defining and calling a pure helper function
- Storing records as `(name, score)` tuples in a list
- Sorting with `sorted()` — alphabetically by the first element of each tuple
- Conditional chains (`if / elif / else`)

## Pattern: Read-Process-Output

Most command-line programs follow this pattern:

```python
# 1. Read
n = int(input())
students = []
for _ in range(n):
    parts = input().split()
    name, score = parts[0], int(parts[1])
    students.append((name, score))

# 2. Process
def classify(score):
    if score >= 90: return 'A'
    elif score >= 80: return 'B'
    elif score >= 70: return 'C'
    elif score >= 60: return 'D'
    else: return 'F'

# 3. Output
for name, score in sorted(students):
    print(f"{name}: {classify(score)}")
```

## Why Use a Helper Function?

Keeping the grading logic in `classify()` makes it:

- **Testable** — call `classify(85)` in isolation without any I/O.
- **Readable** — the output loop is one clean line.
- **Reusable** — add more output formats without duplicating the grade logic.

## Sorting Tuples

`sorted(students)` sorts a list of `(name, score)` tuples by `name` (the first element) by default because Python compares tuples element-by-element. To sort by score you would write:

```python
sorted(students, key=lambda s: s[1])
```

## Further Reading

The [OpenStax *Introduction to Python Programming*](https://openstax.org/details/books/introduction-python-programming) textbook (free online, Rice University) covers functions, lists, and sorting in its first four chapters — all directly relevant to this exercise. It includes an embedded code runner so you can experiment without leaving your browser.
