# Linear and Logistic Regression

Regression models are the workhorses of supervised learning. They are simple, interpretable, and often surprisingly competitive with more complex models. Understanding them deeply — including the math — is essential because every advanced method builds on the same ideas.

## Linear Regression

**Goal**: predict a continuous output `y` from input features `x₁, x₂, ..., xₙ`.

The model is:
```
ŷ = w₀ + w₁·x₁ + w₂·x₂ + ... + wₙ·xₙ
```

Where `w₀` is the **bias** (intercept) and `w₁...wₙ` are the **weights** (coefficients). We can write this compactly as `ŷ = wᵀx` (dot product) if we prepend a 1 to x for the bias term.

### Training: Minimizing Mean Squared Error

We want weights that minimize the average squared difference between predictions and true values:

```
MSE = (1/m) · Σᵢ (ŷᵢ - yᵢ)²
```

### A Worked Example: Hand-Computing a Linear Fit

Three training points for house price prediction:

| Size x (sq ft) | Price y ($k) |
|---|---|
| 1000 | 200 |
| 1500 | 290 |
| 2000 | 380 |

Observe that price increases by 90 for every 500 sq ft increase → slope = 90/500 = **0.18**.
Using point (1000, 200): intercept = 200 − 0.18·1000 = **20**.
Model: `ŷ = 0.18·x + 20`.

**Verify**: 
- x=1000: ŷ = 180+20 = 200 ✓
- x=1500: ŷ = 270+20 = 290 ✓
- x=2000: ŷ = 360+20 = 380 ✓ (perfect fit here since the data is exactly linear)

**Prediction**: For a 1800 sq ft house: ŷ = 0.18·1800 + 20 = 324 + 20 = **$344k**.

**MSE on these training points**: all errors are 0, so MSE = 0. In practice, data has noise — the model would fit a line that minimizes the sum of squared vertical deviations from the points.

### Gradient Descent for Linear Regression

For the single-weight model `ŷ = w·x` (no bias for simplicity) and loss `L = (ŷ - y)²`:

```
∂L/∂w = 2·(ŷ - y)·x = 2·(w·x - y)·x
```

Update: `w ← w - α · ∂L/∂w`

**Example**: w=1, x=2, y=6, α=0.1.
- ŷ = 1·2 = 2
- ∂L/∂w = 2·(2−6)·2 = 2·(−4)·2 = −16
- w_new = 1 − 0.1·(−16) = 1 + 1.6 = **2.6**

After one step, w moved from 1.0 toward 3.0 (the true value for y=3x). Repeating many times converges to w=3.

## Logistic Regression

Despite the name, logistic regression is a **classification** algorithm. It predicts the *probability* that an example belongs to class 1.

### The Sigmoid Function

```
σ(z) = 1 / (1 + e^(-z))
```

Key properties:
- σ(0) = 0.5 (exactly on the decision boundary)
- σ(−∞) → 0, σ(+∞) → 1
- Output is always in (0, 1), making it a valid probability
- Derivative: σ'(z) = σ(z)·(1 − σ(z)) — useful for gradient computation

The model is:
```
p = σ(z)  where  z = w₀ + w₁·x₁ + ... + wₙ·xₙ
Predict class 1 if p ≥ 0.5 (equivalently, if z ≥ 0)
Predict class 0 if p < 0.5
```

### Worked Example: Email Spam

Features: x₁ = "free" word count, x₂ = "money" word count. Trained weights: w₀ = −2, w₁ = 1.5, w₂ = 1.0.

Email A: x₁=3, x₂=1 (has "free" 3 times, "money" once):
```
z = −2 + 1.5·3 + 1.0·1 = −2 + 4.5 + 1.0 = 3.5
p = σ(3.5) = 1/(1 + e^(-3.5)) = 1/(1 + 0.0302) ≈ 0.97
```
97% probability of spam → **classify as spam**.

Email B: x₁=0, x₂=0 (neither word appears):
```
z = −2 + 0 + 0 = −2
p = σ(−2) = 1/(1 + e^2) = 1/(1 + 7.389) ≈ 0.119
```
12% probability of spam → **classify as not spam**.

### The Decision Boundary

The boundary p = 0.5 corresponds to z = 0, which defines a **hyperplane** in feature space:
```
w₀ + w₁·x₁ + ... + wₙ·xₙ = 0
```

In 2D: a line. In 3D: a plane. In n-D: a hyperplane. Everything on one side is predicted as class 1, the other as class 0.

For the spam example: −2 + 1.5·x₁ + 1.0·x₂ = 0 → boundary line: x₂ = 2 − 1.5·x₁.

### Training: Binary Cross-Entropy Loss

MSE is not ideal for classification. Instead, logistic regression minimizes **binary cross-entropy** (also called log loss):

```
L = −(1/m) · Σᵢ [yᵢ · log(pᵢ) + (1 − yᵢ) · log(1 − pᵢ)]
```

Why this loss? It heavily penalizes **confident wrong predictions**:
- True label = 1, predicted p = 0.01: contribution = −log(0.01) ≈ 4.6 (large penalty)
- True label = 1, predicted p = 0.99: contribution = −log(0.99) ≈ 0.01 (small penalty)

The gradients of cross-entropy are simpler and better-behaved than MSE for classification, leading to faster and more stable training.

## Regularization for Both Models

Both linear and logistic regression overfit when there are many features or limited data. Regularization adds a penalty for large weights to the loss:

### L2 Regularization (Ridge)

```
L_reg = L + λ · Σᵢ wᵢ²
```

Effect: shrinks all weights toward zero, but rarely exactly to zero. Handles correlated features well. The regularization strength `λ` is a hyperparameter — larger λ means more shrinkage.

**Example**: if w₁=5 is very large and λ=0.1, the penalty adds 0.1·25=2.5 to the loss, discouraging such large weights.

### L1 Regularization (Lasso)

```
L_reg = L + λ · Σᵢ |wᵢ|
```

Effect: drives some weights to **exactly zero**, performing automatic feature selection. If you have 1000 features but only 50 are relevant, Lasso can identify and zero out the irrelevant 950. Useful in genomics, finance, and text classification.

The optimal `λ` is chosen via cross-validation.

## When to Use Each

| Algorithm | Output | Best for |
|---|---|---|
| Linear regression | Continuous real value | House price, temperature, salary |
| Logistic regression | Probability + binary class | Spam/ham, disease/healthy, fraud/legit |
| Logistic regression (multi-class) | Probability distribution over k classes | Digit classification (0–9), sentiment (positive/neutral/negative) |

## Why Linear Models Are Still Useful

Despite the prevalence of neural networks, linear models remain valuable:

- **Interpretable**: each weight has a direct meaning. "Adding one square foot adds $180 to the predicted price." Regulators often require interpretability.
- **Fast**: train on millions of examples in seconds. Inference is a single dot product.
- **Baseline**: if a linear model works well, you don't need a neural network. Don't add complexity you don't need.
- **Foundation**: understanding linear models makes every advanced method clearer — attention is essentially weighted linear combinations, and logistic regression is a single-layer neural network.
