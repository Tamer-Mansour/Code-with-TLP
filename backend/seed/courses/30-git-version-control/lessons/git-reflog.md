# Git Reflog — The Safety Net

The reflog is Git's journal of every position HEAD has been at. Even if you accidentally delete a branch, force-reset to the wrong commit, or lose work in a rebase gone wrong, the reflog lets you find and recover it — as long as it happened in the last 90 days.

## What the reflog is

Every time HEAD or a branch tip moves, Git appends an entry to the reflog:

```bash
git reflog
# 4f3a2b1 (HEAD -> main) HEAD@{0}: commit: Add user filter
# a1b2c3d HEAD@{1}: rebase (finish): returning to refs/heads/main
# 9c8d7e6 HEAD@{2}: rebase (pick): Fix typo in README
# 3e4f5g6 HEAD@{3}: rebase (start): checkout origin/main
# b2c3d4e HEAD@{4}: commit: WIP login form
# c5d6e7f HEAD@{5}: checkout: moving from feature/auth to main
```

`HEAD@{N}` is a way to reference past HEAD positions. `HEAD@{0}` is the current position; `HEAD@{1}` is where you were before the last move.

## Recovering a lost commit after `reset --hard`

```bash
# Disaster: you reset away work you needed
git reset --hard HEAD~3

# Find the lost commits in reflog
git reflog
# 4f3a2b1 HEAD@{0}: reset: moving to HEAD~3
# 7d8e9f0 HEAD@{1}: commit: Add payment module   ← this is the "lost" commit

# Restore by creating a branch at that commit
git branch recovery 7d8e9f0
git switch recovery
```

Or just move main back directly:

```bash
git reset --hard 7d8e9f0
```

## Recovering a deleted branch

```bash
# Accidentally deleted feature/auth
git branch -D feature/auth

# Find the last commit that was on that branch
git reflog | grep 'feature/auth'
# 9c8d7e6 HEAD@{7}: checkout: moving from feature/auth to main

git branch feature/auth 9c8d7e6   # recreate the branch
```

## Recovering after a bad rebase

Rebase rewrites commits. If the rebase produced bad results:

```bash
# Before rebase HEAD was at this commit
git reflog
# HEAD@{5}: rebase (start): checkout main   ← the SHA just before rebase started

git reset --hard HEAD@{5}   # go back to pre-rebase state
```

## Reflog for a specific branch

```bash
git reflog show main          # reflog for main branch
git reflog show feature/auth  # reflog for that branch
```

## Reflog expiry

Entries expire after 90 days by default (30 days for unreachable commits). The clock starts from when you ran the command that moved HEAD. For critical recovery, act promptly.

```bash
git config --global gc.reflogExpire "180 days"      # extend if desired
```

## Reflog vs. git log

| | `git log` | `git reflog` |
|---|---|---|
| Shows | Commits reachable from current HEAD | Every position HEAD has ever been |
| After branch delete | Deleted commits disappear | Commits still appear |
| After reset --hard | Prior commits not visible | Prior commits still visible |
| Useful for | Normal history browsing | Disaster recovery |

## Key takeaway

Before panicking about lost work, always run `git reflog`. In the vast majority of "I've destroyed my commits" situations, the data is still in `.git/objects` and the reflog tells you exactly where to find it.
