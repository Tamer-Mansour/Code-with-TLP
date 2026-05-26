# Sigmoid Function and Logistic Prediction

Given a bias weight `w0`, a weight vector, and a feature vector, compute the logistic regression prediction.

**Input**:
- Line 1: integer `n` (number of features, not counting the bias)
- Line 2: `n+1` space-separated floats: `w0 w1 w2 ... wn` (bias first, then feature weights)
- Line 3: `n` space-separated floats: `x1 x2 ... xn` (feature values)

**Output** (three lines):
```
z: <value rounded to 4 dp>
p: <value rounded to 4 dp>
prediction: <0 or 1>
```

Where:
- `z = w0 + w1*x1 + ... + wn*xn`
- `p = 1 / (1 + exp(-z))`
- `prediction = 1` if `p >= 0.5`, else `0`

Use `math.exp` from the standard library.

**Example**

Input:
```
2
-1.0 0.5 0.4
2.0 3.0
```

Output:
```
z: 1.2000
p: 0.7685
prediction: 1
```

Explanation: z = -1.0 + 0.5*2.0 + 0.4*3.0 = -1.0 + 1.0 + 1.2 = 1.2. p = 1/(1+e^-1.2) ≈ 0.7685 >= 0.5 → predict 1.
