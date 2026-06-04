# Exercise: Build a .gitignore Matcher

The `.gitignore` file is one of the first things you configure in any project. It tells Git which files and directories to skip when you run `git add` or `git status`. Without it, build artifacts, dependency folders, secrets, and OS metadata would constantly appear as untracked files cluttering your output.

## How .gitignore works

Each line in `.gitignore` is a pattern. When Git checks whether to track a file, it evaluates the file's path against all applicable patterns. The most common pattern types are:

| Pattern | Meaning |
|---------|---------|
| `*.log` | Any file ending in `.log` |
| `__pycache__` | Exact filename or directory name match |
| `.env` | Exact filename |
| `# comment` | Ignored (comment line) |
| *(blank line)* | Ignored |

Key insight: **adding a file to `.gitignore` after it is already tracked does nothing**. You must first untrack it with `git rm --cached <file>`, then ignore it. This is a common mistake covered in detail in *Pro Git*, Chapter 2.

## What you are building

Implement a simplified version of Git's ignore matching logic. You will be given a list of patterns followed by a list of file paths, and you must output only the paths that would be **ignored**.

## Why this matters

`.gitignore` matching is often misunderstood — developers frequently wonder why their pattern "isn't working." Writing a matcher from scratch forces you to think precisely about what each pattern type actually tests, which builds the intuition to debug real `.gitignore` files.

## Supported pattern types (for this exercise)

1. **Wildcard extension**: `*.ext` — matches any file whose name ends with `.ext`
2. **Exact name**: any other pattern matches if the basename of the path equals the pattern exactly, OR if the full path equals the pattern exactly

## Input format

```
<pattern1>
<pattern2>
...
                  ← blank line separator
<filepath1>
<filepath2>
...
```

Lines starting with `#` and blank lines in the pattern section are comments/separators and must be ignored.

## Output format

Print each ignored file path on its own line, in input order.

## Example

Input:
```
# Python cache
*.pyc
*.log
__pycache__
.env

src/main.py
src/app.pyc
logs/error.log
src/__pycache__
README.md
.env
build/output.log
```

Output:
```
src/app.pyc
logs/error.log
src/__pycache__
.env
build/output.log
```

## Further reading

- *Pro Git* — gitignore: https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository#_ignoring
- gitignore specification: https://git-scm.com/docs/gitignore
