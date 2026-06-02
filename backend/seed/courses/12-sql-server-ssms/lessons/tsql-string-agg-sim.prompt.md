# String Aggregation Simulation

You are simulating SQL Server's `STRING_AGG` function.

**Input:**
- Line 1: integer `n`.
- Next `n` lines: `group,value` pairs (one comma, no spaces).

**Output:**
One line per group in order of first appearance:
```
group: value1, value2, ...
```
Values within each group are sorted alphabetically ascending.

**Example input:**
```
5
fruits,banana
vegs,carrot
fruits,apple
vegs,broccoli
fruits,cherry
```

**Expected output:**
```
fruits: apple, banana, cherry
vegs: broccoli, carrot
```
