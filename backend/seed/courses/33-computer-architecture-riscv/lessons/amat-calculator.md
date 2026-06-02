# Exercise: Compute Average Memory Access Time

In this exercise you will implement an **AMAT (Average Memory Access Time) calculator** for a multi-level memory hierarchy. Given parameters for each cache level and main memory, your program will compute the AMAT in cycles using the recursive nesting formula.

## What You Will Implement

Your program reads a description of a memory hierarchy from stdin and prints the AMAT rounded to two decimal places.

The hierarchy is described level by level from L1 (closest to CPU) down to main memory. Each cache level has:
- A **hit time** (cycles paid on every access that reaches this level)
- A **local miss rate** (fraction of accesses that reach this level but miss, expressed as a percentage)

Main memory has only a latency (no miss rate — it always hits).

## The Formula

For a single cache level with hit time `H`, local miss rate `m`, and the effective cost of a miss `P`:

```
AMAT = H + (m / 100) × P
```

where `P` is the AMAT of the next level down.

For main memory alone, `AMAT = latency`.

The formula nests from the bottom up:
1. Start with `AMAT = DRAM_latency`
2. For each cache level from innermost (closest to DRAM) to outermost (L1):
   - `AMAT = hit_time + (miss_rate / 100) × AMAT`

## Input Format

```
N
H_1 MR_1
H_2 MR_2
...
H_N MR_N
DRAM_latency
```

- First line: integer `N` — number of cache levels (1 ≤ N ≤ 5)
- Next `N` lines: two space-separated numbers for each level from L1 to LN
  - `H_i`: hit time in cycles (integer)
  - `MR_i`: local miss rate as a percentage (float, 0–100)
- Last line: DRAM latency in cycles (integer)

## Output Format

Print a single line:

```
AMAT: X.XX cycles
```

where `X.XX` is the AMAT rounded to exactly two decimal places.

## Sample Input

```
2
2 8.0
10 40.0
100
```

## Sample Output

```
AMAT: 6.00 cycles
```

**Explanation:**
- Start with DRAM: AMAT = 100
- Apply L2: AMAT = 10 + (40/100) × 100 = 10 + 40 = 50
- Apply L1: AMAT = 2 + (8/100) × 50 = 2 + 4 = 6.00

## Constraints

- 1 ≤ N ≤ 5
- 1 ≤ hit_time ≤ 1000 (cycles)
- 0.0 ≤ miss_rate ≤ 100.0 (percent)
- 1 ≤ DRAM_latency ≤ 10000 (cycles)
- All inputs are valid and within range
