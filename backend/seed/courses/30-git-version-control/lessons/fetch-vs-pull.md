# Fetch vs. Pull — Understanding Remote Synchronization

`git fetch` and `git pull` are both about downloading changes from a remote, but they behave very differently. Confusing them is one of the most common sources of "why is my history a mess?" complaints.

## The mental model

```
Remote repo  ──────►  Remote-tracking branch  ──────►  Local branch
              fetch                              merge or rebase
             (safe)                               (pull does both)
```

- **`git fetch`** downloads new objects and updates your remote-tracking refs (`origin/main`, `origin/feature`, etc.) but **never touches your local branches**.
- **`git pull`** is `git fetch` followed immediately by an integration step (merge or rebase) on the current branch.

## git fetch

```bash
git fetch origin             # fetch all branches from origin
git fetch origin main        # fetch only origin/main
git fetch --all              # fetch from every configured remote
git fetch --prune            # also delete remote-tracking refs for deleted remote branches
```

After a fetch, you can inspect what changed before integrating:

```bash
git log HEAD..origin/main --oneline   # commits on origin/main not yet in HEAD
git diff HEAD origin/main             # full diff
```

Only then do you decide how to integrate:

```bash
git merge origin/main         # merge — creates a merge commit if histories diverged
git rebase origin/main        # rebase — replays your commits on top of the fetched state
```

## git pull

```bash
git pull                     # fetch + merge (default)
git pull --rebase            # fetch + rebase (cleaner history)
git pull origin main         # explicitly name remote and branch
```

With `pull.rebase = true` in your config (set in the previous lesson), `git pull` automatically uses rebase instead of merge, avoiding gratuitous merge commits.

## When to prefer fetch + explicit integrate

- On **shared branches** (main, develop): always fetch first, inspect, then decide.
- When you suspect **force pushes** happened on the remote.
- In **CI scripts** where you want separate control of fetch and integration.
- When **reviewing upstream changes** before accepting them into your branch.

## Remote-tracking branches

After a fetch, remote-tracking branches are updated:

```bash
git branch -r          # list remote-tracking branches
# origin/main
# origin/feature/auth
# origin/HEAD -> origin/main

git log origin/main    # browse the remote's history without being on it
git checkout -b local-feature origin/feature/auth   # create local branch tracking a remote one
```

## Tracking relationships

```bash
git branch -vv
# * main  4f3a2b1 [origin/main: ahead 1] Add user filter
#   dev   9c8d7e6 [origin/dev] Update README
```

`ahead 1` means you have 1 local commit not yet pushed. `behind N` means the remote has N commits you have not fetched yet.

Set up tracking when creating a branch:

```bash
git push -u origin feature/login    # -u = --set-upstream
```

After this, plain `git push` and `git pull` know where to push/pull without specifying the remote and branch name.

## Summary comparison

| | `git fetch` | `git pull` |
|---|---|---|
| Downloads remote objects | Yes | Yes |
| Updates remote-tracking refs | Yes | Yes |
| Touches local branch | **No** | **Yes** |
| Safe to run any time | Yes | Careful |
| Good default for shared branches | Yes | With `--rebase` |
