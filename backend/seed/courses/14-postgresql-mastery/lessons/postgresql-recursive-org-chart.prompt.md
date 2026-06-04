# CTE Chain: Recursive Org Chart Depth

PostgreSQL recursive CTEs are used to traverse hierarchical data such as org charts or category trees. The `WITH RECURSIVE` clause lets you define a query that repeatedly evaluates itself until it produces no new rows.

## Problem

You are given a list of employee-manager pairs. Using recursive CTE logic, compute the depth of each employee in the hierarchy (the CEO/root has depth 0). Employees with no manager listed are roots.

## Input Format

- First line: integer `N` (number of employees)
- Next `N` lines: `employee_id manager_id` (use `0` for no manager)

## Output Format

For each employee in **ascending order of employee_id**, print: `employee_id depth`

## Example

**Input:**
```
6
1 0
2 1
3 1
4 2
5 2
6 3
```

**Output:**
```
1 0
2 1
3 1
4 2
5 2
6 2
```

## Constraints

- `1 <= N <= 1000`
- Employee IDs are positive integers
- Manager ID of `0` means no manager (root node)
- The hierarchy is a valid tree (no cycles)
- There may be multiple root nodes

## Notes

This simulates how PostgreSQL's `WITH RECURSIVE` CTE traverses a hierarchy: the anchor query selects root nodes (employees with no manager), then the recursive term repeatedly joins to find children until no new rows are produced.
