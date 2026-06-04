# Index Selectivity Analyzer

In MongoDB, index selectivity determines how useful an index is for a given query. Compute the selectivity of a field and classify its quality.

## Input Format

```
N
value1
value2
...  (N values total)
```

- Line 1: integer N.
- Next N lines: one string value per line (the field values from a collection sample).

## Output Format

One line:

```
selectivity:<ratio> quality:<LEVEL>
```

Where:

- `ratio` = `unique_count / N`, rounded to **2 decimal places**.
- `LEVEL` is one of:
  - `HIGH` if ratio >= 0.8
  - `MEDIUM` if ratio >= 0.5
  - `LOW` if ratio < 0.5

## Example

**Input:**
```
10
Alice
Bob
Alice
Charlie
Alice
Bob
Dave
Eve
Alice
Bob
```

**Output:**
```
selectivity:0.50 quality:MEDIUM
```

Explanation: 10 total values, 5 unique (Alice, Bob, Charlie, Dave, Eve). 5/10 = 0.50. Threshold 0.50 qualifies as MEDIUM (>= 0.5).

## Notes

- Values are case-sensitive strings.
- N is always >= 1.
- Use standard Python rounding: `round(ratio, 2)` then format with `:.2f`.
