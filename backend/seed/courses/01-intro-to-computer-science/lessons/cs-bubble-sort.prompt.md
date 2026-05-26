# Bubble Sort

Write a program that sorts a list of integers using the bubble sort algorithm and prints each step.

Each test case is a single line of space-separated integers. For each test case, output the list after each complete pass that made at least one swap. After all passes are done (the list is sorted), print the final sorted list on its own line prefixed with `sorted:`.

If the input is already sorted (zero swaps on the first pass), just print `sorted:` followed by the list.

## Input format

Each line contains a space-separated list of integers to sort. Process until EOF.

## Output format

For each pass that performed at least one swap, print the intermediate state as space-separated integers on one line.
After sorting is complete, print `sorted:` followed by the sorted list (space-separated).

## Example

**Input:**
```
5 3 8 1 4
1 2 3
```

**Output:**
```
3 5 1 4 8
3 1 4 5 8
1 3 4 5 8
sorted: 1 3 4 5 8
sorted: 1 2 3
```
