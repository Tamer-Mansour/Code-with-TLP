# Exercise: Naive Bayes Classifier

Implement a **Naive Bayes classifier** for binary classification with binary features using Laplace (add-1) smoothing.

## Background

Naive Bayes applies Bayes' theorem under the "naive" assumption that features are **conditionally independent** given the class label. Despite this strong assumption, it often performs surprisingly well, especially on text classification.

**Bayes' theorem**:
```
P(y | x) ∝ P(y) · P(x | y) = P(y) · Π_j P(x_j | y)
```

We predict the class with the highest **log posterior** (to avoid underflow from multiplying small probabilities):
```
log P(y | x) ∝ log P(y) + Σ_j log P(x_j | y)
```

### Laplace Smoothing

Without smoothing, a feature value never seen with a class would make the entire product zero. **Add-1 (Laplace) smoothing** adds one pseudo-count to every combination:

```
P(y) = (count(y) + 1) / (N + num_classes)

P(x_j = v | y) = (count(x_j = v, y) + 1) / (count(y) + 2)
```

The `+2` in the denominator accounts for both possible values (0 and 1) of the binary feature.

## Your Task

Train a Naive Bayes model on N labeled examples with D binary features. Classify M test examples using the log posterior. Print predicted class (0 or 1) for each test example.

## Key Concepts Practiced

- Bayes' theorem in practice
- Laplace smoothing to handle unseen feature values
- Log-space computation to prevent numerical underflow
- Generative vs. discriminative classifiers
