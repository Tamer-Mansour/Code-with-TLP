# Rotate Array

Given a list of integers and a non-negative integer `k`, rotate the array to the right by `k` steps **in place** and print the result.

Rotating right by 1 step means the last element moves to the front:
`[1, 2, 3, 4, 5]` rotated right by 2 becomes `[4, 5, 1, 2, 3]`.

## Input Format

- Line 1: two integers `n` and `k` separated by a space — the number of elements and the rotation amount.
- Line 2: `n` integers separated by spaces representing the array.

## Output Format

Print the rotated array as space-separated integers on a single line.

## Constraints

- `1 <= n <= 1000`
- `0 <= k <= 10000`

## Examples

**Example 1**
```
Input:
5 2
1 2 3 4 5

Output:
4 5 1 2 3
```

**Example 2**
```
Input:
3 0
7 8 9

Output:
7 8 9
```
