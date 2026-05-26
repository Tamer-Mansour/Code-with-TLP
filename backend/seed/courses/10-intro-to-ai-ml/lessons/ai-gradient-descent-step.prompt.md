# One Step of Gradient Descent

You have a linear model: `y_hat = w * x + b`.

Loss function (MSE for a single example): `L = (y_hat - y)^2`

Gradients:
```
dL/dw = 2 * (y_hat - y) * x
dL/db = 2 * (y_hat - y)
```

Update rule:
```
w_new = w - alpha * dL/dw
b_new = b - alpha * dL/db
```

Given `w`, `b`, `x`, `y` (all integers), and `alpha` (a fraction written as numerator and denominator), compute `w_new` and `b_new`.

Output both values rounded to **2 decimal places**.

## Input Format

```
w b x y
p q
```

- Line 1: integers `w`, `b`, `x`, `y` (space-separated).
- Line 2: integers `p` and `q` such that `alpha = p / q` (e.g. `1 10` means alpha = 0.1).

## Output Format

```
w: X.XX
b: X.XX
```

## Examples

**Example 1**
```
Input:
1 0 2 6
1 10

Output:
w: 2.60
b: 0.80
```

Workings: y_hat = 1*2 + 0 = 2. dL/dw = 2*(2-6)*2 = -16. dL/db = 2*(2-6) = -8. alpha = 0.1.
w_new = 1 - 0.1*(-16) = 2.60. b_new = 0 - 0.1*(-8) = 0.80.

**Example 2**
```
Input:
3 1 4 10
1 10

Output:
w: 0.60
b: 0.40
```

Workings: y_hat = 3*4 + 1 = 13. dL/dw = 2*(13-10)*4 = 24. dL/db = 2*(13-10) = 6. alpha = 0.1.
w_new = 3 - 0.1*24 = 0.60. b_new = 1 - 0.1*6 = 0.40.

**Example 3**
```
Input:
2 1 3 7
1 4

Output:
w: 2.00
b: 1.00
```

Workings: y_hat = 2*3 + 1 = 7 = y. dL/dw = 0. dL/db = 0. alpha = 0.25. No change.
