# Remotes, push, pull, PRs

A **remote** is a named pointer to another copy of the repository — usually hosted on GitHub, GitLab, Bitbucket, or your own Gitea/Forgejo.

## Listing and adding remotes

```bash
git remote -v                              # list with URLs
git remote add origin git@github.com:me/proj.git
git remote add upstream https://github.com/up/proj.git
git remote rename origin myorigin
git remote remove old
```

Convention:
- `origin` — the remote you push to.
- `upstream` — for forks, the original repo.

## Fetch, pull, push

```bash
git fetch                                  # download remote refs, don't merge
git fetch origin
git fetch --all --prune                    # all remotes, drop deleted branches

git pull                                   # fetch + merge (or rebase)
git pull --rebase origin main              # explicit rebase

git push                                   # upload current branch
git push -u origin feature/x                # first push + set upstream
git push origin --delete feature/x          # delete remote branch
```

`fetch` is **non-destructive** — it never modifies your branches. `pull` is `fetch` followed by `merge` (or `rebase`).

## Tracking branches

After `-u`, your local branch is **tracking** the remote one. `git status` will tell you "ahead by 2 commits" or "behind by 1." Plain `git pull` and `git push` know what to do.

```bash
git branch -vv                              # see tracking
git branch -u origin/main main             # set tracking manually
```

## SSH vs HTTPS

```
git@github.com:me/proj.git           # SSH (key-based)
https://github.com/me/proj.git        # HTTPS (PAT or credential helper)
```

SSH is convenient once your key is set up (`~/.ssh/id_ed25519.pub` uploaded to GitHub). HTTPS works through firewalls but needs a credential helper (`git config --global credential.helper osxkeychain` / `manager`).

## Pull requests (the typical flow)

GitHub didn't invent it but popularized it. The shape:

1. Fork (if external) or clone the repo.
2. Branch: `git switch -c feature/x`.
3. Make changes, commit.
4. Push: `git push -u origin feature/x`.
5. Open a PR on GitHub from `feature/x` to `main`.
6. Code review, tests run, push more commits as feedback comes.
7. Merge (via the PR's button).
8. Delete the feature branch.

## Anatomy of a good PR

- **Title** — imperative, < 70 chars. "Add export to CSV", not "exports".
- **Description** — what / why / how to test. Link to the issue.
- **Small** — 100-line PRs get reviewed; 1000-line PRs get rubber-stamped.
- **Tests included** — features ship with the test that proves they work.
- **One concern** — refactors separate from features, separate from formatting.

## GitHub flow vs Git flow

**GitHub flow** — one long-lived branch (`main`), short-lived feature branches, deploy on every merge. Simple. Right for most teams.

**Git flow** — `main`, `develop`, `feature/*`, `release/*`, `hotfix/*`. Heavier, made for shrink-wrapped software with version releases. Overkill for web apps.

**Trunk-based** — minimize branches, integrate frequently to main, feature flags hide incomplete work. Used by big engineering orgs (Google, Facebook).

For most teams: GitHub flow.

## Force-push with safety

Never push `--force` blindly. Use `--force-with-lease`:

```bash
git push --force-with-lease
```

It refuses if someone else pushed since your last fetch. Prevents you from overwriting their work.

For `main`/`master`, configure GitHub's **branch protection** to refuse force-pushes entirely.

## Tags and releases

```bash
git tag v1.0.0                              # lightweight
git tag -a v1.0.0 -m "First release"        # annotated (preferred)
git push origin v1.0.0
git push --tags                             # all tags
git tag -d v0.9                              # delete locally
git push origin :v0.9                        # delete remotely
```

GitHub auto-creates a Release from a tag — pair with a `CHANGELOG.md` for users.

## Hooks (briefly)

Client-side hooks in `.git/hooks/` (e.g., `pre-commit`, `commit-msg`). For shareable hooks, use **pre-commit** (`pre-commit.com`) — a framework that runs linters/formatters on commit, configured per repo.

Server-side hooks live on the hosting platform's side (GitHub Actions, GitLab CI).
