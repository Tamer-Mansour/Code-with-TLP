# CPU Time Calculator

Given an instruction count, CPI, and clock frequency, compute the total CPU execution time in nanoseconds.

## Input

Multiple test cases, one per line. Each line contains three space-separated values:

```
IC CPI freq_GHz
```

Where:
- `IC` = instruction count (positive integer)
- `CPI` = average cycles per instruction (positive float)
- `freq_GHz` = clock frequency in GHz (positive float)

## Output

For each line, print the CPU execution time in nanoseconds, rounded to 4 decimal places.

## Formula

```
CPU_time_ns = IC × CPI × (1 / freq_GHz)
```

## Example

```
Input:
1000 2.0 2.0
500 1.5 3.0

Output:
1000.0
250.0
```

Explanation for line 1: `1000 × 2.0 × (1/2.0) = 1000.0 ns`.
Explanation for line 2: `500 × 1.5 × (1/3.0) = 250.0 ns`.
