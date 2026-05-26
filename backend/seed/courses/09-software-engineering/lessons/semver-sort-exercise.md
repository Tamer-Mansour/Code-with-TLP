# Exercise: Sort Semantic Versions

Sorting version strings requires numeric comparison of each component, not lexicographic string comparison. In this exercise you will read a list of SemVer strings and output them in ascending order (lowest version first).

## Why This Matters

Package managers, release pipelines, and changelogs all need to sort version numbers. A naive alphabetical sort produces wrong results: `"2.10.0"` would sort before `"2.9.0"` because `"1"` < `"9"` lexicographically. Correct SemVer sorting compares each of the three numeric components independently.

## Problem

Read semantic version strings (one per line) from standard input and print them sorted in **ascending order**, one per line.

You may assume:
- All inputs are valid `MAJOR.MINOR.PATCH` strings with non-negative integer components
- There will be at least one version
- Versions may repeat; duplicates should appear in the output as many times as they appear in the input

## Example

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

## Hints

- `str.split('.')` splits a version into its three parts
- `sorted(..., key=...)` with a key function avoids modifying the original strings
- Convert each component to `int` for comparison
