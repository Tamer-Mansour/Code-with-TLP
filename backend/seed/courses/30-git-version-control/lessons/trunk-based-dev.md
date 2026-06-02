# Trunk-Based Development

Trunk-based development (TBD) is a source-control practice where all developers commit to a single shared branch — the "trunk" (`main`) — at least once a day. Feature branches, if used at all, live for hours or a few days, never weeks.

## Core idea

Instead of long-lived feature branches that diverge for weeks and cause painful merge sessions, everyone integrates continuously. The trunk is always in a releasable state because unfinished features are hidden behind **feature flags**, not kept in a private branch.

## Comparison with GitHub Flow

| | GitHub Flow | Trunk-Based Development |
|---|---|---|
| Long-lived branches | Only `main` | Only `main` |
| Feature branches | Up to a week | Hours to 2 days max |
| Integration frequency | On PR merge | At least daily, often per-commit |
| Unfinished feature isolation | Keep on branch | Feature flags |
| PR requirement | Yes | Optional (pair programming as alternative) |

## Feature flags

A feature flag (also called feature toggle) is a boolean condition that controls whether new code runs:

```python
# config.py
FEATURE_NEW_DASHBOARD = os.getenv("FEATURE_NEW_DASHBOARD", "false") == "true"

# views.py
if settings.FEATURE_NEW_DASHBOARD:
    return render_new_dashboard(request)
else:
    return render_legacy_dashboard(request)
```

The code is deployed to production, but the feature is off for everyone until you flip the flag. This means:

- Developers integrate continuously (no merge conflicts from long-lived branches)
- QA can test in production with the flag on for specific users
- Rollback is instant — flip the flag off, no redeployment needed

## Short-lived branches in TBD

Even in TBD, most teams use short branches for code review:

```bash
git switch -c feat/add-cache-header   # create branch
# ... make 1-3 commits ...
git push origin feat/add-cache-header
# Open PR, get review, merge same day
```

The key constraint: **merge before the branch is a day or two old**. If it takes longer, the feature is too big — split it.

## Making it work

### Commit-ready code always

Every commit to `main` must:
- Pass CI (all tests green)
- Not break existing behavior
- Be deployable (feature flags hide incomplete work)

### Continuous integration (CI) is mandatory

Without automated tests, you cannot commit to `main` frequently with confidence. CI runs on every push and blocks merges on failure.

### Small, atomic commits

```bash
# Bad: one giant commit at the end of a week
git commit -m "Add new dashboard"    # 2000-line diff

# Good: incremental commits each day
git commit -m "feat: add dashboard route and empty view"
git commit -m "feat: add dashboard data fetching"
git commit -m "feat: add dashboard chart component"
git commit -m "feat: enable new-dashboard flag in staging"
```

### Pair programming as an alternative to PRs

Some TBD teams skip PRs entirely and use pair programming for code review. With two people reviewing in real time, you skip the async review cycle and integrate immediately.

## Advantages of TBD

- **No merge hell** — integrating daily means conflicts are small and frequent, not large and rare.
- **True continuous delivery** — `main` is always releasable, so you can deploy at any time.
- **Faster feedback** — bugs from your change surface within hours, not weeks later when the branch finally merges.
- **Less work in progress** — small batches reduce risk per change.

## Disadvantages and challenges

- Requires strong CI discipline — no CI means broken `main`.
- Feature flags add complexity (you must clean them up after full rollout).
- Requires a culture shift — developers used to long branches resist the change.
- Code review pressure: quick turnaround needed so branches stay short.

## When to choose TBD

- High-frequency deployment (multiple times per day)
- Mature CI/CD pipeline with high test coverage
- Team is experienced and disciplined
- You want the fastest possible feedback loops
