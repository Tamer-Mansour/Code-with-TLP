# K-Means Clustering (1D)

Implement the **K-Means clustering algorithm** in one dimension. Run up to **100 iterations** (or until centroids stop moving). Initialize centroids as the **first K data points** in input order.

Print the final centroid positions sorted **ascending**, one per line, each rounded to 4 decimal places.

## Input Format

```
N K
x₁ x₂ x₃ ... xₙ
```

- Line 1: two integers N (number of points) and K (number of clusters)
- Line 2: N space-separated floats

## Output Format

K lines, each containing one centroid value rounded to 4 decimal places, sorted ascending.

## Example

**Input:**
```
6 2
1.0 1.5 1.2 9.0 8.5 9.5
```

**Output:**
```
1.2333
9.0000
```

## Algorithm

```
centroids = first K points
repeat up to 100 times:
    assign each point to nearest centroid (by absolute distance)
    recompute each centroid as mean of its cluster
    if centroids unchanged: break
print sorted centroids
```

If a cluster becomes empty during an iteration, keep its centroid unchanged.

## Notes

- Use only the Python standard library.
- Ties in distance: assign to the lower-indexed centroid.
- Sort the output centroids ascending before printing.
