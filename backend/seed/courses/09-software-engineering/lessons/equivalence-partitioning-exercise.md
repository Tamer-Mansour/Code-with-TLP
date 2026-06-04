# Exercise: Equivalence Class Partitioner

Equivalence partitioning is a core black-box testing technique that divides the input domain into classes where every value in a class should be treated identically by the software under test.

Instead of testing every possible input (impossible for any realistic program), a tester selects *one representative value* from each equivalence class. A defect in how the program handles the class boundary will be caught by any value in that class.

## The Specification

You are implementing the classification logic described in the following specification:

```
A ticket-pricing function accepts an integer age and returns a category:
  age < 0          → INVALID
  0 <= age <= 12   → CHILD
  13 <= age <= 17  → TEEN
  18 <= age <= 64  → ADULT
  age >= 65        → SENIOR
```

The equivalence classes for this specification are:
- **Class 1:** age < 0 (invalid inputs)
- **Class 2:** 0–12 (child range)
- **Class 3:** 13–17 (teen range)
- **Class 4:** 18–64 (adult range)
- **Class 5:** age ≥ 65 (senior range)

## Task

Given `N` test cases (one integer per line), output the category for each.

## Input Format

- First line: `N` — number of test cases
- Next `N` lines: one integer per line

## Output Format

One category per line, in the same order as the input.

## Example

**Input:**
```
5
-1
0
10
18
65
```

**Output:**
```
INVALID
CHILD
CHILD
ADULT
SENIOR
```

## Hints

- Boundary values (0, 12, 13, 17, 18, 64, 65) are where specification bugs most often hide — test them too.
- The boundaries themselves define the edges of the equivalence classes.
- Ages of −1 and −1000 belong to the *same* equivalence class and should produce identical output.
