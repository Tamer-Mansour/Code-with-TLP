# Branches, Merges, and Conflicts

A branch is a pointer to a commit. Creating one is free; using them well is a skill.

## Creating and switching

```bash
git branch                        # list local
git branch -a                     # include remote
git branch feature                # create (don't switch)
git checkout feature              # switch
git switch feature                # newer alias for checkout

git switch -c feature             # create + switch
git checkout -b feature           # older equivalent

git branch -d feature             # delete (refuses if unmerged)
git branch -D feature             # force delete
```

Modern Git: prefer `git switch` for branches, `git restore` for files. `git checkout` does both and is hence confusing.

## Merging

```bash
git switch main
git merge feature
```

Two outcomes:

1. **Fast-forward** — main has no new commits since feature branched off. Git just moves main's pointer forward. No merge commit.
2. **Three-way merge** — both branches have moved on. Git creates a **merge commit** with two parents combining the work.

Force a merge commit even when FF would work (preserves branch context):

```bash
git merge --no-ff feature
```

## Conflicts

When the same lines have been edited differently, Git can't auto-merge. You'll see:

```
<<<<<<< HEAD
your version
=======
their version
>>>>>>> feature
```

Edit the file, remove the markers, keep what you want, then:

```bash
git add file.py
git commit                        # finalizes the merge commit
git merge --abort                 # bail out
```

## Conflict tools

```bash
git mergetool                     # configured GUI (e.g., VS Code, Beyond Compare)
git config --global merge.tool vscode
git config --global mergetool.vscode.cmd 'code --wait $MERGED'
```

For tricky conflicts, **resolve in your editor with rich syntax highlighting**, not in raw diff markers.

## Diff in 3-way style

```bash
git config --global merge.conflictstyle diff3
```

Now conflict blocks include the **common ancestor** too — far easier to understand both sides.

## A typical workflow

```bash
git switch main
git pull
git switch -c feature/add-export
# ... do work, commit a few times ...
git push -u origin feature/add-export
# open PR, get review, fix, push more
git switch main
git pull
git merge feature/add-export       # or merge via the PR
git branch -d feature/add-export
```

## When to rebase instead of merge

If you've created commits on your feature branch that haven't been pushed, **rebasing onto main** (instead of merging main into feature) keeps history linear:

```bash
git switch feature
git rebase main
```

Now your commits sit on top of the latest main with no merge commit. We cover rebase next.

## Merge strategies (advanced)

```bash
git merge -X ours feature         # on conflicts, keep "our" side automatically
git merge -X theirs feature       # opposite
git merge -s ours feature         # whole merge, ignore feature's changes
git merge --squash feature
git commit -m "feature: ..."      # squashed into one commit on main
```

`--squash` is popular for "feature branch with messy WIP commits" — the final main history has one clean commit per feature.

## Common confusion

- `git branch -d` doesn't fail at the file level; it only enforces "merged into current branch."
- `git checkout <file>` (in pre-2.23 Git) discards changes — dangerous, use `git restore <file>` now.
- A branch that "disappears" usually still exists — `git reflog` and `git log <sha>` will find it.
