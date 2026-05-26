# Exercise: Calculate Test Coverage Percentage

Test coverage tools report how many lines of source code are executed by the test suite. In this exercise you will compute the coverage percentage from raw line counts.

## Problem

Each test run produces two numbers on a single line: the total number of executable lines in the codebase, and the number of those lines that were actually executed by the tests. Compute the **coverage percentage** for each test run, rounded to one decimal place.

Coverage is defined as:
```
coverage = (covered_lines / total_lines) * 100
```

If total lines is 0, output `"N/A"` for that run.

## Input Format

One test run per line: `<total_lines> <covered_lines>`

## Output Format

One result per line. Print the percentage rounded to one decimal place followed by a `%` sign, or `N/A` if total is 0.

## Example

**Input:**
```
200 160
500 450
100 100
0 0
```

**Output:**
```
80.0%
90.0%
100.0%
N/A
```
