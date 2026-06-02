# Prompt: Compute Effective Access Time From Hit Ratios

## Problem Statement

Given a series of memory system scenarios, compute the Effective Memory Access Time (EMAT) for each one using the standard TLB formula:

```
EMAT = h * t_mem + (1 - h) * (k + 1) * t_mem
```

Where:
- `h` = TLB hit ratio (a decimal between 0.0 and 1.0 inclusive)
- `t_mem` = time for one memory access in nanoseconds (positive integer)
- `k` = number of page-table levels (positive integer, 1–4)

Output each EMAT rounded to exactly **two decimal places**.

## Input Format

```
N
h1 t_mem1 k1
h2 t_mem2 k2
...
hN t_memN kN
```

- First line: integer `N` (1 ≤ N ≤ 100), the number of scenarios.
- Next `N` lines: three space-separated values per line: `h` (float), `t_mem` (int), `k` (int).

## Output Format

Print `N` lines. Each line contains the EMAT for the corresponding scenario, formatted to exactly two decimal places.

## Constraints

- 1 ≤ N ≤ 100
- 0.0 ≤ h ≤ 1.0
- 1 ≤ t_mem ≤ 10,000
- 1 ≤ k ≤ 4

## Sample Input

```
4
0.95 100 2
0.99 80 4
0.80 100 2
0.00 100 2
```

## Sample Output

```
110.00
83.20
140.00
300.00
```

## Explanation

Formula applied to each scenario (`EMAT = h*t + (1-h)*(k+1)*t`):

- Scenario 1: `0.95×100 + 0.05×3×100 = 95.00 + 15.00 = 110.00`
- Scenario 2: `0.99×80  + 0.01×5×80  = 79.20 + 4.00  = 83.20`
- Scenario 3: `0.80×100 + 0.20×3×100 = 80.00 + 60.00 = 140.00`
- Scenario 4: `0.00×100 + 1.00×3×100 = 0.00  + 300.00 = 300.00`
