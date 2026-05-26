# Branching Workflows: GitFlow and Trunk-Based Development

A branching strategy is a team agreement about which branches exist, what they mean, how long they live, and how code moves between them. Choosing the wrong strategy for your team's release cadence causes constant merge pain. This lesson covers the two most widely adopted models.

## Why Branching Strategies Exist

Without a branching strategy, a repository becomes chaotic: hotfixes accidentally land with half-finished features, test environments run different code than production, and "when will this ship?" becomes impossible to answer. A strategy makes the state of the codebase readable from its branch names and history.

## GitFlow

GitFlow was defined by Vincent Driessen in 2010. It uses two permanent branches and three types of short-lived branches.

### Permanent Branches

- **`main`** (or `master`) — always contains production-ready, tagged, released code
- **`develop`** — integration branch; contains finished features waiting for the next release

### Short-Lived Branch Types

| Type | Branches from | Merges into | Naming |
|---|---|---|---|
| Feature | `develop` | `develop` | `feature/login-form` |
| Release | `develop` | `main` + `develop` | `release/1.4.0` |
| Hotfix | `main` | `main` + `develop` | `hotfix/null-pointer-auth` |

### A Complete GitFlow Feature Cycle

```bash
# 1. Start a feature
git checkout develop
git pull
git checkout -b feature/payment-gateway

# 2. Work on the feature (multiple commits)
git commit -m "feat: add Stripe payment intent creation"
git commit -m "feat: add payment confirmation webhook"
git commit -m "test: add unit tests for payment service"

# 3. Merge back to develop
git checkout develop
git merge --no-ff feature/payment-gateway
git push origin develop
git branch -d feature/payment-gateway

# 4. When develop is ready to release, cut a release branch
git checkout -b release/2.3.0 develop

# 5. Only bug fixes on the release branch (no new features)
git commit -m "fix: round tax calculation to two decimal places"

# 6. Finish the release: merge to main AND back to develop
git checkout main
git merge --no-ff release/2.3.0
git tag -a v2.3.0 -m "Release 2.3.0"
git push origin main --tags

git checkout develop
git merge --no-ff release/2.3.0
git branch -d release/2.3.0

# 7. Emergency hotfix on production
git checkout -b hotfix/sql-injection-login main
git commit -m "security: parameterise login query"
git checkout main
git merge --no-ff hotfix/sql-injection-login
git tag -a v2.3.1 -m "Hotfix 2.3.1"
git checkout develop
git merge --no-ff hotfix/sql-injection-login
git branch -d hotfix/sql-injection-login
```

### When GitFlow Works Well

- **Scheduled releases:** software shipped on a monthly or quarterly cycle (mobile apps, packaged software, SaaS with maintenance windows)
- **Multiple versions in production:** when you need to maintain v1.x while developing v2.x
- **Strict QA gates:** release branches give QA a stable target to test without feature churn

### GitFlow's Drawbacks

- `develop` accumulates features and diverges from `main`, making merges painful at release time
- Long-lived feature branches cause integration conflicts
- The overhead (two merges per feature to reach main, plus release + hotfix ceremonies) is high for fast-moving teams
- Vincent Driessen himself added a note to the original post in 2020 recommending trunk-based development for web products that deploy continuously

## Trunk-Based Development (TBD)

**Trunk-based development** has one rule: every developer integrates their work into the main branch (the "trunk") at least once per day. Feature branches exist but live for hours or days, never weeks.

### Core Practices

**Short-lived feature branches (1–2 days max):**
```bash
git checkout -b feature/add-avatar main
# ... commit small, focused changes ...
git push origin feature/add-avatar
# Open PR → review → merge same day
```

**Feature flags** decouple deployment from release:
```python
# Ship the code to production on day 1
# Enable the feature for users on day N

if feature_flags.is_enabled("new-dashboard", user):
    return new_dashboard_view(user)
else:
    return old_dashboard_view(user)
```

This lets you merge incomplete features safely. The code is in production but invisible to users until the flag is turned on. Teams like Google and Facebook use this pattern to ship to production hundreds of times per day.

**Branch by abstraction** for large refactors:
1. Create an abstraction layer (interface/abstract class) that both old and new implementations satisfy
2. Deploy the abstraction with old implementation live
3. Build the new implementation behind the abstraction
4. Switch the abstraction to use the new implementation
5. Remove the old implementation and the abstraction layer

### A Trunk-Based Day

```
09:00  git checkout main && git pull
09:05  git switch -c fix/empty-cart-crash
09:45  git push -u origin fix/empty-cart-crash
10:00  Open PR — CI runs (2 min) — request review
10:20  Review feedback: rename variable. Make change, push.
10:25  CI re-runs — passes. Reviewer approves.
10:30  Merge PR → delete branch
       main is now updated; CI/CD deploys to staging automatically
```

### When TBD Works Well

- **Continuous deployment:** teams deploying to production multiple times per day
- **Small, experienced teams** that can review PRs quickly
- **Web products:** no versioned installations to support; all users run the latest version
- **Strong CI culture:** tests must be fast and comprehensive, or the trunk becomes unstable

### TBD's Requirements

TBD requires discipline: every commit to trunk must leave the codebase in a deployable state. This means:
- A comprehensive automated test suite that runs in under 10 minutes
- Feature flags for any in-progress work
- A culture where unfinished features are always hidden, never broken
- Fast PR review (same-day turnaround)

## GitHub Flow

**GitHub Flow** is a simplified model that works well for most web teams:

1. `main` is always deployable
2. New work is done on descriptively named branches off `main`
3. Push to the remote branch and open a PR early (even as a draft)
4. Merge via PR after review + CI passing
5. Deploy immediately after merging

```
main ──────────────────────────────────→ production
          ↑         ↑         ↑
      feature/X  bugfix/Y  feature/Z
      (merged)   (merged)  (merged)
```

GitHub Flow is not GitFlow. It has no `develop` branch, no release branches, and no explicit hotfix process. It works because `main` is always deployable — a hotfix is just a very small, very fast PR.

## Choosing a Workflow

| Factor | GitFlow | GitHub Flow / TBD |
|---|---|---|
| Release cadence | Scheduled (monthly/quarterly) | Continuous (multiple times/day) |
| Parallel versions | Yes (v1.x, v2.x) | No (everyone on latest) |
| Team maturity | Good for teams learning Git | Requires disciplined CI culture |
| Merge overhead | High (multiple merges per feature) | Low (one PR per feature) |
| Feature hiding | Release branch | Feature flags |

For most modern web applications, GitHub Flow or Trunk-Based Development is the right choice. GitFlow is appropriate when your delivery model involves versioned, packaged releases.

## Tagging Releases

Regardless of workflow, tag your releases so you can identify exactly what is in production:

```bash
git tag -a v2.3.0 -m "Release 2.3.0: payment gateway and avatar upload"
git push origin v2.3.0

git tag                    # list all tags
git show v2.3.0            # see the tag annotation and commit
git checkout v2.3.0        # inspect the exact code that was in that release
```

Semantic versioning (`MAJOR.MINOR.PATCH`) is the convention for tag names — covered in the next lesson.
