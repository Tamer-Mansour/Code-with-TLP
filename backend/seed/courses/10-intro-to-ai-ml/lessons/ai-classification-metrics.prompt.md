# Classification Metrics

Given predicted and actual binary labels (0 or 1), compute:

1. **Accuracy** = (TP + TN) / total
2. **Precision** = TP / (TP + FP)  — output `0.00` if TP+FP = 0
3. **Recall** = TP / (TP + FN)  — output `0.00` if TP+FN = 0
4. **F1** = 2 * Precision * Recall / (Precision + Recall)  — output `0.00` if Precision+Recall = 0

Round all four values to **2 decimal places**.

## Input Format

```
N
predicted: p1 p2 ... pN
actual:    a1 a2 ... aN
```

- First line: integer `N` (number of samples).
- Second line: `predicted:` followed by N space-separated integers (0 or 1).
- Third line: `actual:` followed by N space-separated integers (0 or 1).

## Output Format

Four lines:
```
accuracy: X.XX
precision: X.XX
recall: X.XX
f1: X.XX
```

## Example

**Input:**
```
10
predicted: 1 0 1 1 0 1 0 0 1 0
actual:    1 0 1 0 0 1 0 1 1 0
```

**Confusion matrix:**
- TP=4 (positions 0,2,5,8: predicted=1, actual=1)
- TN=4 (positions 1,4,6,9: predicted=0, actual=0)
- FP=1 (position 3: predicted=1, actual=0)
- FN=1 (position 7: predicted=0, actual=1)

**Output:**
```
accuracy: 0.80
precision: 0.80
recall: 0.80
f1: 0.80
```
