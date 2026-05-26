# Cosine Similarity

Compute the cosine similarity between two vectors.

**Input**:
- Line 1: integer `d` (dimensionality of both vectors)
- Line 2: `d` space-separated integers: components of vector `a`
- Line 3: `d` space-separated integers: components of vector `b`

**Output**: one line — the cosine similarity rounded to exactly **4 decimal places**.

Formula:
```
cosine_similarity(a, b) = dot(a, b) / (norm(a) * norm(b))
```
where `dot(a, b) = sum(a[i]*b[i])` and `norm(v) = sqrt(sum(v[i]^2))`.

If either vector is the zero vector (all components are 0), output `0.0000`.

Use `math.sqrt` from the standard library — no numpy allowed.

**Example**

Input:
```
3
1 2 3
1 2 3
```

Output:
```
1.0000
```

Explanation: identical vectors have cosine similarity = 1.0 (angle = 0°).

**Another example**

Input:
```
2
1 0
0 1
```

Output:
```
0.0000
```

Explanation: perpendicular vectors have cosine similarity = 0 (angle = 90°).
