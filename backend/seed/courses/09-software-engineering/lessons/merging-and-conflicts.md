# Merging, Rebasing, and Resolving Conflicts

Once you have a feature branch, you need to integrate it back into `main`. Git offers several strategies, each with trade-offs that affect your history readability, rollback ability, and team workflow.

## Merging

A **merge** combines two branches by creating a new "merge commit" that has two parents.

```bash
git checkout main
git merge feature/login
# Merge made by the 'ort' strategy.
#  auth/login.py | 42 +++++++++++++++++++++++++++++++
#  1 file changed, 42 insertions(+)
```

If both branches edited different files, Git merges automatically. If the same lines were changed on both sides, you get a **merge conflict**.

### Fast-Forward Merge

When `main` has not moved since you branched off, Git just moves the `main` pointer forward — no merge commit is created.

```
Before:  A──B  ← main
              \
               C──D  ← feature

After fast-forward: A──B──C──D  ← main, feature
```

Force a merge commit even when fast-forward is possible (preferred in many teams for a clear history of when features landed):

```bash
git merge --no-ff feature/login
# Creates: A──B──────M  ← main
#               \   /
#                C──D
```

### When to Use `--no-ff`

Most teams use `--no-ff` for feature branches so that:
1. The feature's commits appear as a single group in `git log --graph`
2. Rolling back a feature is a single `git revert <merge-commit-hash>`
3. `git log` clearly shows when each feature landed on `main`

However, for very small changes (single-commit fixes), fast-forward keeps history cleaner.

## Rebasing

**Rebase** replays your branch commits on top of the target branch, rewriting their parent pointers:

```bash
git checkout feature/login
git rebase main
# First, rewinding head to replay your work on top of it...
# Applying: feat: add login form
# Applying: feat: add JWT validation
```

```
Before:  A──B──E  ← main (E is a new commit added since we branched)
              \
               C──D  ← feature

After rebase: A──B──E──C'──D'  ← feature (C' and D' are new commit objects)
```

C and D have been replaced by C' and D' with new SHA hashes. The content is the same; the history is different. The result is a perfectly linear history — as if you had created the branch from E, not B.

**Benefits of rebase:** linear `git log`, cleaner `git bisect`, easier for code reviewers to understand the progression.

**Golden rule of rebasing:** never rebase commits that have already been pushed to a shared remote branch. Rewriting public history creates divergence for everyone who pulled the old commits. If you must "redo" a shared branch, coordinate with your team first.

### Interactive Rebase

`git rebase -i` lets you rewrite your own branch history before pushing:

```bash
git rebase -i HEAD~3   # rewrite the last 3 commits
```

This opens an editor showing:
```
pick a1b2c3 feat: add login form
pick d4e5f6 wip: half-done validation
pick 789abc fix typo in comment
```

You can change `pick` to:
- `squash` (or `s`) — combine with previous commit
- `reword` (or `r`) — edit the commit message
- `drop` (or `d`) — delete the commit
- `edit` (or `e`) — stop and amend the commit

A common workflow: squash multiple "WIP" commits into one clean commit before opening a PR.

## Resolving Merge Conflicts

A conflict marker looks like this in the affected file:

```python
<<<<<<< HEAD
    return user.email
=======
    return user.username
>>>>>>> feature/login
```

- Everything between `<<<<<<< HEAD` and `=======` is the current branch's version
- Everything between `=======` and `>>>>>>>` is the incoming branch's version

Steps to resolve:
1. Open the file and edit it to the correct final state (remove all three marker lines)
2. Stage the resolved file: `git add auth/user.py`
3. Complete the merge: `git commit` (message pre-filled)

**Tools that help:**
- `git mergetool` — launches a 3-way diff tool (vimdiff, meld, p4merge)
- VS Code's built-in merge editor shows three panes (current, incoming, result)
- `git diff --conflict=diff3` — shows the common ancestor as a third column for context

**Choosing which side is correct** often requires reading both branches' intent and sometimes consulting the author. Never blindly accept one side without understanding what the other side changed and why.

## Pull Requests (PRs) in Depth

A **pull request** (or "merge request" on GitLab) is not a Git concept — it is a feature of hosting platforms (GitHub, GitLab, Bitbucket). It requests that a branch be merged and provides a structured space for code review, CI status, and discussion.

### Anatomy of a Good PR

```markdown
## What changed
Added password reset endpoint and email delivery via SendGrid.
Three new files: `auth/reset.py`, `tests/test_reset.py`, email template.

## Why
Closes #142 — users were permanently locked out after forgetting a password.

## Testing
- Unit tests in tests/test_reset.py: 12 tests, all passing
- Manually tested reset flow in staging environment
- Confirmed email arrives within 5 seconds, token expires after 1 hour

## Screenshots
[Attach screenshot of reset email if applicable]
```

PR best practices:
- Keep PRs small: ≤400 lines changed is a widely cited guideline; smaller PRs get faster, better reviews
- One concern per PR: don't bundle a feature and a refactor in the same PR
- Pass all CI checks before requesting review
- Link to the ticket/story so reviewers have context
- Self-review the diff before assigning reviewers — you will catch 20% of issues yourself

### Stacked PRs

For large features, use **stacked PRs** (also called "stacked diffs"):

```
main ← PR-1 (base changes) ← PR-2 (builds on PR-1) ← PR-3 (final layer)
```

Each PR is reviewed independently. When PR-1 merges, PR-2 is rebased onto `main` automatically. This keeps individual PRs reviewable while enabling parallel progress.

## Stashing Work in Progress

If you need to switch branches without committing unfinished work:

```bash
git stash               # save working directory changes and staged changes
git stash push -m "half-done login validation"  # named stash
git checkout main
# ... do other work ...
git stash pop           # restore the most recent stash (and drop it from stash list)
git stash list          # see all stashes
# stash@{0}: On feature/login: half-done login validation
# stash@{1}: WIP on main: b12d441 feat: ...
git stash apply stash@{1}  # restore a specific stash without removing it
git stash drop stash@{0}   # delete a specific stash
```

## Key Commands Summary

| Command | Effect |
|---|---|
| `git merge <branch>` | Merge branch into current (auto fast-forward if possible) |
| `git merge --no-ff` | Force a merge commit |
| `git rebase <branch>` | Replay commits on top of branch (linear history) |
| `git rebase -i HEAD~N` | Interactively rewrite last N commits |
| `git cherry-pick <hash>` | Apply a single commit from another branch |
| `git stash` / `pop` | Temporarily shelve uncommitted changes |
| `git diff --staged` | Review staged changes before commit |
| `git log --oneline --graph` | Visual branch history |
