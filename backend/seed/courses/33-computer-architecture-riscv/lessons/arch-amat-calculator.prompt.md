# Prompt: Compute Average Memory Access Time (AMAT)

## Problem Statement

Given a description of a multi-level memory hierarchy, compute the **Average Memory Access Time (AMAT)** in cycles.

The AMAT formula nests from the innermost level (closest to main memory) outward to L1:

```
AMAT_bottom = DRAM_latency
AMAT_level  = hit_time + (miss_rate / 100) × AMAT_next_level
```

Start with main memory latency, then apply each cache level from the deepest cache up to L1.

## Input Format

```
N
H_1 MR_1
H_2 MR_2
...
H_N MR_N
DRAM_latency
```

- Line 1: integer `N` — number of cache levels (1 ≤ N ≤ 5); L1 is listed first, LN is listed last.
- Lines 2 to N+1: `H_i MR_i` — hit time (integer cycles) and local miss rate (float percent) for cache level i.
- Line N+2: integer DRAM latency in cycles.

## Output Format

```
AMAT: X.XX cycles
```

Print exactly two decimal places. Use standard rounding (round half up or Python's built-in `round()`).

## Constraints

- 1 ≤ N ≤ 5
- 1 ≤ H_i ≤ 1000
- 0.0 ≤ MR_i ≤ 100.0
- 1 ≤ DRAM_latency ≤ 10000

## Sample Input 1

```
2
2 8.0
10 40.0
100
```

## Sample Output 1

```
AMAT: 6.00 cycles
```

**Derivation:**
- AMAT = 100 (DRAM)
- Apply L2: 10 + (40/100) × 100 = 50.0
- Apply L1: 2 + (8/100) × 50.0 = 6.00

## Sample Input 2

```
1
4 5.0
200
```

## Sample Output 2

```
AMAT: 14.00 cycles
```

**Derivation:**
- AMAT = 200 (DRAM)
- Apply L1: 4 + (5/100) × 200 = 4 + 10 = 14.00

## Sample Input 3

```
3
4 5.0
12 30.0
45 20.0
250
```

## Sample Output 3

```
AMAT: 6.03 cycles
```

**Derivation:**
- AMAT = 250 (DRAM)
- Apply L3: 45 + (20/100) × 250 = 45 + 50 = 95.0
- Apply L2: 12 + (30/100) × 95.0 = 12 + 28.5 = 40.5
- Apply L1: 4 + (5/100) × 40.5 = 4 + 2.025 = 6.025 → 6.03
