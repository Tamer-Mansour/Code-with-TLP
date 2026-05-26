# Dimensionality Reduction

Real-world datasets often have hundreds or thousands of features. Dimensionality reduction compresses data into fewer dimensions while preserving the most important structure. This makes data easier to visualize, store, and model — and often improves downstream ML performance by removing noise.

## Why High Dimensions Are Problematic

The **curse of dimensionality** refers to a cluster of related phenomena that make high-dimensional spaces counterintuitive and computationally hostile:

**Distances become meaningless.** In 2D, points can be "close" or "far." In 1000 dimensions, all pairwise distances converge to nearly the same value. Formally, as d → ∞, the ratio max_distance/min_distance → 1. A k-NN classifier in 1000 dimensions is essentially picking neighbors at random.

**Data becomes exponentially sparse.** To maintain the same data density in d dimensions as in 1 dimension, you need n^d data points. With 100 features and 1000 training examples, the data covers an astronomically small fraction of the input space.

**Visualization becomes impossible.** Humans perceive only 3 dimensions. Any dataset with more than 3 features requires dimensional reduction before you can visually explore it.

## Principal Component Analysis (PCA)

PCA is the most widely used linear dimensionality reduction technique. It finds the directions of **maximum variance** in the data and projects onto those directions.

### Algorithm

1. **Center the data**: subtract the mean from each feature so the data is centered at the origin.
2. **Compute the covariance matrix**: Σ = (1/n)·XᵀX (where X is the centered data matrix).
3. **Eigendecompose Σ**: find eigenvalues λ₁ ≥ λ₂ ≥ ... ≥ λ_d and corresponding eigenvectors (the **principal components**).
4. **Select top k eigenvectors**: the first k eigenvectors capture the most variance.
5. **Project**: multiply the data by the k×d projection matrix.

Eigenvalue λᵢ = variance explained by principal component i.
**Proportion of variance explained by PCᵢ** = λᵢ / Σλⱼ.

### Worked Example: 2D → 1D

Points (2D): (1,2), (2,4), (3,6), (4,8).

Observe: all points lie exactly on the line y = 2x. PCA should find the direction (1, 2)/√5 as PC1 (along the line) and (2, −1)/√5 as PC2 (perpendicular to the line).

After centering: mean = (2.5, 5), centered points: (−1.5, −3), (−0.5, −1), (0.5, 1), (1.5, 3).

Projecting onto PC1 = (1/√5, 2/√5):
- (−1.5, −3) · (1/√5, 2/√5) = (−1.5 + (−6))/√5 = −7.5/√5 ≈ −3.35
- (−0.5, −1) · (1/√5, 2/√5) = (−0.5 − 2)/√5 = −2.5/√5 ≈ −1.12
- (0.5, 1) · (1/√5, 2/√5) = (0.5 + 2)/√5 = 2.5/√5 ≈ 1.12
- (1.5, 3) · (1/√5, 2/√5) = (1.5 + 6)/√5 = 7.5/√5 ≈ 3.35

**Variance along PC1**: all four points are spaced evenly. The 2D data is perfectly captured in 1D with *zero information loss* because the data was exactly 1D (all on a line).

Projecting onto PC2 (perpendicular direction): all four points project to 0. PC2 explains *zero variance* — nothing is lost by discarding it.

### Explained Variance Ratio

Choose k by plotting cumulative explained variance:

```
Components | Cumulative variance explained
     1     |   85%
     2     |   95%    ← elbow: 2 components capture 95%
     3     |   98%
     4     |   99%
     5     |  100%
```

A common rule: keep enough components to explain 90–95% of total variance. Discarding the last 5–10% usually just removes noise.

### What PCA Preserves and Loses

| Preserves | Loses |
|---|---|
| Global structure (far-apart points stay far) | Non-linear relationships |
| Variance (most important directions) | Some distance information |
| Linear correlations | Local cluster structure (partially) |

## t-SNE

**t-SNE** (t-distributed Stochastic Neighbor Embedding, van der Maaten & Hinton, 2008) is a non-linear dimensionality reduction method primarily used for **visualization**.

### Key Idea

t-SNE models the *similarity* between points as probabilities:
1. In the high-dimensional space, place a Gaussian over each point. Define pᵢⱼ = probability that point i "picks" point j as a neighbor.
2. In the 2D output space, use a **t-distribution** (heavier tails than Gaussian) to define similar probabilities qᵢⱼ.
3. Minimize the KL divergence between the P and Q distributions using gradient descent.

The t-distribution in the output space prevents the "crowding problem" — many points trying to fit near the center — by spreading nearby clusters apart.

### t-SNE vs. PCA

| Property | PCA | t-SNE |
|---|---|---|
| Type | Linear | Non-linear |
| Preserves | Global variance | Local neighborhoods |
| Output | Interpretable (principal components) | Only useful for visualization |
| Reproducible? | Yes | No (random initialization) |
| Speed | Fast | Slow for large datasets |
| Can do k>2 dimensions? | Yes | Theoretically yes, but rarely used above 3D |

**When to use t-SNE**: exploring cluster structure in high-dimensional data (embeddings, gene expression, image features). You'll see tight islands of similar items.

**When NOT to use t-SNE**: as input to a downstream classifier (distances in t-SNE space are not meaningful for generalization), or when you need a reproducible result.

## UMAP

**UMAP** (Uniform Manifold Approximation and Projection, McInnes et al., 2018) is a newer non-linear method that is faster than t-SNE and better preserves global structure. It is increasingly preferred over t-SNE for large datasets. Like t-SNE, it is primarily for visualization and exploration.

## Autoencoders (Neural Dimensionality Reduction)

A neural network **autoencoder** learns a compressed representation (the **latent code** or **bottleneck**) by training to reconstruct its input:

```
Input x → Encoder → Latent code z (low-dim) → Decoder → Reconstruction x̂
Loss = ||x − x̂||²
```

The encoder learns the compression; the decoder learns reconstruction. After training, the encoder alone is used for dimensionality reduction. Unlike PCA, autoencoders can capture **non-linear structure** in the data because the encoder and decoder are neural networks.

Variational autoencoders (VAEs) additionally impose a probabilistic prior on z, enabling generative use (sampling new examples from the learned distribution).

## Choosing a Method

| Use case | Recommended method |
|---|---|
| Pre-processing before k-NN, SVM, linear models | PCA (fast, reproducible, linear) |
| Visualizing high-dimensional clusters | t-SNE or UMAP |
| Non-linear compression for downstream ML | Autoencoder |
| Noise removal from data | PCA (discard low-variance components) |
| Very large datasets (millions of points) | UMAP or incremental PCA |
| Need interpretable components | PCA (components are linear combinations of features) |
