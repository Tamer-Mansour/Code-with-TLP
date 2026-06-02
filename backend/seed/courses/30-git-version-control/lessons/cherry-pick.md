# Cherry-Pick — Replaying Individual Commits

Sometimes you want to bring one specific commit from another branch without merging the whole branch. `git cherry-pick` does exactly that: it takes the diff introduced by a commit and applies it as a new commit on your current branch.

## Basic usage

```bash
git cherry-pick <sha>
```

Git computes the diff between `<sha>` and its parent, then applies that diff on top of your current `HEAD`, creating a new commit with the same message (and a new SHA, since the parent changes).

```
Before:
  main:    A - B - C
  hotfix:  A - B - X - Y

git switch main
git cherry-pick Y

After:
  main:    A - B - C - Y'   ← new commit Y', same diff as Y
  hotfix:  A - B - X - Y
```

## Picking a range

```bash
git cherry-pick A..B        # apply commits after A up to and including B
git cherry-pick A^..B       # include A itself
```

Order matters: Git applies commits in the range one by one, oldest first.

## Practical example — backporting a bug fix

You fixed a bug on `main`. Your `release/2.3` branch also needs the fix.

```bash
# Find the commit SHA on main
git log --oneline main | head -5
# a1b2c3d Fix null pointer in payment service

git switch release/2.3
git cherry-pick a1b2c3d
# [release/2.3 f4e5d6c] Fix null pointer in payment service
#  1 file changed, 2 insertions(+), 1 deletion(-)
```

Done. The same fix is now on the release branch without dragging in unrelated changes from `main`.

## Handling conflicts

Cherry-pick can conflict if the context around the changed lines differs between branches:

```bash
git cherry-pick a1b2c3d
# CONFLICT (content): Merge conflict in src/payment.py

# Edit src/payment.py to resolve, then:
git add src/payment.py
git cherry-pick --continue

# OR abandon the cherry-pick:
git cherry-pick --abort
```

## Useful options

| Flag | Effect |
|------|--------|
| `-e` / `--edit` | Open the editor to change the commit message before applying |
| `-n` / `--no-commit` | Apply the diff but do not commit; lets you combine multiple picks |
| `-x` | Append `(cherry picked from commit <sha>)` to the message for traceability |
| `--signoff` | Add a `Signed-off-by` trailer |

Example with `-x` (recommended for backporting):

```bash
git cherry-pick -x a1b2c3d
# commit message becomes:
# Fix null pointer in payment service
#
# (cherry picked from commit a1b2c3d)
```

## When to cherry-pick vs. merge

- **Cherry-pick:** You want one or a few specific commits; the rest of the source branch is not ready.
- **Merge:** You want everything from the source branch.
- **Rebase:** You want to re-sequence your whole branch onto a new base.

Cherry-picking creates duplicate commits in both branches, which can cause confusion when the source branch is eventually merged. Use it deliberately and prefer a full merge when you intend to integrate the entire branch later.
