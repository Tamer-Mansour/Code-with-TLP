# Fast-Forward or Merge Commit?

When merging a feature branch into main, Git can use a fast-forward merge only if `main` has not advanced since the feature branch was created. Otherwise, a merge commit is required.

You are given a series of scenarios. Each line contains two comma-separated integers:
- `main_new`: the number of commits added to `main` after the feature branch was created
- `feature_commits`: the number of commits on the feature branch

If `main_new == 0`, print `fast-forward`.
Otherwise, print `merge-commit`.

**Input:** One scenario per line (two integers separated by a comma) until EOF.

**Output:** One line per scenario: `fast-forward` or `merge-commit`.

**Example:**

Input:
```
0,3
2,1
0,1
5,0
```

Output:
```
fast-forward
merge-commit
fast-forward
merge-commit
```
