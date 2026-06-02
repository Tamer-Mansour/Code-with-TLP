# Git Stash — Shelving Work in Progress

You are halfway through a feature when an urgent bug lands in your lap. You are not ready to commit, but you need a clean working tree to switch branches. `git stash` is the answer.

## What stash does

`git stash` takes all **modified tracked files** and **staged changes**, bundles them into a hidden commit-like object, and restores your working tree to match `HEAD`. Your work is safe; it is just out of the way.

```bash
git stash            # save dirty state, restore to HEAD
git stash pop        # restore most recent stash (and drop it from the list)
git stash apply      # restore but keep the stash in the list
git stash list       # see all stashes
```

## Basic workflow

```bash
# You are mid-feature on 'feature/login'
git status
# M  src/auth.py

git stash
# Saved working directory and index state WIP on feature/login: 4f3a2 Add user model

git switch main           # clean working tree now
git pull                  # fetch the urgent fix
# ... fix the bug, commit, push ...

git switch feature/login
git stash pop             # your auth.py changes come back
```

## Stash with a message

Plain stash names look like `WIP on feature/login: 4f3a2 Add user model`, which gets hard to read when you have several. Add a description:

```bash
git stash push -m "half-done login form validation"
git stash list
# stash@{0}: On feature/login: half-done login form validation
# stash@{1}: WIP on feature/login: 4f3a2 Add user model
```

## Including untracked files

By default, brand-new files you have never staged are **not** stashed. Use `-u` (or `--include-untracked`) to include them:

```bash
git stash push -u -m "new helper plus edits"
```

## Applying a specific stash

```bash
git stash apply stash@{2}   # apply without dropping
git stash drop  stash@{2}   # manually drop after applying

git stash pop stash@{1}     # apply + drop stash@{1}
```

## Creating a branch from a stash

Sometimes your stash has grown into a real feature. Turn it directly into a branch:

```bash
git stash branch feature/new-thing stash@{0}
# Creates the branch, checks it out, applies stash, drops it — all at once
```

## Stash internals (why it works)

Git stores a stash as a pair of special commits that are not reachable from any branch:

```
refs/stash  →  commit (index state)
                └── commit (working-tree state)
                       └── HEAD at the time of stash
```

Because it is just a commit, you can inspect it:

```bash
git show stash@{0}           # see what the stash changed
git diff stash@{0} HEAD      # compare stash against current HEAD
```

## Common pitfalls

| Situation | What to do |
|-----------|-----------|
| Stash conflicts on pop | Resolve like a merge conflict, then `git stash drop` |
| Forgot `-u`, new files not stashed | `git stash push -u` again on the leftover files |
| Want to stash only one file | `git stash push path/to/file.py` |
| Accidentally dropped a stash | `git fsck --lost-found` can sometimes recover orphaned objects |

## When not to use stash

Stash is for **short-term** parking. If you park work for more than a few hours, consider committing it as a WIP commit (`git commit -m "WIP: login form"`). A WIP commit is visible to teammates, backed up when pushed, and avoids the "what was that stash again?" problem.
