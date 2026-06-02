# Exercise: String Aggregation Simulation

In SQL Server you would use `STRING_AGG` to collapse multiple rows into a comma-separated list. In this exercise you simulate that behavior in Python, reinforcing the concept.

Given a list of `(group, value)` pairs, produce one line per group showing the group name followed by its values joined with `, ` (comma-space), sorted alphabetically by value. Groups appear in the order of their first occurrence in the input.

## Input Format

- Line 1: integer `n` — number of pairs.
- Next `n` lines: `group,value` (no spaces around the comma).

## Output Format

One line per group: `group: value1, value2, ...` (values sorted alphabetically ascending).

## Example

Input:
```
5
fruits,banana
vegs,carrot
fruits,apple
vegs,broccoli
fruits,cherry
```

Output:
```
fruits: apple, banana, cherry
vegs: broccoli, carrot
```
