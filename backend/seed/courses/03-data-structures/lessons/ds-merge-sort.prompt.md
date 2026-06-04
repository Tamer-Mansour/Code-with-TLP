# Merge Sort

Implement the merge sort algorithm and sort a sequence of integers in ascending order.

## Input Format

- Line 1: N — number of integers (1 ≤ N ≤ 100000)
- Line 2: N space-separated integers (−10⁹ ≤ each value ≤ 10⁹)

## Output Format

Print the sorted integers on a single line, separated by spaces.

## Example

**Input:**
```
6
5 3 8 1 9 2
```

**Output:**
```
1 2 3 5 8 9
```

## Requirements

- Implement merge sort yourself (do not use Python's built-in `sort` or `sorted`)
- Your solution must have O(n log n) time complexity in the worst case

## Hint

```
merge_sort([5, 3, 8, 1, 9, 2])
  ↓ divide
merge_sort([5, 3, 8])  +  merge_sort([1, 9, 2])
  ↓                           ↓
[3, 5, 8]              [1, 2, 9]
  ↓ merge
[1, 2, 3, 5, 8, 9]
```
