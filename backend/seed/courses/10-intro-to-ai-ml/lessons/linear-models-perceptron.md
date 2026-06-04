# Linear Models and the Perceptron

Linear models draw a straight line (or hyperplane) to separate or predict. The **perceptron** is the simplest linear classifier and the direct ancestor of every modern neural network. Mastering it gives you the conceptual foundation for everything from logistic regression to deep learning.

## What Is a Linear Classifier?

A linear classifier computes a weighted sum of features and uses the sign of the result to assign a class label:

```
z = w₁·x₁ + w₂·x₂ + ... + wₙ·xₙ + b
Predict +1 if z > 0, else predict -1
```

The parameters `w` (weights) and `b` (bias) define a **decision boundary** — a hyperplane in feature space that separates the two classes.

In 2D, this boundary is a line: `w₁·x₁ + w₂·x₂ + b = 0`. Points above the line get one label, points below get the other.

## The Perceptron Algorithm

Invented by Frank Rosenblatt in 1957, the perceptron is the earliest learning algorithm for linear classifiers. It is both simple and provably correct for **linearly separable** data.

### The Update Rule

Initialize all weights and bias to zero. For each training example `(x, y)` where `y ∈ {+1, −1}`:

```
z = dot(w, x) + b

If y * z <= 0:   (misclassified or on the boundary)
    w ← w + y * x
    b ← b + y
```

The condition `y * z <= 0` means the prediction is wrong:
- If `y = +1` but `z ≤ 0`: prediction was -1, should be +1. Add `x` to `w`.
- If `y = -1` but `z ≥ 0`: prediction was +1, should be -1. Subtract `x` from `w`.

Repeat passes over the full training set until no mistakes occur (or for a maximum number of epochs).

### Worked Example

Training set (2D):

| x₁ | x₂ | y |
|---|---|---|
| 2  | 1  | +1 |
| -1 | -2 | -1 |
| 1  | -1 | -1 |

**Initialize**: w = [0, 0], b = 0.

**Epoch 1, Example 1**: x=[2,1], y=+1
- z = 0·2 + 0·1 + 0 = 0
- y·z = +1·0 = 0 ≤ 0 → misclassified
- w = [0+1·2, 0+1·1] = [2, 1], b = 0+1 = 1

**Epoch 1, Example 2**: x=[-1,-2], y=-1
- z = 2·(-1) + 1·(-2) + 1 = -2 - 2 + 1 = -3
- y·z = (-1)·(-3) = 3 > 0 → correct, no update

**Epoch 1, Example 3**: x=[1,-1], y=-1
- z = 2·1 + 1·(-1) + 1 = 2 - 1 + 1 = 2
- y·z = (-1)·2 = -2 ≤ 0 → misclassified
- w = [2+(-1)·1, 1+(-1)·(-1)] = [1, 2], b = 1+(-1) = 0

**Epoch 2, Example 1**: x=[2,1], y=+1
- z = 1·2 + 2·1 + 0 = 4
- y·z = 4 > 0 → correct

**Epoch 2, Example 2**: x=[-1,-2], y=-1
- z = 1·(-1) + 2·(-2) + 0 = -5
- y·z = (-1)·(-5) = 5 > 0 → correct

**Epoch 2, Example 3**: x=[1,-1], y=-1
- z = 1·1 + 2·(-1) + 0 = -1
- y·z = (-1)·(-1) = 1 > 0 → correct

No mistakes in Epoch 2 → training complete. Final: **w = [1, 2], b = 0**.

### The Perceptron Convergence Theorem

If the data is **linearly separable** (a hyperplane exists that correctly classifies all training points), the perceptron algorithm is **guaranteed to converge** in a finite number of steps. The bound on convergence depends on the **margin** — the distance from the separating hyperplane to the nearest training point. Larger margins mean faster convergence.

If the data is **not linearly separable**, the perceptron loops forever. In practice: set a maximum epoch count.

## Feature Normalization

Before applying any linear model, **normalize features** to have comparable scales:

**Standardization** (zero mean, unit variance):
```python
x_scaled = (x - mean(x)) / std(x)
```

**Min-max scaling** (range [0, 1]):
```python
x_scaled = (x - min(x)) / (max(x) - min(x))
```

Without normalization, a feature with range 0–10,000 dominates a feature with range 0–1. The gradient/update for the large-scale feature is much bigger, making learning unstable.

## From Perceptron to Neural Networks

The perceptron is a single artificial neuron:
- Compute `z = w·x + b` (linear combination)
- Apply a **step function**: output +1 if z > 0, else -1

Replace the step function with a differentiable function (sigmoid, ReLU) and you get a modern **artificial neuron**. Stack many neurons in layers and you get a **multi-layer perceptron (MLP)** — the core building block of deep learning.

The perceptron's limitation: it can only solve **linearly separable** problems. XOR is not linearly separable — a single perceptron cannot learn it. This limitation (famously pointed out by Minsky and Papert in 1969) was resolved by adding hidden layers, enabling non-linear decision boundaries.

## Further Reading

- **MIT 6.034 AI (OpenCourseWare)** — Patrick Henry Winston's lectures cover the perceptron and linear separability from first principles: https://ocw.mit.edu/courses/6-034-artificial-intelligence-fall-2010/
- **MIT 6.036 ML Notes** — Chapter on linear classifiers covers the perceptron, margin, and SVM from a rigorous theoretical perspective: https://ocw.mit.edu/courses/6-036-introduction-to-machine-learning-fall-2020/
- **Understanding Machine Learning** (Shalev-Shwartz & Ben-David) — Chapter 9 covers the perceptron with PAC learning guarantees: https://www.cs.huji.ac.il/~shais/UnderstandingMachineLearning/understanding-machine-learning-theory-algorithms.pdf
