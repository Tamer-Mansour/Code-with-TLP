# Gradient Descent from Scratch

Implement **batch gradient descent** to train a linear regression model with one feature.

Given N (feature, target) pairs, run gradient descent for **1000 iterations** and print the final weight `w` and bias `b`, each rounded to 4 decimal places.

**Parameters**: learning rate `α = 0.01`, initialize `w = 0.0`, `b = 0.0`.

**Update rule (each iteration)**:
```
dw = (1/N) · Σᵢ (w·xᵢ + b − yᵢ) · xᵢ
db = (1/N) · Σᵢ (w·xᵢ + b − yᵢ)
w  ← w − 0.01 · dw
b  ← b − 0.01 · db
```

## Input Format

```
N
x₁ y₁
x₂ y₂
...
xₙ yₙ
```

- First line: integer N (number of training points)
- Next N lines: two floats `x` and `y`, space-separated

## Output Format

```
w=<value>
b=<value>
```

Both values rounded to exactly 4 decimal places.

## Example

**Input:**
```
5
1.0 2.0
2.0 4.0
3.0 6.0
4.0 8.0
5.0 10.0
```

**Output:**
```
w=2.0000
b=0.0000
```

## Notes

- The data `y = 2x` is perfectly linear so gradient descent converges to the exact answer.
- Use only the Python standard library — no numpy or external packages.
- The 1000-iteration limit and learning rate 0.01 are fixed; do not add early stopping.
