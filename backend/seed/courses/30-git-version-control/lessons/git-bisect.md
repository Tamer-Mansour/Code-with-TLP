# Git Bisect — Finding the Commit That Broke Things

You notice a bug in the current `main`. You know it worked three weeks ago. There are 200 commits in between. `git bisect` performs a binary search over that commit range, narrowing down the culprit in about eight steps instead of checking all 200.

## How binary search helps

With 200 commits, a linear search is 200 checks in the worst case. Binary search:

```
200 → 100 → 50 → 25 → 13 → 7 → 4 → 2 → 1
```

At most **8 steps** to isolate the first bad commit.

## Starting a bisect session

```bash
git bisect start

# Mark the current HEAD as bad (the bug is present)
git bisect bad

# Mark a known-good commit (the bug was NOT present)
git bisect good v2.1.0
# Bisecting: 99 revisions left to test after this (roughly 7 steps)
# [a1b2c3d4] Add product search feature
```

Git checks out the midpoint commit. You test it and mark it:

```bash
# If the bug IS present in this checkout:
git bisect bad

# If the bug is NOT present:
git bisect good
```

Repeat until Git reports:

```
a1b2c3d4 is the first bad commit
commit a1b2c3d4
Author: Bob <bob@example.com>
Date:   Mon Feb 12 09:12:00 2024

    Refactor payment calculation
```

## End the session

```bash
git bisect reset     # return to original HEAD / branch
```

## Automating bisect with a script

If you have a test script that exits 0 for good and non-zero for bad, bisect can run automatically:

```bash
git bisect start
git bisect bad HEAD
git bisect good v2.1.0

git bisect run python tests/test_payment.py
```

Git will run the script at each midpoint, mark good/bad automatically, and report the first bad commit — no manual steps.

## Skipping untestable commits

Sometimes the midpoint has a compilation error or is otherwise untestable:

```bash
git bisect skip
```

Git picks a nearby commit and continues. If too many commits are skipped, it may report a range rather than a single commit.

## Practical example

```bash
# Scenario: unit tests were passing in v3.0 but fail today
git bisect start
git bisect bad                     # HEAD is broken
git bisect good v3.0               # v3.0 was fine

# Git checks out commit in the middle — you run your test
python -m pytest tests/
# ... FAILED
git bisect bad

# Git checks out another midpoint
python -m pytest tests/
# ... passed
git bisect good

# Repeat a few more times...
# a4b5c6d is the first bad commit
# Commit message: "Change rounding mode in invoice total"
git bisect reset
```

You now know exactly which commit to examine, who wrote it, and what it changed.

## Viewing bisect history

```bash
git bisect log      # full record of your good/bad marks
```

You can save this log and replay the session (`git bisect replay`), useful for documenting a complex bug investigation.

## When bisect shines

| Scenario | Bisect useful? |
|----------|---------------|
| Performance regression over many commits | Yes |
| Visual glitch appeared somewhere in last 500 commits | Yes |
| Test suite is automated | Excellent — use `bisect run` |
| The bug is non-deterministic / flaky | No — results are unreliable |
| Only 3-4 commits to check | Overkill — just check manually |
