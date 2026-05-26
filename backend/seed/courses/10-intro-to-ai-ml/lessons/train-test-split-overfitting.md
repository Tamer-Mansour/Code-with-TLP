# Train/Test Split, Overfitting, and the Bias-Variance Tradeoff

The most important habit in machine learning is **never evaluating a model on the same data it was trained on**. This lesson explains why — in depth — and introduces the bias-variance tradeoff that governs every modeling decision.

## The Core Problem: Generalization

Suppose you memorize every answer to every practice exam available. You score 100% on those exams — but you've learned nothing useful, and you'll struggle on the real exam if it contains novel questions.

A model that memorizes training data does exactly the same thing: near-zero training error, catastrophic failure on new data. This is called **overfitting**, and it is the central challenge of supervised machine learning.

The goal is not to fit training data perfectly — it's to **generalize**: perform well on data the model has never seen. We call this property *generalization*, and every modeling decision should be judged by it, not by training performance alone.

## Worked Example: Polynomial Regression

Consider 10 training points generated from the noisy function y = sin(x) + noise.

| Degree | Train error | Validation error | What happened |
|---|---|---|---|
| 1 (line) | 0.42 | 0.44 | Underfitting: too simple to capture the curve |
| 3 (cubic) | 0.09 | 0.10 | Good fit: captures the curve without memorizing noise |
| 9 (nonic) | 0.000 | 1.82 | Overfitting: passes through every training point, wildly wrong elsewhere |

The degree-9 polynomial has 10 parameters for 10 training points — it can achieve *zero* training error by definition (a degree-n polynomial can fit n+1 points exactly). But it oscillates wildly between those points, producing terrible validation error.

## The Train / Validation / Test Split

Split your dataset into three **non-overlapping** parts **before any modeling begins**:

| Split | Typical size | Purpose |
|---|---|---|
| Training set | 60–80% | Fit model parameters |
| Validation set | 10–20% | Tune hyperparameters, select between models |
| Test set | 10–20% | Final, unbiased estimate of deployed performance |

**Critical rule**: The test set is a sealed envelope. Touch it exactly once — at the very end, after all decisions are made. If you use test performance to choose between models, you have leaked information. Your test estimate is no longer unbiased, and you have effectively been training on the test set.

## The Bias-Variance Tradeoff

The generalization error of any model can be decomposed into three components:

```
Expected error = Bias² + Variance + Irreducible noise
```

**Bias** measures how far the model's average prediction is from the true value. A high-bias model makes *systematic errors* — it's wrong in a consistent direction. A linear model trying to fit a quadratic relationship always underpredicts at the extremes.

**Variance** measures how much the model's predictions *fluctuate* across different training sets. A high-variance model is very sensitive to the specific training points it saw — if you train it on a slightly different set, you get a very different model.

**Irreducible noise** is the unpredictable randomness in the data that no model can remove.

### The Tradeoff

| Model complexity | Bias | Variance | Training error | Validation error |
|---|---|---|---|---|
| Too simple (underfit) | High | Low | High | High |
| Just right | Low | Low | Low | Low |
| Too complex (overfit) | Low | High | Very low | High |

Increasing model complexity *always* decreases bias and *always* increases variance. The art of ML is finding the complexity level that minimizes their *sum*.

Visualized:

```
Error
 |
 |    Bias²
 |  \
 |   \          Variance
 |    \         /
 |     \       /
 |      \_____/   ← Total error
 |_________________________
         Model Complexity →
```

The minimum of the total error curve is the sweet spot.

## Cross-Validation: Reliable Estimates with Limited Data

A single train/validation split is unreliable when data is scarce — if you're unlucky, your 200-example validation set might be unrepresentative. **k-fold cross-validation** fixes this.

**Procedure (k=5)**:
1. Split data into 5 equal folds.
2. Round 1: train on folds {2,3,4,5}, validate on fold {1}. Record validation score.
3. Round 2: train on folds {1,3,4,5}, validate on fold {2}. Record validation score.
4. ... repeat for each fold.
5. Average the 5 validation scores. This average is your cross-validation estimate.

```
Data: [fold1 | fold2 | fold3 | fold4 | fold5]

Round 1: [TRAIN | TRAIN | TRAIN | TRAIN | VAL  ]
Round 2: [TRAIN | TRAIN | TRAIN | VAL   | TRAIN]
Round 3: [TRAIN | TRAIN | VAL   | TRAIN | TRAIN]
Round 4: [TRAIN | VAL   | TRAIN | TRAIN | TRAIN]
Round 5: [VAL   | TRAIN | TRAIN | TRAIN | TRAIN]
```

Every example appears in validation exactly once. This is 5× more computationally expensive but dramatically more reliable.

**The test set is still held out from ALL folds.** Cross-validation replaces the validation set, not the test set.

**Leave-One-Out Cross-Validation (LOOCV)**: k = n (number of examples). Each example is its own validation set. Maximum data usage but computationally expensive.

## Diagnosing Your Model

**High training error AND high validation error** → underfitting. Fix: use a more complex model, add features, reduce regularization.

**Low training error AND high validation error** → overfitting. Fix: get more data, simplify model, add regularization, use dropout, use early stopping.

**Training error ≈ validation error, both low** → good generalization.

**Training error ≈ validation error, both high** → the problem may be harder than the model can represent, or data quality issues.

## Common Remedies for Overfitting

**More data**: almost always the most effective remedy. Variance decreases as the training set grows — with infinite data, even complex models generalize well.

**Regularization**: add a penalty for large parameter values to the loss function.
- **L2 (Ridge)**: penalty = λ·Σwᵢ². Shrinks all weights toward zero uniformly.
- **L1 (Lasso)**: penalty = λ·Σ|wᵢ|. Drives some weights to exactly zero — effectively selecting features.
- **Elastic Net**: combination of L1 and L2.

**Dropout**: during training, randomly zero out a fraction (e.g., 50%) of neurons in each layer. Forces the network to learn redundant representations and cannot rely on any single pathway. Equivalent to training an ensemble of many smaller networks.

**Early stopping**: monitor validation loss during training. When it stops improving (or starts increasing), stop training. Prevents the model from memorizing training data during the later epochs.

**Data augmentation**: artificially expand the training set by applying label-preserving transformations. For images: rotations, flips, crops, color jitter. For text: synonym replacement, back-translation.

## Key Takeaways

- Overfitting = low training error, high validation error. Underfitting = high both.
- The bias-variance decomposition: Total error = Bias² + Variance + Irreducible noise.
- k-fold cross-validation gives reliable generalization estimates when data is limited.
- Always split data before modeling; the test set is sacred — one use only.
- Remedies form a toolkit: more data, regularization, dropout, early stopping, data augmentation.
