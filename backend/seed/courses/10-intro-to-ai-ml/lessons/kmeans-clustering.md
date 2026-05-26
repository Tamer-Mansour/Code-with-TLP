# k-Means Clustering

k-Means is the most widely used clustering algorithm. Given a set of unlabeled points and a number `k`, it partitions the data into `k` groups (clusters) such that each point belongs to the cluster with the nearest centroid. The algorithm is iterative, deterministic given initial centroids, and surprisingly effective.

## The Algorithm

k-Means alternates between two steps until convergence:

**Step 1 — Assign**: assign each point to the cluster whose centroid is nearest (Euclidean distance).

**Step 2 — Update**: recompute each centroid as the mean of all points currently assigned to it.

**Repeat** until no point changes its cluster assignment (convergence), or a maximum number of iterations is reached.

```
Initialize k centroids (randomly or with k-means++)
repeat:
    for each point x in the dataset:
        assign x to the cluster i with nearest centroid μᵢ
    for each cluster i:
        μᵢ ← mean of all points assigned to cluster i
until assignments do not change
```

k-Means always converges (the objective — total within-cluster sum of squares — decreases or stays the same at every step), but it may converge to a local minimum, not the global optimum.

## Detailed Worked Example

Points: A=(1,1), B=(1,2), C=(4,4), D=(4,5). k=2, initialized with centroids μ₁=(1,1) and μ₂=(4,4).

### Iteration 1 — Assign

Distance from each point to each centroid:

| Point | d to μ₁=(1,1) | d to μ₂=(4,4) | Assigned to |
|---|---|---|---|
| A=(1,1) | 0 | √18 ≈ 4.24 | Cluster 1 |
| B=(1,2) | 1 | √13 ≈ 3.61 | Cluster 1 |
| C=(4,4) | √18 ≈ 4.24 | 0 | Cluster 2 |
| D=(4,5) | √25 = 5 | 1 | Cluster 2 |

Cluster 1: {A, B}. Cluster 2: {C, D}.

### Iteration 1 — Update

```
μ₁ = mean of {(1,1), (1,2)} = ((1+1)/2, (1+2)/2) = (1, 1.5)
μ₂ = mean of {(4,4), (4,5)} = ((4+4)/2, (4+5)/2) = (4, 4.5)
```

### Iteration 2 — Assign (with updated centroids)

| Point | d to μ₁=(1,1.5) | d to μ₂=(4,4.5) | Assigned to |
|---|---|---|---|
| A=(1,1) | 0.5 | √(9+12.25)=√21.25≈4.61 | Cluster 1 |
| B=(1,2) | 0.5 | √(9+6.25)=√15.25≈3.91 | Cluster 1 |
| C=(4,4) | √(9+6.25)≈3.91 | 0.5 | Cluster 2 |
| D=(4,5) | √(9+12.25)≈4.61 | 0.5 | Cluster 2 |

**Same assignments as before → convergence!**

**Final clusters**: Cluster 1 = {A=(1,1), B=(1,2)}, Cluster 2 = {C=(4,4), D=(4,5)}.
**Final centroids**: μ₁ = (1, 1.5), μ₂ = (4, 4.5).

## What k-Means Actually Optimizes

k-Means minimizes the **Within-Cluster Sum of Squares (WCSS)**, also called inertia:

```
WCSS = Σᵢ Σ_{x ∈ Cᵢ} ||x − μᵢ||²
```

For our example after convergence:
- Cluster 1: ||(1,1)−(1,1.5)||² + ||(1,2)−(1,1.5)||² = 0.25 + 0.25 = 0.5
- Cluster 2: ||(4,4)−(4,4.5)||² + ||(4,5)−(4,4.5)||² = 0.25 + 0.25 = 0.5
- **Total WCSS = 1.0**

Every iteration of k-Means either decreases WCSS or keeps it the same. Since there are finitely many assignments, the algorithm must terminate.

## Choosing k: The Elbow Method

k-Means requires you to specify `k` in advance. The elbow method:

1. Run k-Means for k = 1, 2, 3, ..., 10.
2. Plot WCSS vs. k.
3. Look for the "elbow" — the k where adding one more cluster yields diminishing WCSS reduction.

```
WCSS
 |
 |*
 | *
 |  **
 |    **
 |       ***
 |           ****
 |___________________________
   1  2  3  4  5  6  7  8    k
```

In this plot, the elbow is around k=3 or k=4. Beyond that, adding clusters doesn't reduce WCSS much. There is no universal rule — the elbow is a *guideline*, and domain knowledge should confirm the choice.

**Other k-selection methods**:
- **Silhouette score**: measures how well each point fits its cluster vs. the nearest other cluster. Range: −1 to +1. Higher is better.
- **Gap statistic**: compares WCSS to a null reference distribution.
- **Domain knowledge**: often you know roughly how many groups to expect.

## Sensitivity to Initialization

k-Means can converge to different local minima depending on initial centroids. Example with k=2 and two natural clusters at (0,0) and (10,0):

- Good init: μ₁=(1,0), μ₂=(9,0) → converges to correct clustering.
- Bad init: μ₁=(0,0), μ₂=(0,1) → may converge to an unnatural clustering.

**k-Means++ initialization** (Arthur & Vassilvitskii, 2007) dramatically improves results:
1. Choose the first centroid uniformly at random.
2. For each subsequent centroid, choose each point with probability proportional to its squared distance from the nearest already-chosen centroid.
3. Repeat until k centroids are chosen.

This spreads initial centroids across the space, greatly reducing bad local minima.

## Limitations

| Limitation | Detail |
|---|---|
| Requires k in advance | Must guess or use heuristics like the elbow method |
| Sensitive to initialization | k-means++ mitigates but doesn't eliminate this |
| Assumes spherical clusters | Fails on elongated, ring-shaped, or oddly-shaped clusters |
| Sensitive to outliers | One outlier can pull a centroid far from its cluster |
| Euclidean distance only | Standard version doesn't handle categorical features natively |
| Scales poorly to very high dimensions | Distance becomes uninformative in high-D spaces |

## Applications

- **Customer segmentation**: group users by purchase behavior to target marketing.
- **Image compression**: quantize the 2^24 possible RGB colors down to k representative colors — a 256-color image uses only 1 byte per pixel instead of 3.
- **Document clustering**: group news articles by topic without labeled data.
- **Anomaly detection**: points far from every centroid are likely anomalies.
- **Pre-processing**: use cluster IDs as features for downstream supervised learning.
- **Vector quantization**: compress embedding spaces in LLMs and image models.
