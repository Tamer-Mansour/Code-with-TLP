# Equivalence Class Partitioner

Equivalence partitioning divides an input domain into classes where every value in a class is expected to be handled identically by the code under test.

You are given the specification of a ticket-pricing function:

```
age < 0          → INVALID
0 <= age <= 12   → CHILD
13 <= age <= 17  → TEEN
18 <= age <= 64  → ADULT
age >= 65        → SENIOR
```

Given `N` test cases (one integer per line), output the category for each age.

## Input Format

- First line: `N`
- Next `N` lines: one integer per line

## Output Format

One category per line (`INVALID`, `CHILD`, `TEEN`, `ADULT`, or `SENIOR`).

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
