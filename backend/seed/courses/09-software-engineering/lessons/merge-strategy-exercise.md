# Exercise: Fast-Forward or Merge Commit?

Understanding when Git can fast-forward is a key Git skill. In this exercise you will analyse branch states and determine the correct merge strategy.

## Task

You are given a series of test scenarios. Each scenario describes two branch states as a sequence of commit IDs. The `main` branch has a base, and the `feature` branch diverges from some point. Determine whether a **fast-forward** merge is possible or whether a **merge commit** is required.

Read scenarios from standard input. Each scenario is one line with this format:

```
<main_commits> | <feature_commits>
```

- `main_commits` is a space-separated list of commit IDs on `main` (in order from oldest to newest).
- `feature_commits` is a space-separated list of commit IDs on the feature branch **starting from the point of divergence** (not including the shared base).

A **fast-forward** is possible when `main` has not moved since the feature branch was created — i.e., the last commit on `main` is the commit that the feature branch diverged from (the feature branch starts right after main's tip).

More precisely: fast-forward is possible when `main_commits` is a proper prefix of `(main_commits + feature_commits)`, meaning `feature_commits` begins where `main` ends with no new commits on `main` after the branch point.

For simplicity in this problem: fast-forward is possible if and only if there are **no new commits on main** after the feature branch was created. We model this as: `feature_commits` are all new (not in `main_commits`), AND `main_commits` has not grown since branching — i.e., the last commit ID in `main_commits` does NOT appear in `feature_commits` (they don't share new work), and **`main_commits` ends at the branch point**.

## Simplified Rule for This Problem

Print `fast-forward` if `main_commits` and `feature_commits` share NO commit IDs (they are disjoint), meaning main hasn't advanced beyond what feature branched from.

Print `merge-commit` if any commit ID appears in both lists (main has advanced after the branch point, causing divergence).

## Example

**Input:**
```
A B C | D E
A B C X | D E
A | B
A B | B C
```

**Output:**
```
fast-forward
merge-commit
fast-forward
merge-commit
```

Explanation:
- Line 1: main=[A,B,C], feature=[D,E] — disjoint → fast-forward
- Line 2: main=[A,B,C,X], feature=[D,E] — disjoint → fast-forward... wait, re-read: X is only on main, D/E only on feature. Still disjoint.

Actually this problem uses a simpler deterministic rule — see the prompt for the exact specification.
