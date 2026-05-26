# k-Nearest Neighbors and Decision Trees

Two foundational supervised learning algorithms: k-NN makes predictions by looking up similar examples; decision trees learn a hierarchy of yes/no questions. Both are highly interpretable and work well across many domains with no tuning.

## k-Nearest Neighbors (k-NN)

k-NN is arguably the simplest conceptually correct ML algorithm. It stores the entire training set and at prediction time finds the `k` most similar training examples to the query.

### Algorithm

1. Compute the distance from query `q` to every training point.
2. Find the `k` closest training points.
3. **Classification**: return the majority class label among the k neighbors.
4. **Regression**: return the average label value among the k neighbors.

That's it. No "training" in the traditional sense — k-NN is a **lazy learner**.

### Distance Metrics

**Euclidean distance** (L2 norm):
```
d(a, b) = sqrt((a₁−b₁)² + (a₂−b₂)² + ... + (aₙ−bₙ)²)
```

**Manhattan distance** (L1 norm):
```
d(a, b) = |a₁−b₁| + |a₂−b₂| + ... + |aₙ−bₙ|
```

**Cosine similarity** (for text/embeddings):
```
cos(a, b) = (a·b) / (||a|| · ||b||)
```
Measures angle between vectors, ignoring magnitude. Two documents that use the same words proportionally have high cosine similarity even if one is much longer.

### Worked Example (k=3)

Training set:
- A = (1, 2), label=0
- B = (3, 4), label=1
- C = (1, 3), label=0
- D = (4, 1), label=1

Query point Q = (2, 2), k=3.

Computing Euclidean distances from Q:
- d(Q, A) = √((2−1)² + (2−2)²) = √(1+0) = **1.00**
- d(Q, C) = √((2−1)² + (2−3)²) = √(1+1) = **1.41**
- d(Q, B) = √((2−3)² + (2−4)²) = √(1+4) = **2.24**
- d(Q, D) = √((2−4)² + (2−1)²) = √(4+1) = **2.24**

Sorted: A(1.00), C(1.41), B(2.24), D(2.24). Three nearest: **A(label=0), C(label=0), B(label=1)**.

Vote: class 0 has 2 votes, class 1 has 1 vote. **Predicted label: 0**.

### Effect of k

| k value | Bias | Variance | Boundary | Risk |
|---|---|---|---|---|
| k=1 | Very low | Very high | Jagged, noisy | Overfitting |
| k=3 to 7 | Low | Moderate | Smooth | Good starting point |
| k=n (all points) | Very high | Zero | Always predicts majority class | Underfitting |

Best k is found via cross-validation. Typically odd numbers are used for classification to avoid ties.

### Limitations

- **Slow at prediction**: O(n·d) per query where n = training examples, d = features. A 1M-point dataset requires 1M distance computations per prediction. Can be improved with KD-trees (O(log n) for low dimensions) or approximate nearest neighbor structures (HNSW, FAISS for embeddings).
- **Memory-heavy**: stores the entire training set.
- **Curse of dimensionality**: in high dimensions, all points become roughly equidistant. With 100 features, the "nearest" neighbor might be almost as far away as the "farthest." Feature selection or dimensionality reduction is essential before applying k-NN to high-dimensional data.
- **Feature scaling matters**: if one feature ranges 0–1000 and another 0–1, the large-scale feature dominates the distance. Always standardize features (subtract mean, divide by std) before k-NN.

## Decision Trees

A decision tree asks a sequence of yes/no questions to classify an example. Each internal node is a **feature split** (a threshold test on one feature); each **leaf** is a predicted class or value.

### Example Tree (Predicting loan default)

```
Annual Income > $50k?
├── Yes → Credit score > 700?
│         ├── Yes → Predict: No Default (leaf)
│         └── No  → Predict: Default (leaf)
└── No  → Predict: Default (leaf)
```

This tree is fully interpretable: a loan officer can follow the same logic manually.

### Splitting Criteria: Entropy and Gini Impurity

