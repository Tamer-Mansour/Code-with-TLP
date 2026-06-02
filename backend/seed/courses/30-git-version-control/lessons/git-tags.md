# Git Tags — Marking Releases

Tags are like branches that never move. They point to a specific commit permanently, making them ideal for marking release points: `v1.0.0`, `v2.3.1`, `2024-01-release`.

## Two kinds of tags

| Type | How created | Stored as | Has message/author? |
|------|------------|-----------|---------------------|
| Lightweight | `git tag v1.0` | A ref (pointer) | No |
| Annotated | `git tag -a v1.0 -m "..."` | A full Git object | Yes |

**Prefer annotated tags** for releases. They carry the tagger's name, date, and a message — all useful metadata that lightweight tags lack.

## Creating tags

```bash
# Annotated tag on HEAD
git tag -a v1.0.0 -m "First stable release"

# Annotated tag on a specific commit
git tag -a v0.9.0 abc1234 -m "Beta release"

# Lightweight (no message, not recommended for releases)
git tag v1.0.0-rc1
```

## Listing tags

```bash
git tag             # all tags, alphabetical
git tag -l "v1.*"   # pattern filter
git tag --sort=-version:refname   # sort newest first (semver-aware)
```

## Viewing a tag

```bash
git show v1.0.0
# tag v1.0.0
# Tagger: Alice <alice@example.com>
# Date:   Mon Jan 15 10:30:00 2024
#
# First stable release
#
# commit 4f3a2b1...
# Author: Alice <alice@example.com>
# ...
```

## Pushing tags to a remote

Tags are **not** pushed automatically by `git push`. You must push them explicitly:

```bash
git push origin v1.0.0          # push one tag
git push origin --tags          # push all tags
git push origin --follow-tags   # push only annotated tags reachable from pushed commits
```

`--follow-tags` is the recommended option: it pushes the annotated tags for the commits you just pushed, but skips old or irrelevant tags.

## Deleting tags

```bash
# Delete locally
git tag -d v1.0.0-beta

# Delete on remote
git push origin --delete v1.0.0-beta
```

## Checking out a tag

```bash
git checkout v1.0.0
# Note: switching to 'v1.0.0'.
# You are in 'detached HEAD' state.
```

You are now in detached HEAD. If you want to base new work from this point, create a branch:

```bash
git checkout -b hotfix/1.0.1 v1.0.0
```

## Semantic versioning

Most projects use [SemVer](https://semver.org): `MAJOR.MINOR.PATCH`.

- **MAJOR** — breaking API change
- **MINOR** — new backward-compatible feature
- **PATCH** — backward-compatible bug fix

```bash
v1.0.0   # initial release
v1.1.0   # added a feature
v1.1.1   # patched a bug in 1.1.0
v2.0.0   # breaking change
```

Git's `--sort=-version:refname` understands this ordering:

```bash
git tag --sort=-version:refname | head -5
# v2.0.0
# v1.1.1
# v1.1.0
# v1.0.0
```

## Tags in CI/CD pipelines

Most CI systems can trigger workflows on tag pushes. In GitHub Actions:

```yaml
on:
  push:
    tags:
      - 'v*.*.*'
```

This triggers a release pipeline whenever a SemVer tag is pushed — a clean, explicit way to manage deployments.
