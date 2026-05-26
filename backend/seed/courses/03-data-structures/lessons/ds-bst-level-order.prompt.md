# BST Level-Order Traversal

Insert N integers (all distinct) into a Binary Search Tree in the given order, then print a **level-order (BFS) traversal** — one level per output line, values on each level separated by spaces.

## Input Format

```
N
v1 v2 ... vN
```

- Line 1: integer N (1 ≤ N ≤ 1000) — number of values to insert.
- Line 2: N space-separated distinct integers.

## Output Format

One line per level of the BST (from root level down), with values in left-to-right order, space-separated.

## Example

Input:
```
7
5 3 7 1 4 6 8
```

The BST looks like:
```
       5
      / \
     3   7
    / \ / \
   1  4 6  8
```

Output:
```
5
3 7
1 4 6 8
```

## Notes

- Insert values in the given order (duplicates will not appear in the input).
- Use standard BST insertion rules: values less than the root go left, greater go right.
