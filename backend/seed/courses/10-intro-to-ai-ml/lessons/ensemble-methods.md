# Ensemble Methods and Support Vector Machines

When a single model is not enough, combine many. **Ensemble methods** are among the most powerful tools in practical machine learning — they routinely win Kaggle competitions and power production systems at major tech companies. This lesson covers bagging, boosting, and support vector machines.

## Why Ensembles Work

A single decision tree has **high variance**: small changes in training data produce a very different tree. Combine many trees and the random errors **cancel out**, leaving the true signal.

Formally, if you average `B` independent models each with error variance `σ²`, the ensemble's error variance is `σ²/B`. Even with moderately correlated models, the variance reduction is significant.

## Bagging (Bootstrap Aggregating)

**Bagging** creates diversity by training each model on a different random sample of the data.

**Algorithm**:
1. Draw `B` bootstrap samples (sample n examples **with replacement** from the training set — about 63% of examples appear in each sample).
2. Train one model (typically a decision tree) on each bootstrap sample independently.
3. **Prediction**: average predictions (regression) or majority vote (classification).

### Random Forests

Random forests extend bagging with one additional trick: at each node split, only consider a **random subset of features** (typically `√d` for classification, `d/3` for regression).

This extra randomness makes the trees less correlated with each other — which amplifies the variance reduction.

**Practical advantages**:
- Among the strongest off-the-shelf classifiers for tabular data
- No feature scaling required
- Robust to outliers and irrelevant features
- Built-in feature importance: features used for splits near the root are the most informative
- Out-of-bag (OOB) error: each tree was not trained on ~37% of data — use these for free validation

```python
# Conceptual random forest prediction
predictions = []
for tree in forest:
    predictions.append(tree.predict(x))
return majority_vote(predictions)  # classification
```

**Key hyperparameters**: number of trees (`n_estimators`), max tree depth, min samples per leaf, number of features considered per split.

## Boosting

Where bagging trains models in **parallel** on independent samples, boosting trains models **sequentially**, with each model focusing on the mistakes of the previous one.

### AdaBoost (Adaptive Boosting)

1. Assign equal weights `wᵢ = 1/n` to all training examples.
2. For `t = 1, 2, ..., T`:
   - Train a **weak learner** (typically a 1-level decision tree, called a "stump") on the weighted data.
   - Compute its weighted error: `ε_t = Σᵢ wᵢ · 𝟙[yᵢ ≠ ĥ_t(xᵢ)]`
   - Compute model weight: `α_t = (1/2) · ln((1 − ε_t) / ε_t)` — higher weight for better models
   - Update example weights: increase weight of misclassified examples, decrease for correct ones
3. **Final prediction**: weighted majority vote of all weak learners: `sign(Σ_t α_t · ĥ_t(x))`

Misclassified examples get higher weights → the next stump focuses more on them. The ensemble builds up to a strong classifier from many weak ones.

### Gradient Boosting

Gradient boosting generalizes AdaBoost using a gradient descent perspective:

- Each new tree fits the **negative gradient of the loss** with respect to the current model's predictions (the **residuals** for MSE loss).
- Add the new tree to the ensemble with a **learning rate** `η` (shrinkage).

```
F₀(x) = mean(y)
For t = 1 to T:
    rᵢ = −∂L/∂F(xᵢ)   (residuals / pseudo-residuals)
    Train tree hₜ on residuals {(xᵢ, rᵢ)}
    Fₜ(x) = F_{t-1}(x) + η · hₜ(x)
```

**XGBoost, LightGBM, CatBoost** are highly optimized implementations of gradient boosting that handle large datasets efficiently and include regularization, missing value handling, and categorical feature support. They dominate structured/tabular data competitions.

### Bagging vs. Boosting

| Aspect | Bagging (Random Forest) | Boosting (Gradient Boosting) |
|---|---|---|
| Training order | Parallel | Sequential |
| Focus | Reduce variance | Reduce bias + variance |
| Sensitivity to noise | Low | Higher (can overfit noisy labels) |
| Interpretability | Low | Low |
| Speed | Fast (parallelizable) | Slower |
| Typical performance | Excellent baseline | Often best on tabular data |

## Support Vector Machines (SVMs)

SVMs find the **maximum-margin hyperplane** — the decision boundary that is as far as possible from the nearest training points of each class. These nearest points are called **support vectors**.

### Hard-Margin SVM (Linearly Separable Data)

For data that is linearly separable with labels `y ∈ {+1, −1}`:

The margin is `2 / ||w||`. Maximizing the margin is equivalent to minimizing `||w||²`.

**Optimization problem**:
```
Minimize:    (1/2) ||w||²
Subject to:  yᵢ · (w·xᵢ + b) ≥ 1   for all i
```

The constraint ensures every training point is on the correct side and at least distance `1/||w||` from the boundary.

### Soft-Margin SVM (Non-Separable Data)

Real data has noise and overlapping classes. Allow some violations with **slack variables** `ξᵢ ≥ 0`:

```
Minimize:    (1/2) ||w||² + C · Σᵢ ξᵢ
Subject to:  yᵢ · (w·xᵢ + b) ≥ 1 − ξᵢ
```

**C** is the regularization hyperparameter:
- Large C: fewer violations allowed, smaller margin, more overfitting risk.
- Small C: more violations allowed, larger margin, less overfitting.

### The Kernel Trick

SVMs can classify **non-linearly separable** data by mapping features to a higher-dimensional space where they become separable — without ever explicitly computing the transformation.

**The kernel function** `K(xᵢ, xⱼ) = φ(xᵢ)·φ(xⱼ)` computes the dot product in the high-dimensional space implicitly:

| Kernel | Formula | When to use |
|---|---|---|
| Linear | `xᵢ·xⱼ` | Text classification, high-dim sparse data |
| RBF (Gaussian) | `exp(−γ||xᵢ−xⱼ||²)` | Most non-linear problems; common default |
| Polynomial | `(γxᵢ·xⱼ + r)^d` | Image recognition tasks |

The RBF kernel maps data into an infinite-dimensional space and can represent arbitrarily complex boundaries. The `γ` parameter controls how wide the influence of each training point is.

## Further Reading

- **Dive into Deep Learning (D2L.ai)** — Covers tree-based methods and the relationship to deep learning: https://d2l.ai/
- **Understanding Machine Learning** (Shalev-Shwartz & Ben-David) — Rigorous treatment of SVMs, margin theory, and boosting with PAC guarantees: https://www.cs.huji.ac.il/~shais/UnderstandingMachineLearning/understanding-machine-learning-theory-algorithms.pdf
- **MIT 6.034 AI** — Winston's lectures on SVMs and learning theory: https://ocw.mit.edu/courses/6-034-artificial-intelligence-fall-2010/
