# Exercise: Merge Sort Implementation

Implement the merge sort algorithm from scratch and use it to sort a sequence of integers.

## What You'll Practice

- Divide-and-conquer decomposition
- Writing a correct merge step that preserves sorted order
- O(n log n) guaranteed sorting in all cases

## Instructions

Read N integers and sort them in ascending order using your own merge sort implementation. Print the sorted array on a single line, values separated by spaces.

## Input Format

- Line 1: N (number of integers)
- Line 2: N space-separated integers

## Output Format

N integers in ascending order, space-separated on a single line.

## Example

```
Input:
6
5 3 8 1 9 2

Output:
1 2 3 5 8 9
```

## Hint

Split the array at the midpoint, recursively sort each half, then merge the two sorted halves by repeatedly taking the smaller front element.
