# k-Means One Iteration

Given k initial 2D centroids and n 2D data points, perform **one** complete assign-then-update iteration of k-Means and output the resulting centroids.

**Input**:
- Line 1: two integers `k n` (number of clusters, number of points)
- Next k lines: two integers `cx cy` (initial centroid coordinates)
- Next n lines: two integers `px py` (data point coordinates)

**Output**: k lines, each `cx cy` rounded to exactly **4 decimal places**, one centroid per line in order of cluster index.

**Rules**:
- Use Euclidean distance: `d = sqrt((px-cx)^2 + (py-cy)^2)`
- Ties (equidistant from two centroids): assign to the **lower-indexed** centroid.
- If a centroid ends up with no assigned points, its position does not change.

**Example**

Input:
```
2 4
1 1
4 4
1 1
1 2
4 4
4 5
```

Output:
```
1.0000 1.5000
4.0000 4.5000
```

Explanation: (1,1) and (1,2) are closer to centroid 0=(1,1); (4,4) and (4,5) are closer to centroid 1=(4,4). New centroid 0 = mean of {(1,1),(1,2)} = (1.0, 1.5). New centroid 1 = mean of {(4,4),(4,5)} = (4.0, 4.5).
