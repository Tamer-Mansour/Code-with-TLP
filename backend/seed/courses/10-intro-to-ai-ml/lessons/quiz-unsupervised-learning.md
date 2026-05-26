# Quiz: Unsupervised Learning

**Q1. What does the k-Means algorithm require you to specify before running?**
- [ ] The learning rate used to update centroids.
- [x] The number of clusters k.
- [ ] The distance threshold at which to merge two clusters.
- [ ] The true labels for a representative subset of the data.

**Q2. In k-Means, why does the algorithm always converge (terminate)?**
- [ ] Because centroids are initialized using k-means++ which guarantees a unique solution.
- [ ] Because the algorithm stops after a fixed maximum number of iterations is reached.
- [x] Because every step either decreases or maintains the total within-cluster sum of squares, and there are only finitely many possible assignments.
- [ ] Because Euclidean distance always produces well-separated clusters.

**Q3. The "curse of dimensionality" in machine learning means:**
- [ ] High-dimensional datasets are too large to fit in memory on standard hardware.
- [x] Distance metrics lose meaning and data becomes exponentially sparse as the number of dimensions grows.
- [ ] Deep learning models require more layers when input features are high-dimensional.
- [ ] Clustering algorithms fail by definition when features exceed 3 dimensions.

**Q4. What does PCA primarily preserve when reducing dimensionality?**
- [ ] The original feature names and measurement units.
- [ ] The cluster assignments that k-Means would produce.
- [x] The directions of maximum variance — the global structure of the data.
- [ ] Local neighborhood relationships between closely clustered points.

**Q5. When would you prefer t-SNE over PCA for a visualization task?**
- [ ] When you need a compressed representation to feed into a downstream linear classifier.
- [x] When you want to visualize local cluster structure in high-dimensional data (e.g., embeddings) in 2D.
- [ ] When you need a deterministic, reproducible 2D plot that others can regenerate exactly.
- [ ] When your dataset has many more samples than features.

**Q6. The elbow method for choosing k in k-Means involves:**
- [ ] Choosing k equal to the number of distinct labels found by label propagation.
- [ ] Stopping when successive centroid updates change by less than a threshold.
- [x] Plotting within-cluster sum of squares (WCSS) vs. k and selecting the k where the curve bends most sharply.
- [ ] Evaluating multiple distance metrics and choosing k where they agree.
