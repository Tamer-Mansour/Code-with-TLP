# Highest Semantic Version

Given a list of semantic version strings (one per line, format `MAJOR.MINOR.PATCH`), output the highest version on a single line.

**Input format:** One version string per line until EOF.

**Output format:** A single version string — the highest one.

**Example:**

Input:
```
1.2.3
2.0.0
1.9.5
2.0.1
```

Output:
```
2.0.1
```

Versions compare numerically by major, then minor, then patch. `1.9.0` < `1.10.0`.
