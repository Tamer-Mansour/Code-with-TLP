# Perceptron Learning Algorithm

Implement the **perceptron learning algorithm** for binary classification with labels `+1` and `-1`.

Train on N examples with D features for up to **100 epochs** (stop early if no mistakes in an epoch). Then classify M test examples.

**Update rule**: if `y * (dot(w, x) + b) <= 0`, then `w = w + y*x` and `b = b + y`.

Initialize `w` as all zeros, `b = 0`.

**Prediction**: output `1` if `dot(w, x) + b > 0`, else `-1`.

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

- Line 1: three integers N, D, M
- Next N lines: D floats followed by integer label (`1` or `-1`)
- Next M lines: D floats (test points, no labels)

## Output Format

M lines, each with the predicted label (`1` or `-1`).

## Example

**Input:**
```
4 2 2
1.0 1.0 1
-1.0 -1.0 -1
1.0 -0.5 1
-0.5 1.0 -1
2.0 2.0
-2.0 -2.0
```

**Output:**
```
1
-1
```

## Notes

- Scan training examples in input order each epoch.
- Stop as soon as a complete epoch passes with zero mistakes, or after 100 epochs.
- Use only the Python standard library.
- The training data in the test cases is always linearly separable.
