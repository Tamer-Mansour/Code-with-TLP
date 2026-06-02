# GitHub Flow — A Lightweight Team Workflow

GitHub Flow is a minimal branching strategy designed for teams that deploy frequently. It has exactly one long-lived branch (`main`), and all work happens in short-lived feature branches merged via pull requests.

## The six steps

```
1. Create a branch from main
2. Commit your changes
3. Open a pull request
4. Discuss and review
5. Merge to main
6. Deploy
```

That is the entire workflow. No release branches, no develop branch, no hotfix process — just `main` and feature branches.

## Step-by-step

### 1. Create a branch

Branch names should be descriptive:

```bash
git switch main
git pull origin main                       # start from the latest
git switch -c feature/user-authentication  # or fix/null-check-payment
```

### 2. Commit regularly

Push early and often — even work-in-progress commits. This backs up your work and signals to teammates what you are working on.

```bash
git add -p                         # stage thoughtfully
git commit -m "feat: add JWT validation middleware"
git push -u origin feature/user-authentication
```

### 3. Open a pull request

Open a PR as soon as you have something to show — even a draft PR:

```
Title:  feat: user authentication with JWT
Body:
  ## What
  Adds JWT-based authentication middleware.

  ## Why
  Fixes #42 — unauthenticated API access.

  ## How to test
  1. Run `pytest tests/test_auth.py`
  2. Manually call GET /api/me without a token — expect 401
```

### 4. Review and iterate

Teammates review the code. You address feedback with new commits — each round of feedback is a commit, not a rewrite of history (reviewers track the delta).

CI runs automatically on every push to the PR branch.

### 5. Merge

Once approved and CI is green, merge to `main`. Options:

| Strategy | Result | Use when |
|----------|--------|----------|
| Merge commit | Preserves all commits + merge commit | Team prefers full history |
| Squash merge | All PR commits become one commit on main | Team prefers clean linear history |
| Rebase merge | PR commits replayed onto main, no merge commit | Team prefers linear without squashing |

GitHub's "Squash and merge" is popular for small features — it keeps `main` history clean.

### 6. Deploy

Because `main` is always deployable, merging to `main` triggers a deployment. Many teams automate this with CI/CD.

## Rules that make it work

1. **`main` is always deployable.** Never merge broken code. CI must be green.
2. **Branches are short-lived.** Aim for 1-3 days; never more than a week. Long branches accumulate conflicts and review fatigue.
3. **Everything is a PR.** No direct pushes to `main` (enforced with branch protection rules on GitHub).
4. **Deploy often.** Frequent small deploys reduce risk per deployment.

## Branch protection rules (GitHub)

In the repository Settings → Branches → Add rule for `main`:

- Require a pull request before merging
- Require status checks to pass (CI)
- Require at least 1 approval
- Dismiss stale pull request approvals when new commits are pushed
- Do not allow bypassing the above settings

## When GitHub Flow is a good fit

- Web applications with continuous deployment
- SaaS products where you ship to one environment
- Small-to-medium teams (2–20 developers)

## When to consider a different workflow

- **Multiple release versions in production simultaneously** (e.g., v1.x and v2.x both supported) → consider Git Flow with release branches.
- **Long release cycles** (quarterly releases) → trunk-based development with feature flags, or Git Flow.
- **Open-source projects with many external contributors** → fork-and-PR model (each contributor forks, opens PR from their fork).
