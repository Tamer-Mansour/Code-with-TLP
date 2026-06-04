# Exercise: Commit Message Validator

Good commit messages are one of the most underrated practices in software development. A well-written commit message tells future developers (including yourself) **why** a change was made — not just what the diff shows. Many professional teams enforce commit message rules using Git hooks or CI pipeline checks.

## The conventions

The most widely adopted convention originates from the open-source community and is described in detail in *Pro Git* and Tim Pope's "A Note About Git Commit Messages":

1. **Subject line is 72 characters or fewer** — many Git interfaces (GitHub, terminal, email patches) truncate lines longer than this, hiding important context.
2. **Subject line does not end with a period** — commit subjects are treated like headlines, not sentences.
3. **Subject line starts with a capital letter** — for consistency and professional appearance.

There are additional conventions (imperative mood, blank line before body, body wrapped at 72 chars), but this exercise focuses on the three rules above.

## What you are building

Write a commit message validator that checks each input message against these three rules in order, and reports the first violation found (or `OK` if all rules pass).

## Why this matters

This is literally what many `commit-msg` Git hooks do. Tools like `commitlint`, `conventional-commits`, and `gitlint` implement exactly this logic at a higher sophistication level. Understanding the underlying check makes you a more informed consumer of these tools.

## Input format

One commit message subject per line. Process each line independently. Stop at EOF.

Skip empty lines.

## Output format

For each message, print:
- `OK` if all rules pass
- `ERROR: subject line must be 72 characters or fewer` (if rule 1 fails first)
- `ERROR: subject line must not end with a period` (if rule 2 fails first)
- `ERROR: subject line must start with a capital letter` (if rule 3 fails first)

Rules are checked in order 1, 2, 3. Report only the **first** failing rule.

## Example

Input:
```
Add user authentication module
fix login bug.
add new feature for the dashboard that handles all the user interactions and navigation throughout the entire application
Update README
refactored database connection pooling logic
```

Output:
```
OK
ERROR: subject line must not end with a period
ERROR: subject line must be 72 characters or fewer
OK
ERROR: subject line must start with a capital letter
```

## Further reading

- *Pro Git* — Commit guidelines: https://git-scm.com/book/en/v2/Distributed-Git-Contributing-to-a-Project#_commit_guidelines
- Atlassian — Writing a good commit message: https://www.atlassian.com/git/tutorials/saving-changes/git-commit
