# Exercise: Highest Semantic Version

Semantic versioning (SemVer) is used in almost every project to tag releases. Given a list of version strings, you need to find the highest one.

## Task

Read a list of semantic version strings (one per line) from standard input. Each version has the format `MAJOR.MINOR.PATCH` where each part is a non-negative integer. Output the highest version on a single line.

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
2.0.1
```

## Notes

- There is always at least one version string.
- Versions compare numerically, not lexicographically (so `1.9.0` > `1.10.0` is **false** — `1.10.0` wins).
- No pre-release suffixes (no `-alpha`, `-rc1`, etc.).
