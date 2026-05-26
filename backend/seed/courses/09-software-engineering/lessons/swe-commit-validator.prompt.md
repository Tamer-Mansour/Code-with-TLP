# Commit Message Validator

Read commit messages from standard input (one per line). For each message, print `valid` if it matches the Conventional Commits format, or `invalid` if it does not.

A commit message is **valid** if it starts with one of the allowed type prefixes (`feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`) followed by `": "` (colon + space), then at least one non-space character.

The type must be exactly lowercase. No scope notation is needed.

**Input:** One commit message per line until EOF.

**Output:** One `valid` or `invalid` per line, in the same order.

**Example:**

Input:
```
feat: add login endpoint
Fix: wrong capitalisation
docs: update README
chore:missing space
```

Output:
```
valid
invalid
valid
invalid
```
