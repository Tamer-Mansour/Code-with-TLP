# arch-two-bit-predictor-simulator

## Problem Statement

Simulate a **two-bit saturating counter branch predictor** for a single branch instruction.

The predictor maintains a Branch History Table (BHT) of 2^K entries, all initialized to state `0` (Strongly Not-Taken). Each entry is a 2-bit saturating counter with states:

```
0 = Strongly Not-Taken  → predict N
1 = Weakly Not-Taken    → predict N
2 = Weakly Taken        → predict T
3 = Strongly Taken      → predict T
```

**Update rules:**
- If the actual outcome is Taken (`T`): increment the counter, saturating at `3`.
- If the actual outcome is Not-Taken (`N`): decrement the counter, saturating at `0`.

For this exercise there is exactly **one branch** with `PC = 0`. All N branch events access BHT entry index `0`.

Count the total number of **mispredictions** (cases where the predicted direction differs from the actual direction) and compute accuracy.

## Input Format

```
Line 1: N  — number of branch events (1 ≤ N ≤ 10000)
Line 2: K  — BHT size parameter; the table has 2^K entries (1 ≤ K ≤ 14)
Line 3: N space-separated characters, each 'T' (taken) or 'N' (not-taken)
```

## Output Format

```
Mispredictions: <integer>
Accuracy: <float>%
```

The float is `(correct / N) * 100` rounded to exactly **2 decimal places** (use Python's `round()` or `:.2f` format).

## Constraints

- 1 ≤ N ≤ 10,000
- 1 ≤ K ≤ 14
- Each outcome is exactly the character `T` or `N`
- Use standard input / standard output only
- No third-party libraries

## Sample Input 1

```
10
2
T T T T T T T T T N
```

## Sample Output 1

```
Mispredictions: 3
Accuracy: 70.00%
```

**Trace:**

| # | State | Predict | Actual | Correct? | New State |
|---|-------|---------|--------|----------|-----------|
| 1 | 0     | N       | T      | No       | 1         |
| 2 | 1     | N       | T      | No       | 2         |
| 3 | 2     | T       | T      | Yes      | 3         |
| 4 | 3     | T       | T      | Yes      | 3         |
| 5 | 3     | T       | T      | Yes      | 3         |
| 6 | 3     | T       | T      | Yes      | 3         |
| 7 | 3     | T       | T      | Yes      | 3         |
| 8 | 3     | T       | T      | Yes      | 3         |
| 9 | 3     | T       | T      | Yes      | 3         |
| 10| 3     | T       | N      | No       | 2         |

3 mispredictions, 7 correct → 70.00%

## Sample Input 2

```
8
2
N N N N N N N N
```

## Sample Output 2

```
Mispredictions: 0
Accuracy: 100.00%
```

All branches are not-taken. The BHT starts at state 0 (predict N), which is always correct. Counter stays at 0 throughout.
