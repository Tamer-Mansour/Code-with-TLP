# Git Submodules — Embedding One Repo Inside Another

A submodule is a Git repository embedded inside another Git repository. The parent ("super") repo records a pointer to a specific commit in the child repo — not the child's files, just the commit SHA. This lets you version-pin an external dependency while keeping the two histories separate.

## When to use submodules

- Sharing a common library between multiple projects, where you want to pin each project to a specific version of the library.
- Embedding a third-party open-source tool with a specific version.
- Monorepo-like setups where independent teams own separate repos but a parent repo ties them together.

**Alternatives to consider first:** package managers (npm, pip, Maven), Git subtree, or a build-time vendoring script. Submodules add complexity — use them only when the above alternatives genuinely do not fit.

## Adding a submodule

```bash
git submodule add https://github.com/example/shared-lib.git libs/shared-lib
```

This creates two things:
1. A directory `libs/shared-lib/` containing the cloned repo.
2. A `.gitmodules` file (tracked) with the URL and path.

```ini
# .gitmodules
[submodule "libs/shared-lib"]
    path = libs/shared-lib
    url = https://github.com/example/shared-lib.git
```

The parent repo records only the commit SHA of `libs/shared-lib`, not the files inside it.

## Cloning a repo that has submodules

```bash
# Option 1: clone then initialize
git clone https://github.com/your-org/main-repo.git
cd main-repo
git submodule update --init --recursive

# Option 2: clone with submodules in one step
git clone --recurse-submodules https://github.com/your-org/main-repo.git
```

Without `--recurse-submodules`, the submodule directories are empty after cloning.

## Updating a submodule to a newer commit

```bash
cd libs/shared-lib
git fetch
git checkout v2.1.0        # or a specific SHA
cd ../..
git add libs/shared-lib    # stage the updated pointer
git commit -m "chore: bump shared-lib to v2.1.0"
```

Other developers then run `git submodule update --init --recursive` to pull the updated version.

## Common submodule commands

```bash
git submodule status             # show current SHA for each submodule
git submodule update --remote    # pull the latest from each submodule's tracked branch
git submodule foreach git pull   # run git pull inside every submodule
```

## Key pitfalls

| Pitfall | What happens | Prevention |
|---------|-------------|------------|
| Forget `--recurse-submodules` on clone | Submodule dirs are empty | Add alias or document in README |
| Commit submodule changes without updating parent | Team gets wrong version | Always `git add <submodule-path>` in parent after updating |
| Submodule is in detached HEAD | Commits inside are lost after `git submodule update` | Create a branch inside the submodule before committing |
| Circular submodule dependency | Infinite recursion on init | Never create circular references |

## Removing a submodule

There is no single `git submodule remove` command. The manual steps:

```bash
git submodule deinit -f libs/shared-lib     # remove from .git/config
rm -rf .git/modules/libs/shared-lib         # remove cached state
git rm -f libs/shared-lib                   # remove the directory + .gitmodules entry
git commit -m "chore: remove shared-lib submodule"
```

## Submodules vs. git subtree

| | Submodule | Subtree |
|---|---|---|
| History | Separate | Merged into parent history |
| Files visible in parent | No (just a pointer) | Yes (copied in) |
| Update workflow | `git submodule update` | `git subtree pull` |
| Complexity | Higher | Lower |
| Suited for | External repos you don't modify often | Repos you want to easily contribute back to |

For most internal shared-library use cases, subtree is simpler. Choose submodules when you want a clear boundary and a pinned external dependency.
