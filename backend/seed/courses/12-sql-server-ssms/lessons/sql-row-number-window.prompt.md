# Simulate ROW_NUMBER Window Function

## Problem

You are given **N** employee records. Each record contains a department name, employee name, and salary.

Assign a `ROW_NUMBER` to each employee **within their department**, ordered by **salary descending** (highest salary = row number 1). For employees with the same salary in the same department, preserve the **original input order** (stable sort — the employee appearing first in the input gets the lower row number).

Output each row as `department,name,salary,row_num`, sorted first by **department alphabetically**, then by **row_num ascending**.

This simulates:
```sql
SELECT department, name, salary,
       ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS row_num
FROM   dbo.employees
ORDER BY department, row_num;
```

## Input Format

- Line 1: integer `N` — the number of employee records
- Next `N` lines: `department,name,salary` (salary is a non-negative integer)

## Output Format

One line per employee: `department,name,salary,row_num`, sorted by department alphabetically then by row_num ascending.

## Constraints

- `1 <= N <= 1000`
- Department names contain no commas
- Employee names contain no commas
- Salaries are non-negative integers
- At least one department is guaranteed

## Example

**Input:**
```
6
Eng,Alice,90000
Eng,Bob,75000
Eng,Carol,85000
HR,Dave,60000
HR,Eve,65000
HR,Frank,60000
```

**Output:**
```
Eng,Alice,90000,1
Eng,Carol,85000,2
Eng,Bob,75000,3
HR,Eve,65000,1
HR,Dave,60000,2
HR,Frank,60000,3
```

Within Eng: Alice (90000) = row 1, Carol (85000) = row 2, Bob (75000) = row 3.
Within HR: Eve (65000) = row 1, Dave and Frank both have 60000 — Dave appears first in input so Dave = row 2, Frank = row 3.
