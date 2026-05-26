# Exercise: k-Means One Iteration

The k-Means algorithm alternates between assigning points to the nearest centroid and moving each centroid to the mean of its assigned points. In this exercise you will implement one complete assign-then-update iteration.

## Background

**Assign step**: for each data point, find the centroid with the smallest Euclidean distance and assign the point to that cluster. If a point is equidistant from two centroids, assign it to the lower-indexed centroid.

**Update step**: move each centroid to the mean (x, y) of all points currently assigned to it. If a centroid has no assigned points, it stays at its current position.

## Task

Given k initial centroids and n data points (all 2D), perform one assign-update iteration and print the new centroids.
