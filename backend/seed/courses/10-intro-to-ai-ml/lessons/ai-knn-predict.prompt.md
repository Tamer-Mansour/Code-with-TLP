# 1-Nearest Neighbor Prediction

You are given `N` labeled 2D training points and a single query point `Q`. Find the training point nearest to `Q` by Euclidean distance and output its label.

Euclidean distance between (x1, y1) and (x2, y2):
```
d = sqrt((x1-x2)^2 + (y1-y2)^2)
```

If two points are equally close, choose the one that appears **first** in the input.

## Input Format

```
N
x1 y1 label1
x2 y2 label2
...
qx qy
```

- First line: integer `N`.
- Next `N` lines: integer coordinates and an integer label (0 or 1).
- Last line: integer coordinates of the query point.

## Output Format

A single integer: the label of the nearest training point.

## Examples

**Example 1**
```
Input:
3
0 0 0
5 5 1
1 1 0
3 3

Output:
1
```
Distances from (3,3): to (0,0) = sqrt(18) ≈ 4.24, to (5,5) = sqrt(8) ≈ 2.83, to (1,1) = sqrt(8) ≈ 2.83. First nearest among ties is (5,5) with label 1.

**Example 2**
```
Input:
4
0 0 1
10 0 0
0 10 0
10 10 1
1 1

Output:
1
```
Nearest to (1,1) is (0,0) with label 1.

**Example 3**
```
Input:
2
3 4 0
6 8 1
0 0

Output:
0
```
d to (3,4) = 5, d to (6,8) = 10. Nearest is (3,4) label 0.
