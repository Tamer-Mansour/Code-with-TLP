# Git Hooks — Automating Quality Gates

Git hooks are shell scripts that run automatically at specific points in the Git workflow. They live in `.git/hooks/` and fire before or after operations like commit, push, and merge. Use them to enforce quality standards, run tests, or block bad commits at the source.

## How hooks work

Git looks for executable scripts in `.git/hooks/<hook-name>`. If the script exits with a non-zero code, Git aborts the operation (for pre-hooks). Post-hooks run after the fact and cannot abort the operation.

```bash
ls .git/hooks/
# applypatch-msg    pre-applypatch  pre-rebase
# commit-msg        pre-commit      pre-receive
# post-commit       prepare-commit-msg  update
# post-merge        pre-push
```

The `.sample` extension is stripped before Git recognizes a hook. To activate the sample:

```bash
cp .git/hooks/pre-commit.sample .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit   # on Linux/macOS
```

## Common hooks

| Hook | When it runs | Common uses |
|------|-------------|-------------|
| `pre-commit` | Before commit message entry | Lint, format, run fast tests |
| `commit-msg` | After message is written | Enforce message format |
| `pre-push` | Before `git push` | Run full test suite |
| `post-merge` | After a merge/pull | `npm install` if package.json changed |
| `post-checkout` | After branch switch | Rebuild environment |

## Example: pre-commit hook

```bash
#!/bin/sh
# .git/hooks/pre-commit

# Run Python linter on staged .py files
STAGED=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')

if [ -n "$STAGED" ]; then
    echo "Running flake8..."
    flake8 $STAGED
    if [ $? -ne 0 ]; then
        echo "Lint errors found. Fix them before committing."
        exit 1
    fi
fi

exit 0
```

## Example: commit-msg hook

Enforce a conventional commit prefix (`feat:`, `fix:`, `docs:`, etc.):

```bash
#!/bin/sh
# .git/hooks/commit-msg

MSG=$(cat "$1")
PATTERN="^(feat|fix|docs|style|refactor|test|chore|ci)(\(.+\))?!?: .{1,72}"

if ! echo "$MSG" | grep -qE "$PATTERN"; then
    echo "ERROR: Commit message must start with a type (feat, fix, docs, etc.)"
    echo "  Example: feat: add user authentication"
    exit 1
fi
```

## Sharing hooks with your team

`.git/hooks/` is not tracked by Git (`.git/` is never committed). To share hooks:

1. **Store hooks in a versioned directory** (e.g., `scripts/hooks/`) and document how to install them.
2. **Use a tool like [pre-commit](https://pre-commit.com/)** (Python-based, config via `.pre-commit-config.yaml`).
3. **Configure `core.hooksPath`** to point to a tracked directory:

```bash
mkdir -p .githooks
cp .git/hooks/pre-commit .githooks/pre-commit
git config core.hooksPath .githooks
git add .githooks/
git commit -m "chore: add shared git hooks"
```

Now everyone who clones the repo and runs `git config core.hooksPath .githooks` (or you automate this in a setup script) shares the same hooks.

## Using the pre-commit framework

The `pre-commit` tool manages hooks as plugins:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
```

```bash
pip install pre-commit
pre-commit install    # installs the hook into .git/hooks/pre-commit
pre-commit run --all-files   # run manually
```

This approach handles hook installation, versioning, and cross-platform compatibility much better than raw shell scripts.

## Bypassing hooks (use sparingly)

```bash
git commit --no-verify -m "WIP: skip hooks"
git push --no-verify
```

Bypass only when you have a genuine reason (e.g., an emergency fix). Never make bypassing the norm — it defeats the purpose of having hooks.
