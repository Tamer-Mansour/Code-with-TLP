# Sort Semantic Versions

Read semantic version strings from standard input (one per line) and print them sorted in **ascending** order, one per line.

## Rules

- Input: one or more lines, each containing a valid `MAJOR.MINOR.PATCH` version string (e.g. `1.9.5`)
- Output: the same versions, sorted ascending by `(MAJOR, MINOR, PATCH)` as integers
- Duplicates: if the same version appears multiple times in the input, it must appear the same number of times in the output
- Comparison must be numeric, not lexicographic

## Examples

**Input:**
```
1.2.3
2.0.0
1.9.5
2.0.1
```
**Output:**
```
1.2.3
1.9.5
2.0.0
2.0.1
```

---

**Input:**
```
2.10.0
2.9.9
```
**Output:**
```
2.9.9
2.10.0
```
Note: `2.10.0 > 2.9.9` because 10 > 9 numerically.
