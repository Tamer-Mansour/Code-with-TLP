# Prompt: Pipeline Cycle Calculator

## Problem Statement

Given the parameters of a k-stage pipeline processor, compute the total number of clock cycles required to execute N instructions and the resulting CPI (Cycles Per Instruction).

Use the following formulas:

```
total_cycles = round((k - 1) + N * (1 + s))
CPI = total_cycles / N
```

Where:
- `k` = number of pipeline stages (integer, >= 2)
- `N` = number of instructions (integer, >= 1)
- `s` = average stall cycles per instruction (float, >= 0.0)
- `(k - 1)` accounts for filling the pipeline before the first instruction completes

## Input Format

Exactly three lines from stdin:
1. Line 1: a single integer `k` (2 <= k <= 100)
2. Line 2: a single integer `N` (1 <= N <= 10,000,000)
3. Line 3: a single float `s` (0.0 <= s <= 10.0)

## Output Format

Exactly two lines to stdout:
1. `Cycles: <total_cycles>` — where total_cycles is rounded to the nearest integer
2. `CPI: <cpi>` — CPI rounded to exactly 2 decimal places

## Constraints

- 2 <= k <= 100
- 1 <= N <= 10,000,000
- 0.0 <= s <= 10.0
- No negative values
- Use standard rounding (round half up, i.e., Python's `round()` function is acceptable)

## Sample Input 1

```
5
1000
0.4
```

## Sample Output 1

```
Cycles: 1404
CPI: 1.40
```

**Explanation:** total_cycles = (5-1) + 1000 * (1 + 0.4) = 4 + 1400 = 1404. CPI = 1404 / 1000 = 1.404, rounded to 2 decimal places = 1.40.

## Sample Input 2

```
3
1
0.0
```

## Sample Output 2

```
Cycles: 3
CPI: 3.00
```

**Explanation:** A single instruction in a 3-stage pipeline takes k=3 cycles. total_cycles = (3-1) + 1*(1+0) = 2+1 = 3. CPI = 3/1 = 3.00.

## Sample Input 3

```
5
100
0.0
```

## Sample Output 3

```
Cycles: 104
CPI: 1.04
```

**Explanation:** Ideal pipeline (no stalls), 5 stages, 100 instructions. total_cycles = 4 + 100 = 104. CPI = 104/100 = 1.04.
