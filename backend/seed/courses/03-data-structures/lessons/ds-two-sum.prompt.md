# Two-Sum with Hash Table

Given an array of N integers and a target T, find all **unique pairs of indices** (i, j) with i < j such that `arr[i] + arr[j] == T`.

Output the pairs sorted by i ascending, then by j ascending. Each pair on its own line as `i j`.

If no such pair exists, print `NONE`.

## Input Format

```
N T
a1 a2 ... aN
```

- Line 1: integers N (2 ≤ N ≤ 100000) and T (any integer).
- Line 2: N space-separated integers.

## Output Format

One pair `i j` per line (0-indexed), sorted by i then j.
If no pair found, print `NONE`.

## Examples

Input:
```
6 9
2 7 11 15 2 7
```
Output:
```
0 1
0 5
1 4
4 5
```
(arr[0]+arr[1]=2+7=9, arr[0]+arr[5]=2+7=9, arr[1]+arr[4]=7+2=9, arr[4]+arr[5]=2+7=9)

Input:
```
4 100
1 2 3 4
```
Output:
```
NONE
```

## Notes

- The array may contain duplicates.
- Each element may be part of multiple valid pairs.
- Indices are 0-based.
