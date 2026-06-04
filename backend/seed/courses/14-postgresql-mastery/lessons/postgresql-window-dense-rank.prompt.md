# Window Function: Dense Rank by Salary

PostgreSQL's `DENSE_RANK()` window function assigns a rank to each row within a partition. Unlike `RANK()`, `DENSE_RANK()` never leaves gaps: if two employees tie at rank 1, the next rank is 2 (not 3).

## Problem

You are given a list of employees with their department and salary. Simulate the SQL `DENSE_RANK()` window function: for each department, assign a rank to each employee based on their salary in **descending** order. Employees with the same salary in the same department share the same rank, and the next rank is not skipped (dense ranking).

## Input Format

- First line: integer `N` (number of employees)
- Next `N` lines: `name department salary` (space-separated)

## Output Format

For each employee, print: `name department salary dense_rank`

Sort output by **department** (alphabetically), then by **rank ascending**, then by **name ascending** for ties.

## Example

**Input:**
```
6
Alice Engineering 90000
Bob Engineering 90000
Carol Engineering 80000
Dave Sales 70000
Eve Sales 70000
Frank Sales 60000
```

**Output:**
```
Alice Engineering 90000 1
Bob Engineering 90000 1
Carol Engineering 80000 2
Dave Sales 70000 1
Eve Sales 70000 1
Frank Sales 60000 2
```

## Constraints

- `1 <= N <= 500`
- Department names and employee names contain no spaces
- Salaries are positive integers
- There is at least one employee per department

## Notes

In SQL, this corresponds to:

```sql
SELECT name, department, salary,
       DENSE_RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS dense_rank
FROM employees
ORDER BY department, dense_rank, name;
```
