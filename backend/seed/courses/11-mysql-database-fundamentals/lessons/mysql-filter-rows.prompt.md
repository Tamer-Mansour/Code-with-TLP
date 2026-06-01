# WHERE-style Row Filter

Read a small CSV from stdin and print the header plus all rows whose `age` column is strictly greater than a threshold. This mirrors `SELECT * FROM t WHERE age > :n;`.

## Input

- Line 1: comma-separated header, always containing a column named `age`.
- Line 2: integer threshold.
- Lines 3..N: data rows, comma-separated, in the same column order as the header.

## Output

- Print the header line unchanged.
- Then print each row whose `age` value is strictly greater than the threshold, **in the original order**.
- If no rows match, print only the header.

## Example

Input:

```
id,name,age
25
1,Alice,30
2,Bob,22
3,Carol,40
```

Output:

```
id,name,age
1,Alice,30
3,Carol,40
```

## Constraints

- 1 ≤ rows ≤ 10000
- `age` fits in a 32-bit integer.
- Other columns are arbitrary strings without commas.
