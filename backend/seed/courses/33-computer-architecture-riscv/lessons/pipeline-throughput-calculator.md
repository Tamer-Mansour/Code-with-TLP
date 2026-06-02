# Exercise: Compute Cycles for N Instructions in a Pipeline

In this exercise you will implement a pipeline cycle calculator. Given the parameters of a pipelined processor and a workload description, your program must compute the exact number of cycles required to execute N instructions and the resulting CPI.

## What You Will Implement

You will read a set of pipeline parameters from standard input and write the total cycle count and CPI to standard output.

The formula for total cycles in a k-stage pipeline executing N instructions with an average of s stall cycles per instruction is:

```
total_cycles = (k - 1) + N * (1 + s)
```

Where:
- `k` is the number of pipeline stages
- `N` is the number of instructions
- `s` is the average number of stall cycles per instruction (a decimal value)
- `(k - 1)` is the pipeline fill cost (ramp-up)

The CPI is:

```
CPI = total_cycles / N
```

Round `total_cycles` to the nearest integer. Print CPI rounded to 2 decimal places.

## Input Format

Three lines:
1. An integer `k` — number of pipeline stages
2. An integer `N` — number of instructions
3. A float `s` — average stall cycles per instruction

## Output Format

Two lines:
1. `Cycles: <integer>`
2. `CPI: <float with 2 decimal places>`

## Example

**Input:**
```
5
1000
0.4
```

**Output:**
```
Cycles: 1404
CPI: 1.40
```

## Getting Started

Think about:
- How the pipeline fill cost (`k - 1`) is a one-time cost at the start
- How each instruction contributes `1 + s` cycles on average
- Edge cases: what if N = 1? What if s = 0?

The solution must read from standard input and write to standard output only. No file I/O or third-party libraries.
