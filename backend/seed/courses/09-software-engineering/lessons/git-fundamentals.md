# Git Fundamentals: Repos, Commits, and Branches

Git is a **distributed version control system** — every developer has a full copy of the repository history. It was created by Linus Torvalds in 2005 to manage the Linux kernel source after the team lost access to their proprietary VCS. Today it is the universal standard for source control; understanding it deeply separates confident engineers from developers who treat `git push --force` as a panic button.

## Key Concepts

### Repository

A **repository** (repo) is the database that stores all versions of your project. It lives in the hidden `.git/` folder at the root of your project.

```bash
git init          # create a new repo in the current directory
git clone <url>   # copy a remote repo to your machine (full history included)
```

When you clone, Git creates a remote called `origin` pointing to the source URL and sets up tracking branches so `git push` and `git pull` know where to sync.

### The Three Trees

Git maintains three conceptual areas (sometimes called "the three trees"):

| Area | Description | How to move files |
|---|---|---|
| Working Directory | Files on disk that you edit | Edit in your editor |
| Staging Area (Index) | Files queued for the next commit | `git add <file>` |
| Repository (HEAD) | Committed history (permanent) | `git commit` |

```bash
git add <file>            # stage a specific file
git add -p                # interactive staging — pick hunks to stage
git commit -m "message"   # move staging → repository
git status                # see what is staged / unstaged / untracked
git diff                  # unstaged changes (working dir vs staging)
git diff --staged         # staged changes (staging vs last commit)
```

The staging area is unique to Git and is one of its most powerful features — it lets you craft a clean commit even if your working directory has several unfinished changes.

### Commits

A **commit** is a snapshot of the staged files plus metadata: author, timestamp, and a reference to the parent commit. Commits form a directed acyclic graph (DAG) — the history of your project.

```bash
# Typical sequence: edit → stage → commit
vim auth/login.py
git add auth/login.py
git commit -m "fix: handle null user in login endpoint"

git log --oneline          # compact history
# Output example:
# a3f9c21 fix: handle null user in login endpoint
# b12d441 feat: add password reset via email
# 8e4b210 chore: upgrade dependencies

git show a3f9c21           # inspect a specific commit (diff + metadata)
git diff HEAD~1 HEAD       # diff last two commits
git log --oneline --graph  # ASCII graph of branch history
```

**Anatomy of a good commit message:**

```
fix: handle null user in login endpoint

Null users could reach the auth middleware if the JWT
was signed but the user was deleted from the database.
Added an early return with a 401 response and a log line
so that security teams can monitor unauthorized access.

Closes #347
```

Subject line rules (the "50/72 rule"):
- First line ≤ 72 characters, imperative mood ("add" not "added")
- Blank line separating subject from body
- Body wrapped at 72 characters
- Body explains *why*, not *what* (the diff already shows what)

## Branches

A **branch** is a lightweight, movable pointer to a commit. Creating a branch is nearly instantaneous in Git — it just creates a 41-byte file in `.git/refs/heads/`.

```bash
git branch feature/login    # create a branch at current HEAD
git checkout feature/login  # switch to it (moves HEAD)
# Modern shortcut:
git switch -c feature/login   # create AND switch (git 2.23+)

git branch           # list local branches (* = current)
git branch -v        # show last commit on each branch
git branch -d feature/login   # delete a merged branch
git branch -D feature/login   # force-delete (unmerged changes discarded)
```

Working on a branch means your changes are isolated. The `main` branch can stay stable while experiments happen in parallel.

## A Typical Feature Workflow

Here is a complete sequence showing what actually happens — including the output — when a developer adds a feature:

```bash
# 1. Start from an up-to-date main
git checkout main
git pull
# Output: Already up to date.  (or: Fast-forward, N files changed)

# 2. Create a feature branch
git switch -c feature/password-reset

# 3. Make changes
vim auth/reset.py
vim tests/test_reset.py

# 4. Stage and commit
git add auth/reset.py tests/test_reset.py
git status
# On branch feature/password-reset
# Changes to be committed:
#   modified: auth/reset.py
#   new file:  tests/test_reset.py

git commit -m "feat: add password reset via email

Users were permanently locked out after forgetting their password.
Added a /reset endpoint that sends a time-limited token via SendGrid.
Closes #142"

# 5. Push branch to remote (first time: set upstream)
git push -u origin feature/password-reset
# Enumerating objects: 7, done.
# Branch 'feature/password-reset' set up to track 'origin/feature/password-reset'.

# 6. Open a Pull Request on GitHub/GitLab
# 7. After review approval + CI green, merge via platform UI
# 8. Update local main and clean up
git checkout main
git pull
git branch -d feature/password-reset
```

## Understanding HEAD

`HEAD` is a special pointer that tells Git which commit you are currently working on. It usually points to a branch name, which in turn points to a commit.

```bash
cat .git/HEAD
# ref: refs/heads/main    ← attached to main branch

git checkout HEAD~2   # "detached HEAD": inspect 2 commits back
# Warning: You are in 'detached HEAD' state.

git checkout main     # re-attach to main branch
```

In detached HEAD state you can look around and even make experimental commits, but those commits will be garbage-collected unless you create a branch:

```bash
git switch -c experiment/temp-branch   # save the detached commits
```

## Undoing Changes

```bash
git restore <file>          # discard unstaged changes (working dir → last commit)
git restore --staged <file> # unstage a file (keep changes in working dir)
git revert <hash>           # create a new commit that undoes a previous commit
git reset --soft HEAD~1     # undo last commit, keep changes staged
git reset --mixed HEAD~1    # undo last commit, keep changes unstaged (default)
git reset --hard HEAD~1     # undo last commit, DISCARD changes (destructive!)
```

**Never use `git reset --hard` or `git push --force` on a shared branch.** These rewrite history that other developers have already pulled, causing divergence.

## Git Objects Under the Hood

Git stores four types of objects in `.git/objects/`, content-addressed by SHA-1 hash:

- **blob** — file content (no filename, just bytes)
- **tree** — directory listing (maps filenames to blobs and subtrees)
- **commit** — snapshot + metadata (points to a root tree + parent commits)
- **tag** — named pointer to a commit with optional signed message

```bash
git cat-file -t a3f9c21   # show object type: "commit"
git cat-file -p a3f9c21   # show commit metadata + tree hash
```

This content-addressable model makes Git tamper-evident: changing any byte in any file changes its hash, which changes the tree hash, which changes the commit hash, cascading all the way up. You cannot silently alter history.

## Summary

| Command | Purpose |
|---|---|
| `git init` / `clone` | Set up a repo |
| `git add` / `commit` | Record changes |
| `git log` / `diff` / `show` | Inspect history |
| `git branch` / `switch` | Manage branches |
| `git push` / `pull` / `fetch` | Sync with remote |
| `git restore` / `revert` / `reset` | Undo changes |
| `git stash` | Temporarily shelve work |
