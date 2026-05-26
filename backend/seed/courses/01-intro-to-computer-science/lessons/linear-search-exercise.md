# Exercise: Linear Search

Practice the linear search algorithm by implementing a program that searches a list of integers.

## What you need to do

Read pairs of lines from standard input until EOF:
1. First line: a space-separated list of integers
2. Second line: the target integer to search for

For each pair, print the **0-based index** of the **first** occurrence of the target in the list. If the target is not found, print `-1`.

## Example

**Input:**
```
3 1 4 1 5 9 7 6
7
10 20 30 40 50
25
5 5 5 5
5
```

**Output:**
```
6
-1
0
```

## Notes

- Return the index of the **first** occurrence (in case of duplicates).
- If the list has one element and it matches the target, output `0`.
- Linear search checks elements from left to right; it does not require a sorted list.
