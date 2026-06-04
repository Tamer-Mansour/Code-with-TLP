# Exercise: K-Means Clustering (1D)

Implement the **K-Means clustering algorithm** to full convergence in one dimension.

## Background

K-Means partitions N data points into K clusters by iterating two steps until convergence:

**Assignment step**: assign each point to its nearest centroid.
```
cluster(xᵢ) = argmin_k |xᵢ − cₖ|
```

**Update step**: recompute each centroid as the mean of its assigned points.
```
cₖ = mean({xᵢ : cluster(xᵢ) = k})
```

Repeat until no centroid changes (or for up to 100 iterations).

## Initialization

Initialize the K centroids to the **first K data points** in input order.

## Your Task

Given N data points and K, run K-Means to convergence and print the final centroid positions sorted in **ascending order**, each rounded to 4 decimal places.

## Example

With 6 points in two natural clusters:
- Group 1: 1.0, 1.5, 1.2 → mean ≈ 1.2333
- Group 2: 9.0, 8.5, 9.5 → mean = 9.0000

After convergence the centroids are `1.2333` and `9.0000`.

## Key Concepts Practiced

- The assign-update loop of K-Means
- Convergence detection (centroids stop moving)
- Sensitivity to initialization
- 1D clustering as a foundation for understanding higher-dimensional variants
