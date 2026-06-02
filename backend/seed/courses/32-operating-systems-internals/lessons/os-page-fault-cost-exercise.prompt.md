# Prompt: Compute Effective Access Time With Page Faults

## Problem

The **Effective Memory Access Time (EAT)** formula is:

```
EAT = (1 - p) × mem_time + p × page_fault_time
```

Given multiple memory-access scenarios, compute the EAT for each one and output it rounded to the nearest integer (standard rounding: 0.5 rounds up).

## Input format

- The first line contains a single integer **N** (1 ≤ N ≤ 1000): the number of scenarios.
- Each of the next N lines contains three space-separated values:
  - `p` — a floating-point number (0.0 ≤ p ≤ 1.0) representing the page-fault rate.
  - `mem_time` — an integer (1 ≤ mem_time ≤ 10,000) representing the normal memory access time in nanoseconds.
  - `page_fault_time` — an integer (1 ≤ page_fault_time ≤ 100,000,000) representing the total time to handle one page fault in nanoseconds.

## Output format

For each scenario, output one integer on its own line: the EAT rounded to the nearest nanosecond.

## Constraints

- No third-party libraries. Use only the Python standard library.
- `p` will have at most 10 decimal digits.
- All outputs fit in a 64-bit integer.

## Sample input

```
6
0.0 100 8000000
1.0 100 8000000
0.001 100 8000000
0.5 200 10000000
0.0001 150 5000000
0.01 100 20000000
```

## Sample output

```
100
8000000
8100
5000100
650
200099
```

## Explanation of sample cases

| p | mem_time | page_fault_time | EAT calculation | Result |
|---|---|---|---|---|
| 0.0 | 100 | 8000000 | 1.0×100 + 0.0×8000000 = 100.0 | 100 |
| 1.0 | 100 | 8000000 | 0.0×100 + 1.0×8000000 = 8000000.0 | 8000000 |
| 0.001 | 100 | 8000000 | 0.999×100 + 0.001×8000000 = 99.9+8000 = 8099.9 | 8100 |
| 0.5 | 200 | 10000000 | 0.5×200 + 0.5×10000000 = 100+5000000 = 5000100.0 | 5000100 |
| 0.0001 | 150 | 5000000 | 0.9999×150 + 0.0001×5000000 = 149.985+500 = 649.985 | 650 |
| 0.01 | 100 | 20000000 | 0.99×100 + 0.01×20000000 = 99+200000 = 200099.0 | 200099 |
