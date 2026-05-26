# Exercise: Cosine Similarity

Cosine similarity measures the angle between two vectors rather than their magnitude. It is the foundation of text similarity, nearest-neighbor search in embedding spaces, and recommendation systems.

## Background

```
cosine_similarity(a, b) = (a · b) / (||a|| * ||b||)
```

Where:
- `a · b = sum(ai * bi)` is the dot product
- `||a|| = sqrt(sum(ai^2))` is the L2 norm (Euclidean magnitude)

The result ranges from -1 (perfectly opposite) through 0 (orthogonal, no shared direction) to +1 (identical direction).

## Task

Given two vectors, compute their cosine similarity rounded to 4 decimal places. If either vector is the zero vector (all zeros), output `0.0000`.