At each node, the algorithm finds the feature and threshold that best **separates** the classes. Two standard measures of impurity:

**Entropy** (from information theory):
```
H(S) = −Σ pᵢ · log₂(pᵢ)
```
H=0 for a pure node (all one class). H=1 for a perfectly mixed binary node (50/50 split).

**Gini impurity**:
```
G(S) = 1 − Σ pᵢ²
```
G=0 for a pure node. G=0.5 for a 50/50 binary node.

**Information gain** = entropy before split − weighted entropy after split.

### Worked Example: Computing a Split

Dataset (5 examples, binary label):

| Feature x | Label y |
|---|---|
| 1 | 0 |
| 2 | 0 |
| 3 | 1 |
| 4 | 1 |
| 5 | 1 |

**Parent entropy** (3 class-1, 2 class-0 out of 5):
```
p₀ = 2/5 = 0.4,  p₁ = 3/5 = 0.6
H(parent) = −0.4·log₂(0.4) − 0.6·log₂(0.6)
          = −0.4·(−1.322) − 0.6·(−0.737)
          = 0.529 + 0.442 = 0.971
```

**Split at x ≥ 3** (left: {1,2} → all class 0; right: {3,4,5} → all class 1):
```
H(left)  = −1·log₂(1) = 0      (pure node)
H(right) = −1·log₂(1) = 0      (pure node)
Weighted H = (2/5)·0 + (3/5)·0 = 0
Information gain = 0.971 − 0 = 0.971   (maximum possible!)
```

**Split at x ≥ 2** (left: {1} → class 0; right: {2,3,4,5} → 1 class-0, 3 class-1):
```
H(left)  = 0    (pure)
H(right): p₀=1/4=0.25, p₁=3/4=0.75
H(right) = −0.25·log₂(0.25) − 0.75·log₂(0.75)
         = −0.25·(−2) − 0.75·(−0.415) = 0.5 + 0.311 = 0.811
Weighted H = (1/5)·0 + (4/5)·0.811 = 0.649
Information gain = 0.971 − 0.649 = 0.322
```

The split at x≥3 gives higher information gain (0.971 vs 0.322), so the tree algorithm chooses it. After this split, both children are pure — training is complete.

### Overfitting in Trees

A fully grown tree memorizes the training data: every leaf contains exactly one training example. This achieves zero training error but is highly sensitive to noise — one outlier creates an entire branch for itself.

**Strategies to control overfitting**:
- **Maximum depth**: stop splitting when depth reaches `d`.
- **Minimum samples per leaf**: don't split if fewer than `k` examples reach this node.
- **Pruning**: grow the full tree, then remove subtrees that don't improve validation performance.

### Random Forests: Ensemble of Trees

Individual decision trees have high variance — small changes in training data produce very different trees. A **random forest** fixes this by:

1. Drawing `B` bootstrap samples (sample n examples with replacement) from the training data.
2. Training one decision tree on each bootstrap sample. At each split, only a **random subset of features** (typically √d features for classification) is considered.
3. At prediction time, aggregate all trees' predictions: majority vote (classification) or mean (regression).

Why it works: individual trees are *diverse* because of random feature subsets. Diverse errors cancel out when averaged.

Random forests are often among the strongest out-of-the-box classifiers for tabular data, require minimal hyperparameter tuning, and naturally provide feature importance scores.

## Comparison

| Property | k-NN | Decision Tree | Random Forest |
|---|---|---|---|
| Training time | O(1) (store data) | O(n·d·log n) | O(B·n·d·log n) |
| Prediction time | O(n·d) | O(depth) | O(B·depth) |
| Interpretable? | Moderate | Very (draw the tree) | No (many trees) |
| Handles non-linear boundaries? | Yes (any shape) | Yes (axis-aligned) | Yes |
| Feature scaling needed? | Yes (critical) | No | No |
| Handles missing values? | Needs imputation | Yes (surrogate splits) | Yes |
