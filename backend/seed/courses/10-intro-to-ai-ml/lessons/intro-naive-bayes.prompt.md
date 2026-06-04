# Naive Bayes Classifier (Discrete Features)

Implement a **Naive Bayes classifier** for binary classification with binary (0/1) features and **Laplace (add-1) smoothing**.

Train on N examples, then classify M test examples. Output the predicted class (`0` or `1`) for each test example.

## Formulas

```
P(y) = (count(y) + 1) / (N + 2)                  [Laplace-smoothed prior]
P(x_j = v | y) = (count(x_j=v, y) + 1) / (count(y) + 2)   [binary feature]
```

**Predict**: class with higher `log P(y) + Σ_j log P(x_j | y)`.

## Input Format

```
N D M
x₁₁ x₁₂ ... x₁D y₁
x₂₁ x₂₂ ... x₂D y₂
...
(N training lines)
t₁₁ t₁₂ ... t₁D
(M test lines)
```

- Line 1: integers N (training examples), D (features), M (test examples)
- Next N lines: D binary integers (0 or 1) followed by class label (0 or 1)
- Next M lines: D binary integers (test features, no label)

## Output Format

M lines, each with predicted class (`0` or `1`).

## Example

**Input:**
```
6 3 2
1 1 0 1
1 0 1 1
0 0 0 0
0 1 0 0
1 1 1 1
0 0 1 0
1 1 0
0 0 1
```

**Output:**
```
1
0
```

## Notes

- Use log probabilities to avoid numerical underflow when D is large.
- Laplace smoothing denominator is `count(y) + 2` for binary features (two possible values).
- Use only the Python standard library (no numpy or scipy).
- If scores are tied, predict class `0`.
