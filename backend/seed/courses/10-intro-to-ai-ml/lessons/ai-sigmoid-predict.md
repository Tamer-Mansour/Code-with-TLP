# Exercise: Sigmoid Function and Logistic Prediction

Logistic regression applies the sigmoid function to a linear combination of features to produce a probability, then classifies the example based on whether that probability is at or above 0.5.

## Background

**Linear combination**:
```
z = w0 + w1*x1 + w2*x2 + ... + wn*xn
```

**Sigmoid function**:
```
sigma(z) = 1 / (1 + exp(-z))
```

**Decision rule**: predict class 1 if sigma(z) >= 0.5 (equivalently, z >= 0), class 0 otherwise.

## Task

Given a weight vector (including bias w0) and a feature vector, compute z, the sigmoid output, and the predicted class label.
