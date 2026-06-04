# Exercise: Gradient Descent from Scratch

Train a linear regression model using **batch gradient descent** from scratch. This exercise builds on the theory of gradient descent by having you implement the full iterative training loop — not just one step, but 1000 steps on real data.

## Background

Gradient descent minimizes the mean squared error loss for a linear model `ŷ = w·x + b`:

```
MSE = (1/N) · Σᵢ (w·xᵢ + b − yᵢ)²

∂MSE/∂w = (2/N) · Σᵢ (w·xᵢ + b − yᵢ) · xᵢ
∂MSE/∂b = (2/N) · Σᵢ (w·xᵢ + b − yᵢ)
```

Each iteration updates both parameters simultaneously:
```
w ← w − α · (∂MSE/∂w)
b ← b − α · (∂MSE/∂b)
```

With learning rate `α = 0.01` and `1000` iterations, gradient descent reliably converges on small linear datasets.

## Your Task

Read N (feature, target) pairs from stdin. Run batch gradient descent for 1000 iterations starting from `w=0.0, b=0.0`. Print the final `w` and `b`, each rounded to 4 decimal places.

## Example

If the data is perfectly linear (`y = 2x`), gradient descent should converge to `w ≈ 2.0000` and `b ≈ 0.0000`.

## Key Concepts Practiced

- Implementing a training loop from scratch
- Computing batch gradients over an entire dataset
- Understanding convergence through iteration
- The relationship between learning rate and convergence speed
