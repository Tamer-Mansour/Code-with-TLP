# Amdahl's Law Speedup Calculator

Apply **Amdahl's Law** to compute the theoretical speedup of a program when a fraction of its execution is parallelized across N processors, and determine the theoretical maximum speedup as N approaches infinity.

## Amdahl's Law

```
Speedup(N) = 1 / ((1 - P) + P/N)
```

Where:
- `P` is the **parallelizable fraction** of the program (0.0 ≤ P ≤ 1.0)
- `N` is the number of processors
- `1 - P` is the **serial fraction** that cannot be parallelized

As N → ∞, the limit is:

```
Max Speedup = 1 / (1 - P)    (or "Infinite" when P = 1.0)
```

## Input Format

```
Line 1: T — number of test cases (1 <= T <= 10)
Each of the next T lines: P N   (float P, integer N)
```

## Output Format

For each test case, print two lines:

```
Speedup: X.XXX
Max Speedup: Y.XXX
```

(3 decimal places). Use `Infinite` when P = 1.0.

Separate consecutive test cases with a **blank line**.

## Examples

**Input:**
```
3
0.9 10
0.5 100
1.0 8
```

**Output:**
```
Speedup: 5.263
Max Speedup: 10.000

Speedup: 1.980
Max Speedup: 2.000

Speedup: 8.000
Max Speedup: Infinite
```

**Explanation:**

- Case 1: P=0.9, N=10. Speedup = 1/((0.1) + (0.9/10)) = 1/(0.1 + 0.09) = 1/0.19 ≈ 5.263. Max = 1/0.1 = 10.000.
- Case 2: P=0.5, N=100. Speedup = 1/(0.5 + 0.005) ≈ 1.980. Max = 1/0.5 = 2.000. The serial half caps speedup at 2x no matter how many processors are added.
- Case 3: P=1.0, N=8. Speedup = 1/(0 + 1/8) = 8.000 exactly. Max = Infinite (no serial fraction).

## Common Misconception

More cores does NOT mean proportional speedup. If 10% of a program is serial (P=0.9), the maximum possible speedup is **10×**, regardless of whether you use 100 or 1,000,000 processors. This is the fundamental lesson of Amdahl's Law.

## Hints

- Use Python's built-in float arithmetic.
- To avoid floating-point edge cases, compare `P == 1.0` exactly for the Infinite case.
- Print a blank line between test cases (not after the last one).
