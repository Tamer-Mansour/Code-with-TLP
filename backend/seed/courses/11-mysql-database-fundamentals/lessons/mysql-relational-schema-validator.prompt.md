# Relational Schema Validator

## Problem

You are given two tables: **Students** and **Enrollments**. Your job is to check referential integrity — every `student_id` in Enrollments must match an existing `id` in Students.

**Input format:**

```
N
id1 name1
id2 name2
...   (N student rows)
M
student_id1 course1
student_id2 course2
...   (M enrollment rows)
```

**Output:**

- If every `student_id` in Enrollments has a matching student: print `VALID`
- Otherwise: print `INVALID` on the first line, then print each orphaned `student_id` on its own line, sorted **ascending**

## Example

**Input:**
```
3
1 Alice
2 Bob
3 Carol
4
1 Math
2 Science
4 History
2 Art
```

**Output:**
```
INVALID
4
```

**Explanation:** Student ID `4` appears in enrollments but no student with `id = 4` exists.

## Constraints

- `1 <= N <= 1000`
- `1 <= M <= 1000`
- Student IDs are positive integers
- A `student_id` may appear multiple times in enrollments, but should only be reported once if orphaned
