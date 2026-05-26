# Calculate Test Coverage Percentage

Read pairs of numbers from standard input representing test coverage data. For each pair, compute the coverage percentage.

## Input Format

One line per test run: `<total_lines> <covered_lines>`

Both values are non-negative integers. `covered_lines` will never exceed `total_lines`.

## Output Format

One result per line:
- If `total_lines > 0`: print the coverage percentage rounded to **one decimal place**, followed by `%` (e.g. `80.0%`, `100.0%`, `73.5%`)
- If `total_lines == 0`: print `N/A`

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

## Notes

- `round(x, 1)` in Python rounds to one decimal place
- Do not print extra spaces or trailing characters
