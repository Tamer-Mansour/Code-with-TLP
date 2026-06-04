# Normalize to 1NF

## Problem

A table violates First Normal Form (1NF) because a column stores multiple semicolon-separated course names in a single cell. Your task is to normalize it: output one row per `(student_id, course)` pair.

**Input format:**

```
N
student_id1 course_A;course_B;course_C
student_id2 course_D
...
```

- First line: `N`, the number of student rows
- Each following line: a student ID (integer), a space, then a semicolon-separated list of course names (no spaces inside course names)

**Output:**

One line per `(student_id, course)` pair in the format `student_id course`, sorted by `student_id` ascending, then by course name ascending (alphabetical).

## Example

**Input:**
```
3
101 Math;Science;Art
102 Science
103 Math;Art
```

**Output:**
```
101 Art
101 Math
101 Science
102 Science
103 Art
103 Math
```

## Constraints

- `1 <= N <= 500`
- Each student has `1` to `10` courses
- Student IDs are positive integers
- Course names are alphabetic strings (no spaces, no special characters)
- The same student ID will not appear more than once in the input
