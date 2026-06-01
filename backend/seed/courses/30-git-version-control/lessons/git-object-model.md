# The Git Object Model

Git is a content-addressable filesystem with a version-control interface on top. Once you understand the four object types and what a branch really is, everything else becomes mechanical.

## Four object types

Stored in `.git/objects/`, addressed by SHA-1 (or SHA-256 in newer Git) of their contents.

- **Blob** — a file's contents (no filename, no path).
- **Tree** — a directory: mappings of name → mode + (blob or sub-tree).
- **Commit** — points to one tree (the snapshot), plus parent commit(s), author, timestamp, message.
- **Tag** — annotated tag: points to an object with its own author and message.

```
commit  4f3a2…
  tree 9b8c7…           ← the root directory at this commit
  parent 1e2d3…         ← (zero or more parents)
  author Alice <a@x.com> 1700000000 +0000
  
  Refactor user auth
```

Each commit is a **snapshot** of the whole tree, not a diff. Diffs are computed when you ask for them.

## A branch is just a pointer

```
.git/refs/heads/main → 4f3a2…
```

A branch is a one-line file containing a commit SHA. Creating a branch is `cp main feature` — instant.

When you commit, Git creates a new commit object and updates the current branch to point at it.

```
HEAD → branch → commit → tree → blobs
```

`HEAD` is `.git/HEAD`, usually `ref: refs/heads/main`. **Detached HEAD** means HEAD points to a commit directly, not a branch.

## Why commits are immutable

A commit's SHA is computed from its contents (tree + parent + author + message). Change anything and the SHA changes. That's why "rewriting history" creates new commits — the old ones still exist (until garbage collected); they just no longer have a branch pointing at them.

## Inspect the model

```bash
git cat-file -p HEAD                  # commit object
git cat-file -p HEAD^{tree}            # tree
git cat-file -p HEAD:README.md        # blob

git log --oneline --graph --decorate --all
git rev-parse HEAD                     # SHA of HEAD
git show 4f3a2                          # commit + diff
```

## The three areas

```
[ working tree ] ──git add──► [ staging (index) ] ──git commit──► [ repository ]
```

- **Working tree** — files on disk you can edit.
- **Index** (a.k.a. staging area) — proposed next commit.
- **Repository** — committed history (objects + refs).

```bash
git status              # show all three
git diff                # working vs index
git diff --staged       # index vs HEAD
git diff HEAD           # working vs HEAD
```

## Why this matters

Once you internalize "commits are snapshots, branches are pointers, history is a DAG of commits," advanced operations stop being scary:

- **Merge** creates a commit with two parents.
- **Rebase** copies commits onto a different parent.
- **Cherry-pick** replays a commit's diff onto another branch.
- **Reset** moves the branch pointer to a different commit.
- **Reflog** is the safety net — every move HEAD made for the last 90 days, recoverable.

The rest of this course is mostly applying these primitives.
