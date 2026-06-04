# Simulate a SELECT with WHERE Filter

## Problem

You are given **N** rows of employee data. Each row has four comma-separated fields: `id`, `name`, `department`, `salary`.

Print only the rows where:
- `department` is exactly `Engineering`, **AND**
- `salary` is greater than or equal to `60000`

Output each matching row in its original format (`id,name,department,salary`), one per line, in the **original input order**.

This simulates the SQL:
```sql
SELECT id, name, department, salary
FROM   dbo.employees
WHERE  department = 'Engineering'
  AND  salary >= 60000;
```

## Input Format

- Line 1: integer `N` — the number of employee rows
- Next `N` lines: `id,name,department,salary`
  - `id` — positive integer
  - `name` — string with no commas
  - `department` — string with no commas
  - `salary` — non-negative integer

## Output Format

Each matching row printed as `id,name,department,salary`, one per line, in original order. If no rows match, print nothing.

## Constraints

- `1 <= N <= 1000`
- Salary values are non-negative integers up to `999999`
- Department names are case-sensitive

## Example

**Input:**
```
5
1,Alice,Engineering,75000
2,Bob,Marketing,50000
3,Carol,Engineering,55000
4,Dave,Engineering,80000
5,Eve,HR,62000
```

**Output:**
```
1,Alice,Engineering,75000
4,Dave,Engineering,80000
```

Carol is excluded because her salary (55000) is below 60000. Bob and Eve are excluded because their departments are not Engineering.
