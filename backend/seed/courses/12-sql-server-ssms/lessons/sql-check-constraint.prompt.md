# Enforce a CHECK Constraint

## Problem

You are given **N** rows of data intended to be inserted into a table with two CHECK constraints:

1. `age` must be between `18` and `65` **inclusive**
2. `status` must be either `'active'` or `'inactive'`

For each row, print `OK` if it passes **both** constraints, or `REJECTED` if it violates either one.

This simulates how SQL Server CHECK constraints enforce data integrity at insert time.

## Input Format

- Line 1: integer `N` — the number of rows
- Next `N` lines: `name,age,status`
  - `name` — string with no commas
  - `age` — integer
  - `status` — string

## Output Format

One line per row: either `OK` or `REJECTED`, in the original order.

## Constraints

- `1 <= N <= 500`
- `age` is always an integer (may be outside 18–65)
- `status` is a non-empty string

## Example

**Input:**
```
5
Alice,25,active
Bob,17,active
Carol,40,pending
Dave,65,inactive
Eve,70,active
```

**Output:**
```
OK
REJECTED
REJECTED
OK
REJECTED
```

- Alice (25, active): both constraints satisfied → OK
- Bob (17, active): age 17 < 18 → REJECTED
- Carol (40, pending): status 'pending' is not in ('active', 'inactive') → REJECTED
- Dave (65, inactive): age 65 is within 18–65, status valid → OK
- Eve (70, active): age 70 > 65 → REJECTED
