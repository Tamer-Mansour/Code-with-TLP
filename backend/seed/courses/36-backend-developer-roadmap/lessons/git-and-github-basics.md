# Git and GitHub Basics

Version control is the foundation of every professional software project. **Git** tracks changes to your files over time, lets you experiment without fear, and makes collaboration with other developers possible. **GitHub** is a cloud platform that hosts Git repositories and adds pull requests, issue tracking, and CI/CD workflows on top.

## Key Concepts

| Term | What it means |
|------|---------------|
| **Repository (repo)** | A directory whose full history Git tracks |
| **Commit** | A snapshot of the project at one point in time |
| **Branch** | An independent line of development |
| **Remote** | A copy of the repo on another machine (e.g., GitHub) |
| **Working tree** | The files you actually see and edit on disk |
| **Staging area (index)** | A holding area where you prepare the next commit |

## The Three-State Model

Every tracked file lives in exactly one of three states:

1. **Modified** — changed on disk but not yet staged.
2. **Staged** — added to the index with `git add`; will be part of the next commit.
3. **Committed** — safely stored in the local repository.

```
Working Tree  ──git add──▶  Staging Area  ──git commit──▶  Local Repo  ──git push──▶  Remote
```

## Your First Repository

```bash
# Initialize a new repo in the current directory
git init my-backend-project
cd my-backend-project

# Tell Git who you are (run once per machine)
git config --global user.name  "Your Name"
git config --global user.email "you@example.com"

# Create a file, stage it, and commit
echo "# Backend Project" > README.md
git add README.md
git commit -m "docs: add initial README"
```

After the commit, `git log --oneline` shows one entry:

```
a1b2c3d docs: add initial README
```

## Connecting to GitHub

Create a new **empty** repository on GitHub (no README, no .gitignore), then link your local repo to it:

```bash
git remote add origin https://github.com/your-username/my-backend-project.git
git branch -M main           # rename default branch to main
git push -u origin main      # push and set upstream tracking
```

From this point forward, `git push` (no arguments) pushes `main` to `origin/main`.

## The Day-to-Day Workflow

```bash
# 1. Check what changed
git status

# 2. Stage specific files (never blindly stage everything)
git add src/Main.java
git add src/model/User.java

# 3. Commit with a meaningful message
git commit -m "feat: add User model with name and email fields"

# 4. Pull any team-mates' changes before pushing
git pull --rebase origin main

# 5. Push your work
git push
```

## Branching and Merging

Working on a feature? Always branch off `main` so your in-progress work does not break the stable baseline.

```bash
# Create and switch to a new branch in one command
git checkout -b feature/login-endpoint

# ... make changes, add, commit ...

# Merge back into main
git checkout main
git merge --no-ff feature/login-endpoint
git push
```

The `--no-ff` flag forces a merge commit even when a fast-forward is possible. This preserves a clear record that a feature branch was integrated.

## A Realistic .gitignore for This Course

Some files must never be committed: compiled class files, IDE project metadata, and secrets.

```
# Java build output
target/
*.class
*.jar

# IntelliJ IDEA
.idea/
*.iml

# VS Code
.vscode/

# Environment / secrets
.env
application-local.properties

# macOS
.DS_Store
```

Save this as `.gitignore` in the root of your project and commit it before you add anything else.

## Conventional Commits

Consistent commit messages make `git log` readable and enable automated changelogs. The **Conventional Commits** format is widely used in Java/Spring projects:

```
<type>: <short description>
```

Common types:

| Type | When to use |
|------|-------------|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation only |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `test` | Adding or updating tests |
| `chore` | Build scripts, dependency updates, tooling |

Examples:

```bash
git commit -m "feat: add GET /api/users endpoint"
git commit -m "fix: handle null pointer in UserService.findById"
git commit -m "chore: add .gitignore for Java and IntelliJ"
```

## Common Mistakes to Avoid

- **Committing build output.** Set up `.gitignore` before your first `git add .`.
- **Giant commits.** Each commit should represent one logical change. Small commits are easier to review and revert.
- **Committing directly to `main`.** Use feature branches and merge (or open a pull request) when working with a team.
- **Pushing credentials.** Never commit passwords, API keys, or database URLs. Use environment variables or a `.env` file that is listed in `.gitignore`.
- **Vague messages.** `"fix stuff"` tells no one anything. Describe the what and the why.

## Checking History

```bash
git log --oneline --graph --all   # visual branch history
git diff HEAD~1 HEAD              # changes in the last commit
git show a1b2c3d                  # full details of one commit
```

---

Git is the single tool you will use every day as a developer. Mastering the add-commit-push cycle and working on feature branches from day one will make every project in this roadmap — and every job you hold afterwards — run more smoothly.
