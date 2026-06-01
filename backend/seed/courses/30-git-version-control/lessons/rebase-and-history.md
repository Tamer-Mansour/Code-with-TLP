# Rebase and Rewriting History

`git rebase` rewrites commits onto a different base. Used carefully it produces cleaner, more readable history; used carelessly it corrupts shared branches.

## What rebase does

```
before:
        A — B — C   (feature)
       /
  --- M — X — Y     (main)

git switch feature
git rebase main

after:
                A' — B' — C'   (feature)
               /
  --- M — X — Y                (main)
```

Git replays A, B, C **as new commits** (A', B', C' have different SHAs) on top of Y.

## Why rebase

- Linear history is easier to read with `git log --oneline --graph`.
- Bisecting (finding a bug commit) works better on linear history.
- No "Merge branch 'main' into feature" pollution.

## When NOT to rebase

**Never rebase commits you've pushed to a shared branch.** Other people's clones still point to the old SHAs; rebasing diverges your history from theirs, and the next `git pull` produces ugly duplicate commits.

Rule: rebase your own private branch as much as you like; merge once it's public.

## Interactive rebase

The power feature: edit, reorder, squash, or drop commits before they're shared.

```bash
git rebase -i HEAD~5             # last 5 commits
git rebase -i main               # all commits since main
```

You'll see:

```
pick a1b2c3 Add filter
pick d4e5f6 fix typo
pick 7g8h9i WIP
pick j0k1l2 actually fix the bug
pick m3n4o5 cleanup
```

Edit to:

```
pick a1b2c3 Add filter
fixup d4e5f6 fix typo            (merge into previous, drop message)
squash 7g8h9i WIP                (merge into previous, combine messages)
fixup j0k1l2 actually fix the bug
pick m3n4o5 cleanup
```

Operations:

- `pick` — keep as-is.
- `reword` — change the message.
- `edit` — pause to modify the commit's content.
- `squash` — merge into previous, combine messages.
- `fixup` — merge into previous, drop this message.
- `drop` — discard.
- Reorder lines to reorder commits.

Save, exit, Git rewrites the history. Result: one or two clean commits ready for review.

## Continuing/aborting

```bash
git rebase --continue
git rebase --abort
git rebase --skip
```

If a conflict appears mid-rebase, resolve like a merge conflict, `git add` the files, `git rebase --continue`.

## Cherry-pick

Replay a single commit onto a different branch:

```bash
git switch hotfix-branch
git cherry-pick <sha>
```

Great for backporting bug fixes between maintenance branches.

## Amend the last commit

```bash
git commit --amend                # update message
git commit --amend --no-edit      # keep message, add staged changes
```

This is technically a tiny rebase — it creates a new commit replacing the previous one. Don't amend a commit you've pushed.

## Reflog — the safety net

Every move HEAD makes is logged for 90 days:

```bash
git reflog
ab12cd HEAD@{0}: rebase finished: returning to refs/heads/feature
1f2e3d HEAD@{1}: rebase: Add filter
4d5c6b HEAD@{2}: checkout: moving from main to feature
```

To recover a "lost" commit:

```bash
git reset --hard HEAD@{3}
# or
git branch recovered HEAD@{3}
```

If you can find the SHA, you can resurrect it. **Reflog has saved careers.**

## A pull-request rebase workflow

```bash
git switch feature
git pull --rebase main           # keep feature current with main
git rebase -i main               # squash WIP commits before review
git push --force-with-lease      # safer than --force
```

`--force-with-lease` refuses to overwrite if someone else pushed to the branch since you fetched. Use it instead of `--force`.

## Squash merge (alternative)

GitHub's "Squash and merge" button does an equivalent server-side: feature branch commits become one commit on main. Many teams prefer this — feature authors don't need to learn interactive rebase, and main history stays clean. The trade: you lose the granular commit history of the feature work.
