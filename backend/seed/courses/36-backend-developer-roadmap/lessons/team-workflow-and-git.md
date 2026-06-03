# Team Workflow and Git Collaboration

Solo projects let you work however you like. The moment a second developer joins, you need an agreed workflow so that two people are never editing the same lines at the same time, every change is reviewed before it lands in the shared codebase, and the history remains readable six months later. This lesson covers the Git-based team practices you will encounter in every professional Java/Spring shop.

## Branching Strategy: Git Flow vs. Trunk-Based Development

| Strategy | Main idea | Best for |
|---|---|---|
| **Git Flow** | Long-lived `main` + `develop` branches; `feature/*`, `release/*`, `hotfix/*` branches | Teams with scheduled release cycles |
| **Trunk-Based Development** | Everyone integrates to `main` at least daily; feature flags hide unfinished work | Teams shipping continuously (CI/CD pipelines) |
| **GitHub Flow** | Single `main` branch + short-lived feature branches; every feature goes through a Pull Request | Small teams, open-source projects |

For most Spring Boot projects in a team of 2–6 developers, **GitHub Flow** is the right default — it is simple, keeps history clean, and enforces code review without overhead.

## GitHub Flow in Practice

```bash
# 1. Always start from an up-to-date main
git checkout main
git pull origin main

# 2. Create a short-lived feature branch — name it by ticket or feature
git checkout -b feature/user-registration

# 3. Work in small, focused commits
git add src/main/java/com/tlp/auth/UserService.java
git commit -m "feat: add registerUser with BCrypt password hashing"

git add src/test/java/com/tlp/auth/UserServiceTest.java
git commit -m "test: unit tests for UserService.registerUser"

# 4. Push the branch to the shared remote
git push -u origin feature/user-registration

# 5. Open a Pull Request on GitHub
# 6. Team reviews, approves, and merges — then delete the branch
git checkout main
git pull origin main
git branch -d feature/user-registration
```

Keep feature branches short-lived — aim for less than two days of work on a single branch. Longer branches drift from `main` and produce painful merge conflicts.

## Pull Requests and Code Review

A Pull Request (PR) is a formal proposal to merge one branch into another. On GitHub it gives teammates a structured place to comment, request changes, and approve.

Good PR hygiene:
- **One concern per PR.** Do not mix a refactor, a new feature, and a bug fix in the same PR.
- **Write a meaningful description.** Explain what changed and why, not just how.
- **Keep the diff small.** Aim for under 400 changed lines; large PRs rarely get thorough reviews.
- **Respond to every comment** — even if you just explain why you chose not to change something.

## Handling Merge Conflicts

Conflicts happen when two branches modify the same lines. Git marks the conflict in the file and you resolve it manually.

```bash
# Someone merged to main while you were working; rebase onto the new tip
git fetch origin
git rebase origin/main

# Git pauses when there is a conflict.
# Open the file — you will see markers like this:
```

```
<<<<<<< HEAD (your branch)
        return userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("User not found"));
=======
        return userRepository.findByEmail(email)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND));
>>>>>>> origin/main
```

Edit the file to keep the correct version (or combine both), then:

```bash
git add src/main/java/com/tlp/auth/UserService.java
git rebase --continue
git push --force-with-lease origin feature/user-registration
```

Use `--force-with-lease` instead of `--force`. It refuses to push if someone else has pushed to the branch since you last fetched, protecting against accidental overwrites.

## Protecting the Main Branch

On GitHub, go to **Settings > Branches > Branch protection rules** and enable:

- **Require a pull request before merging** — no direct pushes to `main`.
- **Require approvals** — at least one team member must approve.
- **Require status checks to pass** — your CI build (e.g., `mvn test`) must be green.

This makes it structurally impossible to break `main` by accident.

## A Minimal GitHub Actions CI Pipeline

Every Spring Boot project should run tests automatically on every PR. Create this file in your repository:

```yaml
# .github/workflows/ci.yml
name: Java CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Build and test
        run: ./mvnw -B verify
```

With this in place, GitHub shows a green checkmark (or red X) on every PR before anyone reviews it. Tests that fail on `main` are everyone's top priority.

## Common Mistakes to Avoid

- **Long-lived feature branches.** Rebase against `main` daily to stay current.
- **Merging your own PR without review.** Require at least one approver, even in small teams.
- **Force-pushing to `main`.** It rewrites shared history — everyone's local clone diverges. Always protect `main`.
- **Committing generated files.** `target/`, `.class` files, and `.idea/` belong in `.gitignore`, not in the repo.
- **Vague branch names.** `fix-bug` tells no one anything. Use `fix/null-pointer-in-order-service` or `feature/jwt-authentication`.

---

A disciplined team workflow — short feature branches, mandatory PR reviews, and an automated CI check — is what separates a hobby project from production-grade software. These habits cost almost nothing once they are set up and save enormous time during every future sprint.
