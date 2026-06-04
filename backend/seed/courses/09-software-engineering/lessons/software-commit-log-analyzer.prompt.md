# Version Control Commit Log Analyzer

Given a simplified commit log, compute project metrics.

Each commit has the format:
```
COMMIT_ID AUTHOR DATE LINES_ADDED LINES_REMOVED MESSAGE_TYPE
```

`MESSAGE_TYPE` is one of: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

Compute and print (sections separated by blank lines):

1. Total commits by each author (sorted alphabetically by author name)
2. Net lines changed per commit type (lines_added − lines_removed, sorted by type name; only include types that appear)
3. The author with the most `fix` commits (ties: alphabetically first)

## Input Format

- Line 1: `N`
- Next `N` lines: `COMMIT_ID AUTHOR DATE LINES_ADDED LINES_REMOVED MESSAGE_TYPE`

## Output Format

```
Commits by author:
alice: 3
bob: 2
carol: 1

Net lines by type:
feat: 65
fix: -21
refactor: 12

Top fix author: alice
```

## Example

**Input:**
```
6
c1 alice 2024-01-01 50 10 feat
c2 bob 2024-01-02 5 20 fix
c3 alice 2024-01-03 30 5 feat
c4 alice 2024-01-04 2 8 fix
c5 bob 2024-01-05 15 3 refactor
c6 carol 2024-01-06 10 10 fix
```

**Output:**
```
Commits by author:
alice: 3
bob: 2
carol: 1

Net lines by type:
feat: 65
fix: -21
refactor: 12

Top fix author: alice
```
