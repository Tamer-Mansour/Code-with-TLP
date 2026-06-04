# Exercise: Version Control Commit Log Analyzer

Understanding your team's commit history is a fundamental project management and DevOps skill. Commit logs reveal defect density, contributor workload distribution, and the ratio of feature work to maintenance — all key inputs for retrospectives, sprint planning, and risk assessment.

**Brooks' Law** reminds us that adding developers to a late project makes it later: new team members take time to onboard, and communication overhead grows as N×(N−1)/2. Commit log analysis can help you see *who* is contributing what, and whether the team's effort is being spent on the right things.

**Free resource:** *Software Engineering: A Modern Approach* — [softengbook.org](https://softengbook.org/) — Chapter 10 covers DevOps practices including CI/CD and version control strategies.

## Task

You are given a simplified commit log. Each commit has the format:

```
COMMIT_ID AUTHOR DATE LINES_ADDED LINES_REMOVED MESSAGE_TYPE
```

`MESSAGE_TYPE` is one of: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

Compute and print three sections:

1. **Total commits by each author** — sorted alphabetically by author name
2. **Net lines changed per commit type** — `lines_added − lines_removed`, sorted by type name
3. **The author with the most `fix` commits** — a proxy for defect density responsibility

## Input Format

- First line: `N` (number of commits)
- Next `N` lines: `COMMIT_ID AUTHOR DATE LINES_ADDED LINES_REMOVED MESSAGE_TYPE`

## Output Format

```
Commits by author:
alice: 3
bob: 2

Net lines by type:
feat: 65
fix: -21

Top fix author: alice
```

Sections are separated by a blank line.

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

## Hints

- Net lines for a type = sum of (lines_added − lines_removed) across all commits of that type.
- Only include types that appear at least once in the log.
- If multiple authors tie for most fix commits, print the one that comes first alphabetically.
