# The Daily Workflow

The commands you'll run hundreds of times a week.

## Starting a project

```bash
git init                          # turn current dir into a repo
git clone <url>                   # download an existing repo
```

## Identity

```bash
git config --global user.name "Alice"
git config --global user.email "alice@example.com"

git config --global init.defaultBranch main
git config --global pull.rebase true       # avoid merge commits on pull
git config --global core.editor "code -w"  # or vim, nano, etc.
```

`--global` writes to `~/.gitconfig`. Drop the flag to set per-repo.

## See what's changed

```bash
git status                        # what's modified/staged
git status -sb                    # short format
git diff                          # working vs staged
git diff --staged                 # staged vs last commit
git diff HEAD                     # working+staged vs last commit
git diff main..feature            # between branches
```

## Stage and commit

```bash
git add file.py                   # specific file
git add -p                        # interactive — review each hunk
git add .                         # everything in current dir
git restore --staged file.py       # unstage

git commit -m "Add user filter"   # message inline
git commit                        # opens editor for longer message
git commit -a -m "..."            # auto-stage modified tracked files (skips new)
git commit --amend                # modify the last commit
```

`git add -p` (patch mode) is a habit-worth-forming. Reviewing each change as you stage catches bugs and creates better commits.

## A commit message worth writing

```
Add filter for active users in admin view

Previously the admin user list showed every user including
soft-deleted ones, making moderation noisy. Add an `is_active`
filter checkbox, default to true.

Fixes #482
```

Convention: 50-char first line (no trailing period), blank line, longer body wrapped at 72.

## See history

```bash
git log
git log --oneline                 # compact
git log --oneline --graph --all   # ASCII graph
git log -p file.py                # diff per commit for this file
git log --since="2 weeks ago"
git log --author="Alice"
git log --grep="bug"              # message contains "bug"
git log -S"def login"             # commits that added or removed this string
git show <sha>                    # show one commit
git blame file.py                 # who wrote each line
```

## Undoing

```bash
# Discard unstaged changes to a file (DANGEROUS — can't recover)
git restore file.py

# Discard ALL unstaged changes
git restore .

# Unstage but keep the changes
git restore --staged file.py

# Undo the last commit, keep changes staged
git reset --soft HEAD~1

# Undo the last commit, unstage (keep changes in working tree)
git reset HEAD~1

# Undo the last commit, throw away changes
git reset --hard HEAD~1           # DANGEROUS

# Make a new commit that reverses a previous one (safe for shared history)
git revert <sha>
```

Rule of thumb: **never `reset --hard` on commits you've pushed to a shared branch**. Use `revert` to make a public undo commit.

## Stashing

```bash
git stash                         # save dirty working tree
git stash pop                     # restore most recent
git stash list
git stash apply stash@{2}
git stash drop stash@{0}
git stash -u                      # include untracked files
```

For "I need to switch branches but my work is mid-flight."

## .gitignore

```
node_modules/
.env
.env.local
dist/
*.log
.DS_Store
__pycache__/
```

Patterns are repo-local. `.gitignore_global` (configured via `core.excludesfile`) covers your personal files.

Once a file is tracked, `.gitignore` won't untrack it — use `git rm --cached file` first.

## Aliases worth setting

```bash
git config --global alias.s "status -sb"
git config --global alias.l "log --oneline --graph --decorate --all"
git config --global alias.co checkout
git config --global alias.last "log -1 HEAD"
```

Now `git s`, `git l`, `git last`.
