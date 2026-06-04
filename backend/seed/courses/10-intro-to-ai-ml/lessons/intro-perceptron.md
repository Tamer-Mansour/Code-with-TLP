# Exercise: Perceptron Learning Algorithm

Implement the **perceptron learning algorithm** from scratch — the foundational binary classifier and the conceptual ancestor of modern neural networks.

## Background

The perceptron is a linear classifier using labels `y ∈ {+1, −1}`. It predicts:

```
ŷ = +1  if  w·x + b > 0
ŷ = -1  otherwise
```

**Update rule** (applied whenever an example is misclassified):
```
if y · (w·x + b) <= 0:
    w ← w + y · x
    b ← b + y
```

This rule moves the decision boundary toward the misclassified point. If the data is linearly separable, the perceptron is guaranteed to converge to a perfect separator.

## Your Task

Given N labeled training examples with D features, train the perceptron for up to 100 epochs (stop early if a full epoch passes with no misclassifications). Then predict the class labels for M test examples.

## Algorithm Details

- Initialize: `w = [0.0] * D`, `b = 0.0`
- Each epoch: scan training examples in input order, apply the update rule when misclassified
- Stop: after 100 epochs, or when a full epoch produces zero mistakes
- Predict: `+1` if `dot(w, x) + b > 0`, else `-1`

## Key Concepts Practiced

- Implementing the perceptron update rule
- Understanding convergence on linearly separable data
- The connection between weight updates and geometric movement of the decision boundary
